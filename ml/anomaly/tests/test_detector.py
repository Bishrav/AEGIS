import unittest

from aegis_anomaly.detector import AnomalyDetector


class AnomalyTests(unittest.TestCase):
    def test_spike_receives_high_anomaly_score(self):
        results = AnomalyDetector().fit_predict([10, 11, 9, 10, 12, 11, 100])
        self.assertTrue(results[-1].is_anomaly)
        self.assertGreater(results[-1].anomaly_probability, 0.5)

