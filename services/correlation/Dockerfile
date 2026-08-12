FROM python:3.12-slim

WORKDIR /app
COPY services/correlation/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY services/correlation/aegis_correlation_service ./aegis_correlation_service
COPY algorithms/correlation/aegis_correlation /app/algorithms/correlation/aegis_correlation
COPY algorithms/risk/aegis_risk /app/algorithms/risk/aegis_risk

ENV PYTHONPATH=/app/algorithms/correlation:/app/algorithms/risk:/app
EXPOSE 8000
CMD ["sh", "-c", "uvicorn aegis_correlation_service.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
