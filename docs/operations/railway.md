# Railway Deployment

AEGIS uses Railway for the deployable ingestion API and Docker Compose for the complete local/integration platform. Railway should expose the ingestion API as a public service while Kafka and S3-compatible storage remain explicit infrastructure dependencies.

## Current deployment boundary

Deploy this service first:

```text
services/ingestion
```

It includes the Dockerfile, Railway config, health endpoint, live Open-Meteo/BIPAD pulls, replay endpoints, Kafka publishing, MinIO/S3-compatible raw storage, and Redis idempotency.

Railway’s monorepo configuration should set the service Root Directory to `/services/ingestion`. The `railway.toml` file is inside that directory so Railway detects it for the isolated service.

## Create the Railway service

From the repository root:

```powershell
railway link
railway service
```

In the Railway dashboard, connect the service to the GitHub repository and set:

- Root Directory: `/services/ingestion`
- Branch: `main`
- Healthcheck Path: `/health` (also defined in `railway.toml`)

Railway will build the service from `services/ingestion/Dockerfile` and inject `PORT`. The container honors that value and binds to `0.0.0.0`.

## Required variables

Set these on the ingestion service. Values containing credentials must be sealed in Railway and never committed.

| Variable | Value |
| --- | --- |
| `KAFKA_BOOTSTRAP_SERVERS` | Private Kafka/Redpanda broker address |
| `S3_ENDPOINT_URL` | Private or public S3-compatible endpoint |
| `S3_ACCESS_KEY` | S3-compatible access key |
| `S3_SECRET_KEY` | S3-compatible secret key |
| `S3_BUCKET` | `aegis-raw` |
| `REDIS_URL` | Railway Redis `REDIS_URL` reference |
| `AEGIS_WEATHER_LATITUDE` | `27.95` |
| `AEGIS_WEATHER_LONGITUDE` | `85.68` |

For a Railway Redis service named `Redis`, use a reference variable rather than copying credentials:

```text
REDIS_URL=${{Redis.REDIS_URL}}
```

## Deploy with the CLI

After linking the project and service:

```powershell
railway up --service ingestion
railway domain --service ingestion
railway logs --service ingestion
```

The generated public URL should respond to:

```text
GET /health
GET /ready
GET /sources/health
```

`/health` only verifies that the process is running. `/ready` verifies Kafka, Redis, and S3-compatible storage connectivity.

## Deployment verification

```powershell
$baseUrl = "https://YOUR-RAILWAY-DOMAIN"
Invoke-WebRequest "$baseUrl/health"
Invoke-WebRequest "$baseUrl/ready"
Invoke-WebRequest -Method Post "$baseUrl/pull/weather"
Invoke-WebRequest "$baseUrl/sources/health"
```

Do not run live pulls repeatedly during verification: each provider has its own rate limits and the ingestion layer intentionally deduplicates records.

## Current limitation

There is no linked Railway project in this checkout yet. The deployment configuration is committed and ready, but the actual public deployment requires selecting the Railway project, adding the Kafka and S3-compatible services, binding variables, and reviewing the first deploy in Railway.

