from __future__ import annotations

import json
from pathlib import Path

from sklearn.model_selection import train_test_split

from aegis_nlp.classifier import FloodTextClassifier
from aegis_nlp.evaluate import evaluate_classifier


ROOT = Path(__file__).parent


def load_dataset() -> tuple[list[str], list[str]]:
    rows = [
        json.loads(line)
        for line in (ROOT / "dataset.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return [row["text"] for row in rows], [row["label"] for row in rows]


def main() -> None:
    texts, labels = load_dataset()
    train_texts, eval_texts, train_labels, eval_labels = train_test_split(
        texts, labels, test_size=0.25, random_state=42, stratify=labels
    )
    model = FloodTextClassifier()
    model.fit(train_texts, train_labels)
    metrics = evaluate_classifier(model, eval_texts, eval_labels)
    print(json.dumps({"model": "tfidf-logistic-regression", "evaluation_size": len(eval_texts), **metrics}, indent=2))


if __name__ == "__main__":
    main()
