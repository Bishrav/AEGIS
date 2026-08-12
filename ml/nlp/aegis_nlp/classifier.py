from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


@dataclass(frozen=True)
class ClassificationResult:
    label: str
    confidence: float


class FloodTextClassifier:
    """TF-IDF + Logistic Regression baseline for flood-related report text."""

    def __init__(self) -> None:
        self.pipeline = Pipeline(
            [
                ("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=1)),
                ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
            ]
        )
        self.labels: tuple[str, ...] = ()

    def fit(self, texts: Iterable[str], labels: Iterable[str]) -> None:
        labels_list = list(labels)
        self.pipeline.fit(list(texts), labels_list)
        self.labels = tuple(self.pipeline.classes_)

    def predict(self, text: str) -> ClassificationResult:
        probabilities = self.pipeline.predict_proba([text])[0]
        index = int(probabilities.argmax())
        return ClassificationResult(self.labels[index], float(probabilities[index]))

    def predict_many(self, texts: Iterable[str]) -> list[ClassificationResult]:
        return [self.predict(text) for text in texts]

