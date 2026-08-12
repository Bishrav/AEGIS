FROM python:3.12-slim

WORKDIR /app
COPY services/auth/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY services/auth/aegis_auth ./aegis_auth

ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["sh", "-c", "uvicorn aegis_auth.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
