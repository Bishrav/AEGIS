FROM python:3.12-slim

WORKDIR /app
COPY services/evidence/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY algorithms/rag/aegis_rag /app/algorithms/rag/aegis_rag
COPY services/evidence/aegis_evidence_service /app/aegis_evidence_service

ENV PYTHONPATH=/app/algorithms/rag:/app
EXPOSE 8000
CMD ["sh", "-c", "uvicorn aegis_evidence_service.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
