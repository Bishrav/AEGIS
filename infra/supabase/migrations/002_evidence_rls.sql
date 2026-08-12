alter table public.aegis_documents enable row level security;
alter table public.aegis_evidence_chunks enable row level security;

-- No anon/authenticated policies are created intentionally.
-- Evidence access is routed through server-side AEGIS services.
