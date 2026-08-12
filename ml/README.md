# Phase 3 ML

Phase 3 implements measured baselines before advanced models:

- NLP: TF-IDF + Logistic Regression.
- NER: gazetteer and deterministic rule extraction.
- Anomaly detection: z-score plus Isolation Forest ensemble.
- Forecasting: naive and seasonal baseline comparison.

The starter NLP dataset is intentionally small. Its current held-out result is accuracy `0.75`, macro precision `0.625`, macro recall `0.75`, and macro F1 `0.667`; these metrics are reported honestly rather than presented as production performance.

