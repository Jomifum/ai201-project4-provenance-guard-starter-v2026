"""
What your test runs. ← UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it. Criterion 1 is left
for your own writing; until you add those ten texts, the evaluator skips only
that scenario and runs the other four.
"""

import json
from pathlib import Path


_TEXTS_PATH = Path(__file__).parent / "test_set" / "texts.json"
_FIXTURES = json.loads(_TEXTS_PATH.read_text(encoding="utf-8"))
_TEXT_BY_ID = {item["id"]: item["text"] for item in _FIXTURES}


def _texts_for(ids: list[str]) -> list[str]:
    missing = [fixture_id for fixture_id in ids if fixture_id not in _TEXT_BY_ID]
    if missing:
        raise ValueError(f"Missing text fixture IDs: {', '.join(missing)}")
    return [_TEXT_BY_ID[fixture_id] for fixture_id in ids]


_AI_IDS = [f"ai_{i:02}" for i in range(1, 6)]
_HUMAN_IDS = [
    "human_01", "human_02", "human_03", "human_04", "human_05_formal",
]
_BORDERLINE_IDS = [f"borderline_{i:02}" for i in range(1, 6)]
_ALL_IDS = _AI_IDS + _HUMAN_IDS + _BORDERLINE_IDS

SCENARIOS = [
    {
        "name": "my own writing",
        "criterion": 1,
        "needs_user_input": True,
        "required_text_count": 10,
        # Add ten pieces you wrote yourself here. This scenario is skipped
        # until all ten are supplied; no sample text is generated for you.
        "texts": [
            None,  # YOUR OWN WRITING 1 OF 10
            None,  # YOUR OWN WRITING 2 OF 10
            None,  # YOUR OWN WRITING 3 OF 10
            None,  # YOUR OWN WRITING 4 OF 10
            None,  # YOUR OWN WRITING 5 OF 10
            None,  # YOUR OWN WRITING 6 OF 10
            None,  # YOUR OWN WRITING 7 OF 10
            None,  # YOUR OWN WRITING 8 OF 10
            None,  # YOUR OWN WRITING 9 OF 10
            None,  # YOUR OWN WRITING 10 OF 10
        ],
    },
    {
        "name": "score spread",
        "criterion": 2,
        "fixture_ids": _AI_IDS + _HUMAN_IDS,
        "texts": _texts_for(_AI_IDS + _HUMAN_IDS),
    },
    {
        "name": "label coverage",
        "criterion": 3,
        "fixture_ids": _ALL_IDS,
        "texts": _texts_for(_ALL_IDS),
        "include_label_ranges": True,
    },
    {
        "name": "borderline text",
        "criterion": 4,
        "fixture_ids": _BORDERLINE_IDS,
        "texts": _texts_for(_BORDERLINE_IDS),
    },
    {
        "name": "appeals and bad input",
        "criterion": 5,
        "fixture_ids": _AI_IDS + _HUMAN_IDS,
        "texts": _texts_for(_AI_IDS + _HUMAN_IDS),
        "appeal_after_submit": True,
        "unknown_appeal": {
            "content_id": "unknown-criteria-id",
            "reasoning": "I wrote this text myself.",
        },
        "bad_bodies": [
            {"creator_id": "eval_missing_text"},
            {"text": "", "creator_id": "eval_empty_text"},
            {"text": "x" * 10_001, "creator_id": "eval_overlength_text"},
        ],
    },
]


def validate() -> list[str]:
    """
    Complain about malformed scenarios before a long run.

    The criterion 1 placeholder is valid only as an explicitly skipped
    scenario; it becomes runnable after ten own-written texts are supplied.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if scenario.get("needs_user_input"):
            continue

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not isinstance(text, str) or not text.strip():
                problems.append(
                    f"scenario {i}, text {j} is empty"
                )
    return problems
