"""Signal three: repeated adjacent two-word phrase rate in normalized text."""

from collections import Counter

import config
import stylometry


def repetition_signal(text: str) -> float:
    """Return a normalized repeated-bigram rate on a 0–1 scale."""
    tokens = stylometry.words(text)
    if len(tokens) < 2:
        return 0.0

    bigrams = [tuple(tokens[index:index + 2]) for index in range(len(tokens) - 1)]
    counts = Counter(bigrams)
    repeated_occurrences = sum(count - 1 for count in counts.values() if count > 1)
    repeat_rate = repeated_occurrences / len(bigrams)
    return round(min(repeat_rate / config.REPETITION_RATE_FOR_MAX, 1.0), 4)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:])
    if not text:
        raise SystemExit('Usage: python repetition.py "some text"')
    print(f"repetition_signal {repetition_signal(text):.4f}")
