"""
Settings for Provenance Guard.

Everything you're likely to change lives here, at the top, on purpose.

You'll edit the thresholds in Milestone 5 and the rate limits in unit 8.
"""

import os
from pathlib import Path

ROOT = Path(__file__).parent


# ─── The service ─────────────────────────────────────────────────────────────

# `127.0.0.1` is loopback — only your own machine can reach it, which is what
# you want all through units 7 and 8. A host somewhere else has to accept
# traffic from outside the box, and that means `0.0.0.0`. Setting the env var
# is how you get it; the default keeps your local `curl` commands unchanged.
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "5000"))

# Flask's debug mode gives anyone who can reach the service an interactive
# Python prompt inside your process. Fine on loopback, a gift to strangers
# anywhere else — so it turns itself off the moment HOST isn't loopback.
DEBUG = os.getenv("AI201_DEBUG", "1") == "1" and HOST in ("127.0.0.1", "localhost")


# ─── The local model ─────────────────────────────────────────────────────────
# Your first signal runs a language model ON YOUR OWN MACHINE. No account, no
# key, no card. It downloads about 550 MB the first time — do that before
# class, not during it.
#
# What it measures: how *predictable* your text is to a language model. Text a
# model finds easy to predict tends to be text a model wrote.
#
# The first call is the slow one — ten to twenty seconds while the model loads,
# longer on an older laptop. After that it stays in memory and a submission
# takes a second or two. That cost is part of what you're learning: this is
# what running a model inline in a request actually looks like.

DETECTOR_MODEL = os.getenv("AI201_DETECTOR_MODEL", "gpt2")

# Longer text gives a steadier reading but takes longer. 400 tokens is roughly
# 300 words, which is enough for the signal to mean something.
DETECTOR_MAX_TOKENS = 400


# ─── Scoring (Milestone 4) ───────────────────────────────────────────────────
# How much each signal counts toward the combined score.
#
# Weights for model predictability, text stylometry, and repeated trigrams.
# Their weighted average is pulled toward 0.5 when the signals disagree.

WEIGHT_MODEL_SIGNAL = 0.20
WEIGHT_STYLE_SIGNAL = 0.60
WEIGHT_REPETITION_SIGNAL = 0.20
REPETITION_RATE_FOR_MAX = 0.05


# ─── Thresholds (Milestone 5) ────────────────────────────────────────────────
# Where one label becomes another. Scores run 0.0 (confidently human) to 1.0
# (confidently AI).
#
#   score <= HUMAN_THRESHOLD         -> high-confidence human
#   between the two                  -> unsure
#   score >= AI_THRESHOLD            -> high-confidence AI
#
# ⚠️ This is where your false-positive decision from Milestone 1 actually gets
# made. Widening the unsure band means fewer wrong accusations and more AI text
# getting through. There is no setting that avoids the trade — only settings
# that decide who pays for it.

HUMAN_THRESHOLD = 0.35
# Keep the AI threshold high and the unsure band wide because false positives
# are more costly than missed AI detections.
AI_THRESHOLD = 0.75

HUMAN_LABEL = "Your writing looks like it was written by a person. Thanks for sharing it."
UNSURE_LABEL = (
    "We can't tell who wrote this text. This result is uncertain, and we are "
    "not accusing you of using AI."
)
AI_LABEL = (
    "This text has features often associated with AI-written text, but this "
    "is not proof of authorship. If this is your original work, you can appeal "
    "by sending its content ID and a brief explanation to POST /appeal."
)
VERIFICATION_PROMPT = (
    "Describe a small task you completed recently. Include what you expected, "
    "one specific detail that changed, and how you responded."
)

# The configured bands are available across the full combined-score range.
# Whether real submissions reach each band depends on the two signal outputs.


# ─── Rate limiting (UNIT 8) ──────────────────────────────────────────────────
# A writer can make a few submissions an hour; these limits allow short bursts
# while slowing a single creator ID that tries to map the thresholds.
#
# Think about two people: a real writer submitting their own work a few times
# an hour, and a script sending a thousand variations to map your thresholds.
# Your README has to say why your numbers and not others.

RATE_LIMITING_ENABLED = True

RATE_LIMIT_PER_MINUTE = 5
RATE_LIMIT_PER_DAY = 50

# Flask-Limiter warns loudly without this. In-memory is right for one laptop
# and wrong for anything real — a restart forgets every count, and two copies
# of the service wouldn't share limits.
RATE_LIMIT_STORAGE = "memory://"


# ─── Paths ───────────────────────────────────────────────────────────────────

LOG_DIR = ROOT / "logs"
AUDIT_LOG = LOG_DIR / "audit.jsonl"
VERIFIED_CREATORS_FILE = LOG_DIR / "verified_creators.json"
RESULTS_DIR = ROOT / "results"
