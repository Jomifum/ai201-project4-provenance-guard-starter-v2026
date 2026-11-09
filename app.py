#!/usr/bin/env python3
"""
Provenance Guard — the web service.

    python app.py

Then, in another terminal:

    curl -X POST http://127.0.0.1:5000/ping \
      -H "Content-Type: application/json" \
      -d '{"message": "hello"}'

That's the example route. It works right now, before you've written anything.
**Leave it alone** — it's your control. When something breaks later, check that
`/ping` still answers: if it does, the problem is in your handler; if it
doesn't, it's the service itself.

Routes:

    POST /ping        the worked example. Already works. Don't edit it
    POST /submit      score submitted text
    POST /appeal      record an appeal
    GET  /content/<id> read one decision and its current status
    POST /verify      complete a prompted-writing credential step
    GET  /log         the audit log. Already works
    GET  /health      is the service up, and is the model loaded
"""

import uuid

from flask import Flask, jsonify, request

import audit
import config

app = Flask(__name__)


def _log_route_rejection(payload, reason: str, **extra) -> None:
    creator_id = payload.get("creator_id") if isinstance(payload, dict) else None
    if not isinstance(creator_id, str) or not creator_id.strip():
        creator_id = "unknown"
    else:
        creator_id = creator_id.strip()
    audit.log_rejection(creator_id=creator_id, reason=reason, **extra)


# ── Rate limiting — UNIT 8 ────────────────────────────────────────────────────
# Enabled for unit 8. The limits are configured in config.py and applied to
# /submit below.
#
# The storage backend is preconfigured, which stops Flask-Limiter printing a
# warning on every start. In-memory is right for one laptop and wrong for
# anything real — a restart forgets every count.

class _LimiterOff:
    """
    Stands in for the real limiter while rate limiting is off.

    It makes @limiter.limit(...) a decorator that returns the route
    untouched, so uncommenting the line before you flip the setting is
    harmless instead of a crash on startup.
    """

    def limit(self, *args, **kwargs):
        return lambda view: view


limiter = _LimiterOff()
if config.RATE_LIMITING_ENABLED:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    def rate_limit_key():
        """
        Who a request counts against.

        Falling back to the caller's address is the easy version. Unit 8's
        stretch asks about per-creator limits instead — and the difference
        matters: one script can look like a thousand callers, and one household
        can look like one.
        """
        payload = request.get_json(silent=True)
        # A body that parses as JSON but isn't an object — a bare list or
        # string — has no .get. Without this guard the key function raises
        # BEFORE the route runs, and a malformed request becomes a 500 that
        # looks like your handler crashed when your handler never ran.
        if not isinstance(payload, dict):
            return get_remote_address()
        creator = payload.get("creator_id")
        return creator if isinstance(creator, str) and creator.strip() else get_remote_address()

    limiter = Limiter(
        key_func=rate_limit_key,
        app=app,
        storage_uri=config.RATE_LIMIT_STORAGE,
        default_limits=[],
    )

    @app.errorhandler(429)
    def rate_limited(exc):
        """
        A rejected request still leaves a trace.

        ⚠️ An attack that shows up only as an absence is one you'll never find.
        """
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            payload = {}
        _log_route_rejection(
            payload, "rate_limited", limit=str(exc.description)
        )
        return jsonify({
            "error": "rate_limited",
            "message": "Too many submissions. Try again shortly.",
            "limit": str(exc.description),
        }), 429


# ── The worked example. Already works. Don't edit. ────────────────────────────

@app.post("/ping")
def ping():
    """
    Everything a route needs, in six lines.

    JSON arrives as a dict. You pull things out of it. You return a dict and
    the framework turns it into a response. That's the whole idea.
    """
    payload = request.get_json(silent=True) or {}
    return jsonify({
        "ok": True,
        "you_sent": payload.get("message"),
        "service": "provenance-guard",
    })


@app.get("/health")
def health():
    """Is the service up, and has the model been downloaded yet?"""
    import detector

    loaded = detector._model is not None
    return jsonify({
        "ok": True,
        "detector_model": config.DETECTOR_MODEL,
        "detector_loaded": loaded,
        "rate_limiting": config.RATE_LIMITING_ENABLED,
        "log_entries": len(audit.read_entries()),
    })


# ── YOU BUILD THIS ────────────────────────────────────────────────────────────

@app.post("/submit")
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute;{config.RATE_LIMIT_PER_DAY}/day")
def submit():
    """
    Score a text with all signals, log the decision, and return the result.

    Expects JSON:
        {"text": "...", "creator_id": "..."}

    Returns the component signal scores, their combined score as `confidence`,
    and the label. Malformed input and unavailable detector errors return
    JSON errors rather than an unhandled exception.
    """
    import detector
    import repetition
    import scoring
    import stylometry
    import verification

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        _log_route_rejection(payload, "invalid_request_body")
        return jsonify({
            "error": "invalid_request",
            "message": "Request body must be a JSON object.",
        }), 400

    text = payload.get("text")
    creator_id = payload.get("creator_id")
    if not isinstance(text, str) or not text.strip():
        _log_route_rejection(payload, "missing_or_empty_text")
        return jsonify({
            "error": "invalid_request",
            "message": "'text' must be a non-empty string.",
        }), 400
    if not isinstance(creator_id, str) or not creator_id.strip():
        _log_route_rejection(payload, "missing_or_empty_creator_id")
        return jsonify({
            "error": "invalid_request",
            "message": "'creator_id' must be a non-empty string.",
        }), 400
    if len(text) > 10_000:
        _log_route_rejection(payload, "text_too_long")
        return jsonify({
            "error": "invalid_request",
            "message": "'text' must not exceed 10,000 characters.",
        }), 400

    try:
        model_score = detector.model_signal(text)
    except ValueError as exc:
        _log_route_rejection(payload, "invalid_text")
        return jsonify({
            "error": "invalid_request",
            "message": str(exc),
        }), 400
    except detector.DetectorUnavailable as exc:
        _log_route_rejection(payload, "detector_unavailable")
        return jsonify({
            "error": "detector_unavailable",
            "message": str(exc),
        }), 503

    style_score = stylometry.style_signal(text)
    repetition_score = repetition.repetition_signal(text)
    combined_score = scoring.combine_signals(
        model_score, style_score, repetition_score
    )
    guess, label = scoring.score_to_label(combined_score)
    content_id = str(uuid.uuid4())
    verified_human = verification.is_verified(creator_id.strip())
    audit.log_decision(
        content_id=content_id,
        creator_id=creator_id.strip(),
        guess=guess,
        model_score=model_score,
        style_score=style_score,
        repetition_score=repetition_score,
        combined_score=combined_score,
        label=label,
        status="decided",
        verified_human=verified_human,
    )

    return jsonify({
        "content_id": content_id,
        "guess": guess,
        "model_score": model_score,
        "style_score": style_score,
        "repetition_score": repetition_score,
        "combined_score": combined_score,
        "confidence": combined_score,
        "label": label,
        "verified_human": verified_human,
    })


@app.post("/appeal")
def appeal():
    """
    Record a writer's appeal against an existing decision.

    Expects JSON:
        {"content_id": "...", "reasoning": "..."}
    """
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        _log_route_rejection(payload, "invalid_request_body")
        return jsonify({
            "error": "invalid_request",
            "message": "Request body must be a JSON object.",
        }), 400

    content_id = payload.get("content_id")
    reasoning = payload.get("reasoning")
    if not isinstance(reasoning, str) or not reasoning.strip():
        _log_route_rejection(payload, "missing_or_empty_reasoning")
        return jsonify({
            "error": "invalid_request",
            "message": "'reasoning' must be a non-empty string.",
        }), 400
    if not isinstance(content_id, str) or not content_id.strip():
        _log_route_rejection(payload, "missing_content_id")
        return jsonify({
            "error": "not_found",
            "message": "No submission exists for that content_id.",
        }), 404

    decisions = [
        entry
        for entry in audit.entries_for(content_id)
        if entry.get("event") != "appeal"
        and entry.get("status") == "decided"
        and isinstance(entry.get("creator_id"), str)
    ]
    if not decisions:
        _log_route_rejection(
            payload,
            "content_not_found",
            content_id=content_id.strip(),
        )
        return jsonify({
            "error": "not_found",
            "message": "No submission exists for that content_id.",
        }), 404

    audit.log_appeal(content_id, decisions[0]["creator_id"], reasoning.strip())
    return jsonify({
        "content_id": content_id,
        "status": "under_review",
        "message": "Your appeal has been recorded for review.",
    })


@app.get("/content/<content_id>")
def get_content(content_id: str):
    """Return one logged decision with the latest appeal status."""
    entries = audit.entries_for(content_id)
    decisions = [
        entry for entry in entries
        if entry.get("event") != "appeal"
        and entry.get("status") == "decided"
        and isinstance(entry.get("creator_id"), str)
    ]
    if not decisions:
        _log_route_rejection(
            None,
            "content_not_found",
            content_id=content_id,
        )
        return jsonify({
            "error": "not_found",
            "message": "No submission exists for that content_id.",
        }), 404

    decision = decisions[0]
    status = (
        "under_review"
        if any(entry.get("event") == "appeal" for entry in entries)
        else decision["status"]
    )
    return jsonify({
        "content_id": content_id,
        "creator_id": decision["creator_id"],
        "guess": decision.get("guess"),
        "label": decision.get("label"),
        "combined_score": decision.get("combined_score"),
        "status": status,
        "verified_human": bool(decision.get("verified_human", False)),
    })


@app.post("/verify")
def verify_creator():
    """
    Grant a prompted-writing completion credential after a 100-word sample.

    This checks completion of the prompt, not identity or human authorship.
    """
    import stylometry
    import verification

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        _log_route_rejection(payload, "invalid_request_body")
        return jsonify({
            "error": "invalid_request",
            "message": "Request body must be a JSON object.",
            "prompt": config.VERIFICATION_PROMPT,
        }), 400

    creator_id = payload.get("creator_id")
    writing_sample = payload.get("writing_sample")
    if not isinstance(creator_id, str) or not creator_id.strip():
        _log_route_rejection(payload, "missing_or_empty_creator_id")
        return jsonify({
            "error": "invalid_request",
            "message": "'creator_id' must be a non-empty string.",
            "prompt": config.VERIFICATION_PROMPT,
        }), 400
    if not isinstance(writing_sample, str) or not writing_sample.strip():
        _log_route_rejection(payload, "missing_or_empty_writing_sample")
        return jsonify({
            "error": "invalid_request",
            "message": "'writing_sample' must be a non-empty string.",
            "prompt": config.VERIFICATION_PROMPT,
        }), 400
    if len(writing_sample) > 10_000:
        _log_route_rejection(payload, "writing_sample_too_long")
        return jsonify({
            "error": "invalid_request",
            "message": "'writing_sample' must not exceed 10,000 characters.",
            "prompt": config.VERIFICATION_PROMPT,
        }), 400

    word_count = len(stylometry.words(writing_sample))
    if word_count < 100:
        _log_route_rejection(payload, "writing_sample_too_short")
        return jsonify({
            "error": "invalid_request",
            "message": "The prompted writing sample must contain at least 100 words.",
            "word_count": word_count,
            "prompt": config.VERIFICATION_PROMPT,
        }), 400

    verified_at = verification.add_verified_creator(creator_id.strip())
    return jsonify({
        "creator_id": creator_id.strip(),
        "verified_human": True,
        "credential": "prompted_sample_completed",
        "verified_at": verified_at,
        "word_count": word_count,
        "message": (
            "The prompted writing sample was received. This credential confirms "
            "completion only; it does not verify identity or authorship."
        ),
    })


# ── Already works ─────────────────────────────────────────────────────────────

@app.get("/log")
def get_log():
    """
    The audit log, most recent last.

        curl "http://127.0.0.1:5000/log?limit=10"

    You need this in unit 8 to paste entries into your README, and you need it
    now to see whether your logging is actually working.
    """
    limit = request.args.get("limit", type=int)
    entries = audit.read_entries(limit=limit)
    return jsonify({"count": len(entries), "entries": entries})


def main():
    print(f"Provenance Guard on http://{config.HOST}:{config.PORT}")
    print(f"  detector model:  {config.DETECTOR_MODEL}")
    print(f"  rate limiting:   {'ON' if config.RATE_LIMITING_ENABLED else 'off (unit 8)'}")
    print(f"  audit log:       {config.AUDIT_LOG}")
    print()
    print("Check it's alive:")
    print(f'  curl -X POST http://{config.HOST}:{config.PORT}/ping \\')
    print('    -H "Content-Type: application/json" \\')
    print("    -d '{\"message\": \"hello\"}'")
    print()
    # debug=True hands out an interactive debugger, so it's local-only — see config.py
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)


if __name__ == "__main__":
    main()
