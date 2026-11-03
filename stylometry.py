"""Signal two: surface-form measurements combined into an AI-likelihood score.

This signal does not understand meaning or establish authorship. Surface edits
such as typos, sentence splitting, or quotations can change its measurements.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation appears per word?

    python stylometry.py "some text to look at"
"""

import re
import statistics

AI_SPREAD_CV = 0.15
HUMAN_SPREAD_CV = 0.55


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


def sentence_length_spread(text: str) -> float:
    """Return the coefficient of variation for sentence word counts."""
    lengths = []
    for sentence in sentences(text):
        length = len(words(sentence))
        if length:
            lengths.append(length)
    if len(lengths) < 2:
        return 0.0
    mean_length = statistics.mean(lengths)
    if mean_length == 0:
        return 0.0
    return statistics.stdev(lengths) / mean_length


def type_token_ratio(text: str) -> float:
    """Return unique normalized words divided by the total normalized words."""
    tokens = words(text)
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)


def punctuation_density(text: str) -> float:
    """Return punctuation marks per normalized word."""
    word_count = len(words(text))
    if word_count == 0:
        return 0.0
    punctuation_count = len(re.findall(r"[^\w\s]", text))
    return punctuation_count / word_count


def style_signal(text: str) -> float:
    """
    Return a 0–1 score, with higher values indicating more AI-like tendencies.
    Low sentence-length variation is the primary AI-like feature. Vocabulary
    diversity and punctuation have small weights because their directions were
    weak or inconsistent in the current calibration sample.
    """
    if not words(text):
        return 0.5

    spread = sentence_length_spread(text)
    vocabulary_variety = type_token_ratio(text)
    punctuation = punctuation_density(text)

    spread_ai = min(
        max((HUMAN_SPREAD_CV - spread) / (HUMAN_SPREAD_CV - AI_SPREAD_CV), 0.0),
        1.0,
    )
    vocabulary_ai = min(max((vocabulary_variety - 0.60) / 0.25, 0.0), 1.0)
    punctuation_ai = 1.0 - min(punctuation / 0.30, 1.0)

    score = 0.90 * spread_ai + 0.05 * vocabulary_ai + 0.05 * punctuation_ai
    return round(min(max(score, 0.0), 1.0), 4)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")
