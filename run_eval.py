#!/usr/bin/env python3
"""
Run your five criteria three times each.  <- UNIT 8, MILESTONE 3

    python app.py                              # in one terminal
    python run_eval.py --label before          # in another
    python run_eval.py --label after

The attack set tests what staff thought to test. This tests what *you* thought
to test, and the two rarely overlap much. Both count.

Fill in `scenarios.py` first — that's where you say what each criterion needs
run against it. A criterion about false positives needs your own writing. One
about label coverage needs inputs across the score range.

!! Three trials, and **your first signal runs a model, so identical input can
score differently twice.** That's exactly why repeats matter here.

This does the sending and the recording. It does not decide whether a trial
passed — that depends on the criterion you wrote, so the Verdict column comes
back blank.
"""

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import config

# Windows consoles often run a codepage that can't print every character in
# this file's help text. Without this, `--help` ends in a UnicodeEncodeError
# traceback instead of the help — which is a miserable first thing to hit.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(errors="replace")
    except (AttributeError, ValueError):  # not a normal text stream
        pass


DEFAULT_URL = f"http://{config.HOST}:{config.PORT}"


def bodies_for(scenario, trial_number: int):
    """
    The request bodies one scenario sends.

    Every text submission gets its own creator_id for each trial, keeping it
    below the per-creator limiter while preserving repeated trials.
    """
    if scenario.get("bodies"):
        return list(scenario["bodies"])
    return [
        {
            "text": text,
            "creator_id": (
                f"eval_c{scenario['criterion']}_t{trial_number}_{i}"
            ),
        }
        for i, text in enumerate(scenario["texts"], 1)
    ]


def describe(body):
    """A short, readable note of what was sent — for the report."""
    if set(body) == {"text", "creator_id"} and isinstance(body.get("text"), str):
        text = body["text"]
        return text[:70] if text else "(empty text)"
    return json.dumps(body)[:120]


def request_json(requests, method, url, timeout, body=None):
    """Make one JSON request and preserve an HTTP status even if JSON parsing fails."""
    try:
        response = requests.request(
            method,
            url,
            json=body,
            timeout=timeout,
        )
    except Exception as exc:  # noqa: BLE001
        return {
            "status": None,
            "payload": {},
            "error": f"{type(exc).__name__}: {exc}",
        }

    try:
        payload = response.json() if response.content else {}
    except ValueError as exc:
        return {
            "status": response.status_code,
            "payload": {},
            "error": f"{type(exc).__name__}: {exc}",
            "response_text": response.text[:200],
        }

    return {
        "status": response.status_code,
        "payload": payload if isinstance(payload, dict) else {},
        "error": None,
    }


def result_for(response, body, kind, fixture_id=None):
    payload = response["payload"]
    result = {
        "kind": kind,
        "fixture_id": fixture_id,
        "status": response["status"],
        "guess": payload.get("guess"),
        "confidence": payload.get("confidence"),
        "model_score": payload.get("model_score"),
        "style_score": payload.get("style_score"),
        "label": payload.get("label"),
        "sent": describe(body),
    }
    if response["error"]:
        result["error"] = response["error"]
        if response.get("response_text"):
            result["response_text"] = response["response_text"]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--label", default="")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--timeout", type=float, default=90.0)
    args = parser.parse_args()

    try:
        import requests
    except ImportError:
        print("The `requests` package isn't installed.\n"
              "Run: pip install -r requirements.txt", file=sys.stderr)
        sys.exit(1)

    try:
        import scenarios
    except ImportError:
        print("No scenarios.py found. Milestone 3 starts by filling it in.",
              file=sys.stderr)
        sys.exit(1)

    problems = scenarios.validate()
    if problems:
        print("scenarios.py has problems:\n", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        sys.exit(1)

    try:
        requests.get(f"{args.url}/health", timeout=5)
    except Exception:  # noqa: BLE001
        print(f"Nothing answering at {args.url}. Start it:  python app.py",
              file=sys.stderr)
        sys.exit(1)

    if args.trials < 3:
        print(f"!! {args.trials} trial(s). The submission asks for three.\n")

    rows = []
    for scenario in scenarios.SCENARIOS:
        print(f"\n{scenario['name']}  (criterion {scenario.get('criterion') or '—'})")

        if (
            scenario.get("needs_user_input")
            and (
                len(scenario.get("texts", []))
                != scenario.get("required_text_count", 0)
                or any(
                    not isinstance(text, str) or not text.strip()
                    for text in scenario.get("texts", [])
                )
            )
        ):
            print(
                f"  not run: add {scenario['required_text_count']} "
                "pieces of your own writing"
            )
            rows.append({"scenario": scenario, "trials": []})
            continue

        trials = []
        for trial in range(1, args.trials + 1):
            results = []
            fixture_ids = scenario.get("fixture_ids", [])
            for i, body in enumerate(bodies_for(scenario, trial), 1):
                preview = describe(body)
                response = request_json(
                    requests, "POST", f"{args.url}/submit", args.timeout, body
                )
                result = result_for(
                    response,
                    body,
                    "submission",
                    fixture_ids[i - 1] if i <= len(fixture_ids) else None,
                )

                if (
                    scenario.get("appeal_after_submit")
                    and response["status"] == 200
                    and response["payload"].get("content_id")
                ):
                    content_id = response["payload"]["content_id"]
                    appeal_body = {
                        "content_id": content_id,
                        "reasoning": "I wrote this text myself.",
                    }
                    appeal = request_json(
                        requests,
                        "POST",
                        f"{args.url}/appeal",
                        args.timeout,
                        appeal_body,
                    )
                    current = request_json(
                        requests,
                        "GET",
                        f"{args.url}/content/{content_id}",
                        args.timeout,
                    )
                    result["appeal"] = {
                        "status": appeal["status"],
                        "body": appeal["payload"],
                        "error": appeal["error"],
                    }
                    result["current_status"] = current["payload"].get("status")

                results.append(result)

            for i, body in enumerate(scenario.get("bad_bodies", []), 1):
                response = request_json(
                    requests, "POST", f"{args.url}/submit", args.timeout, body
                )
                results.append(result_for(response, body, "bad_input"))

            if scenario.get("unknown_appeal"):
                before = request_json(
                    requests, "GET", f"{args.url}/log", args.timeout
                )
                appeal_body = scenario["unknown_appeal"]
                appeal = request_json(
                    requests,
                    "POST",
                    f"{args.url}/appeal",
                    args.timeout,
                    appeal_body,
                )
                after = request_json(
                    requests, "GET", f"{args.url}/log", args.timeout
                )
                results.append({
                    "kind": "unknown_appeal",
                    "status": appeal["status"],
                    "body": appeal["payload"],
                    "error": appeal["error"],
                    "audit_count_before": before["payload"].get("count"),
                    "audit_count_after": after["payload"].get("count"),
                })

            if scenario.get("include_label_ranges"):
                import scoring

                results.append({
                    "kind": "label_ranges",
                    "ranges": scoring.label_ranges(),
                })

            trials.append(results)
            guesses = [
                r.get("guess") or "—"
                for r in results
                if r.get("kind") == "submission"
            ]
            print(f"  trial {trial}: {', '.join(guesses)}")

        rows.append({"scenario": scenario, "trials": trials})

    write_report(rows, args)


def write_report(rows, args):
    config.RESULTS_DIR.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    label = f"_{args.label}" if args.label else ""
    path = config.RESULTS_DIR / f"run_{stamp}{label}.md"

    n = args.trials
    headers = " | ".join(f"Run {i}" for i in range(1, n + 1))
    divider = "|".join(["---"] * n)

    lines = [
        f"# Run log{f' — {args.label}' if args.label else ''}",
        "",
        "- Produced by: `run_eval.py::main`",
        "- Service: `app.py::submit` · scoring: `scoring.py::combine_signals`",
        f"- {n} trials per criterion · {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "Fill in Target from `criteria.md`, and Run and Verdict from the output",
        "underneath. Whether a trial passed depends on the criterion you wrote.",
        "",
        f"| Criterion | Target | {headers} | Verdict |",
        f"|---|---|{divider}|---|",
    ]

    for row in rows:
        scenario = row["scenario"]
        number = scenario.get("criterion")
        name = f"{number}. {scenario['name']}" if number else scenario["name"]
        lines.append(f"| {name} |  | {' | '.join([' '] * n)} |  |")

    lines += ["", "---", "", "## What actually came back", "",
              "Real output. Paste the relevant parts into your README — the rubric",
              "asks for the actual JSON, not a description of it.", ""]

    for row in rows:
        scenario = row["scenario"]
        lines += [f"### {scenario['name']}", ""]
        if not row["trials"]:
            lines += [
                f"Not run: add {scenario['required_text_count']} pieces of your "
                "own writing to `scenarios.py`.",
                "",
            ]
        for trial_number, results in enumerate(row["trials"], 1):
            lines += [f"**Trial {trial_number}**", "", "```json",
                      json.dumps(results, indent=2), "```", ""]

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {path.relative_to(config.ROOT)}")
    print("Commit it. It's the evidence the test actually happened.")


if __name__ == "__main__":
    main()
