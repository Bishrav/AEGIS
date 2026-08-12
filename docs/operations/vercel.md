# Vercel Portfolio Deployment

The AEGIS operations dashboard is deployed to Vercel Hobby at:

<https://aegis-dashboard-beta.vercel.app>

This is the no-card portfolio setup:

- Vercel hosts the Next.js frontend.
- Supabase remains the durable PostgreSQL/vector store.
- The complete backend runs locally through Docker Compose.
- Cloudflare Quick Tunnel temporarily exposes the local API during a live demo.

## Start a demo session

Start the backend first:

```powershell
docker compose up -d
```

Start a temporary API tunnel:

```powershell
cloudflared tunnel --url http://localhost:8000 --no-autoupdate
```

Copy the generated `trycloudflare.com` URL into the Vercel project's `NEXT_PUBLIC_API_URL` variable for Production, then redeploy. Add the Vercel production origin to the API `ALLOWED_ORIGINS` value and restart the API container. The tunnel URL changes whenever the Quick Tunnel process stops, so this is intended for demonstrations rather than uptime.

## Deployment checks

```powershell
Invoke-WebRequest https://aegis-dashboard-beta.vercel.app
Invoke-WebRequest https://<temporary-api-tunnel>/health
```

The Vercel build is configured without Next.js standalone output because Vercel supplies its own runtime. The Dockerfile uses the standard `next start` path for local container deployments.
