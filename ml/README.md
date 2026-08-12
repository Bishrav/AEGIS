# Phase 3 ML

Phase 3 starts with reproducible baselines. The first NLP model is TF-IDF plus Logistic Regression for flood-related report classification. The dataset is intentionally small and versioned for portfolio development; its metrics are engineering evidence, not a claim of production-grade language understanding.

Run the baseline:

```powershell
$env:PYTHONPATH = "ml/nlp"
python ml/nlp/train_baseline.py
```

The initial held-out baseline result is accuracy `0.75`, macro precision `0.625`, macro recall `0.75`, and macro F1 `0.667` on four evaluation examples. The dataset is intentionally small at this stage; Phase 3 will expand it before comparing against a transformer model.

Run tests:

```powershell
$env:PYTHONPATH = "ml/nlp"
python -m unittest discover -s ml/nlp/tests -v
```
