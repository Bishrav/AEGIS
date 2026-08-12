from __future__ import annotations

from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from .classifier import FloodTextClassifier


def evaluate_classifier(model: FloodTextClassifier, texts: list[str], labels: list[str]) -> dict[str, float]:
    predictions = [result.label for result in model.predict_many(texts)]
    return {
        "accuracy": float(accuracy_score(labels, predictions)),
        "macro_precision": float(precision_score(labels, predictions, average="macro", zero_division=0)),
        "macro_recall": float(recall_score(labels, predictions, average="macro", zero_division=0)),
        "macro_f1": float(f1_score(labels, predictions, average="macro", zero_division=0)),
    }

