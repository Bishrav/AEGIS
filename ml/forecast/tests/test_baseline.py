import unittest

from aegis_forecast.baseline import compare_baselines


class ForecastTests(unittest.TestCase):
    def test_baseline_comparison_selects_a_model_and_reports_metrics(self):
        values = [float(index % 24) for index in range(48)] + [0.0]
        result = compare_baselines(values, horizon=1, seasonal_period=24)
        self.assertIn(result.selected_model, {"naive", "seasonal"})
        self.assertGreaterEqual(result.naive_rmse, 0)
        self.assertGreaterEqual(result.seasonal_rmse, 0)

