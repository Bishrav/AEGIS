create extension if not exists vector;

create table if not exists public.aegis_documents (
  document_id text primary key,
  title text not null,
  source_uri text not null,
  source_type text not null,
  published_at timestamptz,
  content text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.aegis_evidence_chunks (
  evidence_id text primary key,
  document_id text not null references public.aegis_documents(document_id) on delete cascade,
  title text not null,
  content text not null,
  source_uri text not null,
  embedding vector(128),
  created_at timestamptz not null default now()
);

create index if not exists aegis_evidence_chunks_document_idx on public.aegis_evidence_chunks(document_id);
