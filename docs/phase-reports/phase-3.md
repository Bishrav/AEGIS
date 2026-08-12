# Phase 3 Completion Report

## Scope delivered

- Reproducible TF-IDF + Logistic Regression flood-report classifier.
- Hybrid domain NER using gazetteers and deterministic date rules.
- Statistical z-score and Isolation Forest anomaly ensemble.
- Naive and seasonal forecasting comparison.
- Typed inference schemas for NLP, anomaly, and forecast outputs.
- Versioned starter dataset and model tests.
- CI execution for all Phase 3 engines.

## Verification evidence

- NLP tests: 3 passing.
- Anomaly tests: 1 passing.
- Forecast tests: 1 passing.
- NLP starter evaluation: accuracy 0.75, macro precision 0.625, macro recall 0.75, macro F1 0.667.
- Anomaly spike detection verified on synthetic river measurements.
- Forecast baseline selection and MAE/RMSE reporting verified.
- Python 3.12 Docker environment used for reproducible ML verification.

## Model limitations

The NLP dataset is intentionally small and produces a baseline below the eventual macro-F1 target. The next quality improvement is expanding and labeling a held-out public-report corpus before comparing a transformer model. No advanced model is claimed until it is measured against this baseline.

