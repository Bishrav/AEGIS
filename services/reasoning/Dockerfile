FROM python:3.12-slim

WORKDIR /app
COPY services/reasoning/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY algorithms/rag/aegis_rag /app/algorithms/rag/aegis_rag
COPY services/reasoning/aegis_reasoning /app/aegis_reasoning

ENV PYTHONPATH=/app/algorithms/rag:/app
EXPOSE 8000
CMD ["sh", "-c", "uvicorn aegis_reasoning.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
