# Render Deployment

AEGIS is Render-compatible, but its current gateway depends on private correlation and evidence services. The production topology must therefore deploy the gateway together with those private services, plus PostgreSQL and Redis-compatible Key Value. The frontend may be deployed to Vercel or Render as a separate web service.

The repository includes [`render.yaml`](../../render.yaml) as the deployment contract. It uses Render Key Value and expects the Supabase/Postgres connection strings and final browser origins to be entered as protected dashboard values.

For a zero-cost portfolio demo, use [`render.free.yaml`](../../render.free.yaml). It keeps the production Blueprint unchanged but runs correlation and evidence as Free Web Services with public HTTPS URLs. The API-to-service `X-AEGIS-Service-Token` protects those internal endpoints. Enter the same strong token in all three services when Render prompts for the `AEGIS_SERVICE_TOKEN` variables.

## Recommended first production slice

| Service | Render type | Required configuration |
| --- | --- | --- |
| `aegis-api` | Web service | `services/api/Dockerfile`, `CORRELATION_URL`, `EVIDENCE_URL`, `REDIS_URL`, `AEGIS_JWT_SECRET`, `ALLOWED_ORIGINS`, `COOKIE_SAMESITE=none` |
| `aegis-correlation` | Private service | `services/correlation/Dockerfile`, `POSTGRES_DSN` |
| `aegis-evidence` | Private service | `services/evidence/Dockerfile`, `EVIDENCE_POSTGRES_DSN` |
| `aegis-postgres` | Render Postgres | Used by correlation and evidence persistence |
| `aegis-redis` | Render Key Value | Used for SSE publication and idempotency |
| `aegis-frontend` | Vercel or Web service | `NEXT_PUBLIC_API_URL=https://<api-domain>` |

Render private services are not available on the Free plan. Do not expose correlation or evidence as public services just to avoid that restriction; use a paid private service plan or deploy the modular backend as a single production service later.

The Blueprint intentionally uses `starter` for the two private services because Render does not offer Free plans for private services. Review the resulting monthly cost in Render before creating the Blueprint.

## Free portfolio deployment

The free profile is suitable for a recruiter demo, not guaranteed production uptime. Free Web Services sleep after inactivity, have limited monthly hours, and may take about a minute to wake. Use Supabase for durable PostgreSQL storage; do not use Render's Free Postgres for the long-term AEGIS database because it expires after 30 days.

Set these values in the Render dashboard for `render.free.yaml`:

```env
AEGIS_SERVICE_TOKEN=<same-random-token-for-api-correlation-evidence>
POSTGRES_DSN=<supabase-postgres-connection-string>
EVIDENCE_POSTGRES_DSN=<supabase-postgres-connection-string>
ALLOWED_ORIGINS=https://aegis-frontend-free.onrender.com
```

Deploy this profile from Render's Blueprint flow by selecting `render.free.yaml`. After deployment, verify the API with `/health` and open the frontend URL. The first request after an idle period may be slow while a Free service wakes.

## Environment variables

Frontend:

```env
NEXT_PUBLIC_API_URL=https://<aegis-api-domain>
```

API:

```env
AEGIS_JWT_SECRET=<random-32-plus-character-secret>
ALLOWED_ORIGINS=https://<frontend-domain>
COOKIE_SAMESITE=none
CORRELATION_URL=http://<correlation-private-host>:8000
EVIDENCE_URL=http://<evidence-private-host>:8000
REDIS_URL=<render-key-value-internal-url>
ENVIRONMENT=production
```

## Deployment order

1. Create Render Postgres and Key Value in the same region.
2. Deploy correlation and evidence as private services.
3. Set their database variables and verify `/health`.
4. Deploy the API web service and set private service URLs.
5. Deploy the frontend with `NEXT_PUBLIC_API_URL` set at build time.
6. Update API `ALLOWED_ORIGINS` to the final frontend origin.
7. Run the deployment smoke contract:

```powershell
$env:AEGIS_DEPLOYMENT_URL = "https://<aegis-api-domain>"
python -m unittest tests.e2e.test_deployment_smoke -v
```

## Current boundary

Ingestion still depends on Kafka-compatible Redpanda and S3-compatible object storage. Keep that service in Docker Compose until managed Kafka and object storage are selected, or add those providers before deploying ingestion to Render. The core dashboard/API/evidence/correlation slice can be deployed independently.
