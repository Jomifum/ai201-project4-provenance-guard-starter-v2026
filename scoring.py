"""
Turning two numbers into one, and one number into something a person can read.
`combine_signals` combines the two likelihood scores, while `score_to_label`
maps the result to a reader-facing label.

⚠️ Your README's **Signals and Scoring** section has to name the file and
function holding your combining rule. The grader checks your code against what
you claim, so that line should read `scoring.py::combine_signals`.
"""

import config


# Combining rule: take the configured weighted average, then pull it toward 0.5
# in proportion to the absolute difference between the two signals.
def combine_signals(model_score: float, style_score: float) -> float:
    """Combine the two 0-1 likelihood scores, pulling disagreement toward 0.5."""
    weight_total = config.WEIGHT_MODEL_SIGNAL + config.WEIGHT_STYLE_SIGNAL
    weighted_average = (
        config.WEIGHT_MODEL_SIGNAL * model_score
        + config.WEIGHT_STYLE_SIGNAL * style_score
    ) / weight_total
    disagreement = abs(model_score - style_score)
    combined = 0.5 + (weighted_average - 0.5) * (1.0 - 0.5 * disagreement)
    return round(min(max(combined, 0.0), 1.0), 4)

def score_to_label(score: float) -> tuple[str, str]:
    """
    Turn a score into a guess and the text a reader actually sees.

    Returns:
        (guess, label_text) — where `guess` is a short machine-readable string
        like "ai" / "human" / "unsure", and `label_text` is the full sentence
        shown to a person.

    ⚠️ Write the label text for someone who has never heard the word
    "threshold".

        ✗ "human, 0.81 confidence"
        ✓ "We think this was probably written by a person."

    The inclusive threshold checks partition every valid score in [0, 1]:
    human scores are at or below HUMAN_THRESHOLD, AI scores are at or above
    AI_THRESHOLD, and the interval between them is unsure.
    """
    if not 0.0 <= score <= 1.0:
        raise ValueError("score must be between 0.0 and 1.0")
    if score >= config.AI_THRESHOLD:
        return "ai", config.AI_LABEL
    if score <= config.HUMAN_THRESHOLD:
        return "human", config.HUMAN_LABEL
    return "unsure", config.UNSURE_LABEL


def label_ranges() -> list[tuple[str, str]]:
    """
    The score range each label covers. Your README needs these beside the
    label text — given to you so the numbers can't drift apart from config.py.
    """
    return [
        ("high-confidence human", f"0.00 – {config.HUMAN_THRESHOLD:.2f}"),
        ("unsure", f"{config.HUMAN_THRESHOLD:.2f} – {config.AI_THRESHOLD:.2f}"),
        ("high-confidence AI", f"{config.AI_THRESHOLD:.2f} – 1.00"),
    ]
