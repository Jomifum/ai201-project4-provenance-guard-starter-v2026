"""Run all configured signals over the 15-text calibration set."""

import json
import statistics
from pathlib import Path

import config
import detector
import repetition
import scoring
import stylometry


TEST_SET = Path(__file__).parent / "test_set" / "texts.json"


def main() -> None:
    items = json.loads(TEST_SET.read_text(encoding="utf-8"))
    if len(items) != 15:
        raise ValueError(f"Expected 15 texts; found {len(items)}.")

    results = []
    print(
        f"{'ID':<20} {'Model':>8} {'Style':>8} "
        f"{'Repeat rate':>12} {'Combined':>9} {'Label':>8}"
    )
    print("-" * 75)
    for item in items:
        text = item["text"]
        word_count = len(stylometry.words(text))
        if word_count < 150:
            raise ValueError(f"{item['id']} has only {word_count} words.")

        model_score = detector.model_signal(text)
        style_score = stylometry.style_signal(text)
        repetition_score = repetition.repetition_signal(text)
        combined_score = scoring.combine_signals(
            model_score, style_score, repetition_score
        )
        guess, _ = scoring.score_to_label(combined_score)
        results.append({
            "id": item["id"],
            "group": item["group"],
            "model": model_score,
            "style": style_score,
            "repetition": repetition_score,
            "combined": combined_score,
            "guess": guess,
        })
        print(
            f"{item['id']:<20} {model_score:>8.4f} {style_score:>8.4f} "
            f"{repetition_score:>16.4f} {combined_score:>9.4f} {guess:>8}"
        )

    print("\nGroup mean combined scores:")
    for group in ("ai", "human", "borderline"):
        scores = [row["combined"] for row in results if row["group"] == group]
        print(f"  {group:<10} {statistics.mean(scores):.4f}")
    gap = (
        statistics.mean(row["combined"] for row in results if row["group"] == "ai")
        - statistics.mean(row["combined"] for row in results if row["group"] == "human")
    )
    print(f"  AI-human gap: {gap:.4f}")
    labels = {
        label: sum(row["guess"] == label for row in results)
        for label in ("ai", "human", "unsure")
    }
    print("Labels: " + ", ".join(f"{label}={count}" for label, count in labels.items()))
    human_false_positives = sum(
        row["group"] == "human" and row["guess"] == "ai" for row in results
    )
    print(f"Human texts labeled ai: {human_false_positives} of 5")
    print(
        "Weights: "
        f"model={config.WEIGHT_MODEL_SIGNAL:.2f}, "
        f"style={config.WEIGHT_STYLE_SIGNAL:.2f}, "
        f"repetition={config.WEIGHT_REPETITION_SIGNAL:.2f}"
    )


if __name__ == "__main__":
    main()
