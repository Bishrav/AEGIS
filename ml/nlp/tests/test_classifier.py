import unittest

from aegis_nlp.classifier import FloodTextClassifier
from aegis_nlp.evaluate import evaluate_classifier


class ClassifierTests(unittest.TestCase):
    def setUp(self):
        self.texts = [
            "river overflow flooded homes",
            "heavy rainfall measured overnight",
            "highway closed by landslide",
            "routine office announcement",
        ] * 3
        self.labels = ["FLOOD", "HEAVY_RAIN", "ROAD_CLOSURE", "NORMAL"] * 3
        self.model = FloodTextClassifier()
        self.model.fit(self.texts, self.labels)

    def test_predicts_flood_label(self):
        result = self.model.predict("flood water overflowed the river bank")
        self.assertEqual(result.label, "FLOOD")
        self.assertGreaterEqual(result.confidence, 0.25)

    def test_evaluation_returns_required_metrics(self):
        metrics = evaluate_classifier(self.model, self.texts, self.labels)
        self.assertEqual(set(metrics), {"accuracy", "macro_precision", "macro_recall", "macro_f1"})
        self.assertGreaterEqual(metrics["macro_f1"], 0)
        self.assertLessEqual(metrics["macro_f1"], 1)

