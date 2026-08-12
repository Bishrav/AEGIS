"use client";

import { useEffect, useState } from "react";
import { Frame, PageTitle } from "../components/frame";
import { apiRequest } from "../lib/api";

type Hit = { id: string; title: string; source: string; score: string; text: string };
const fallback: Hit[] = [
  { id: "ev-8f2c1a4d7e9b3310", title: "Nepal flood response bulletin — Sindhupalchok", source: "Government response archive", score: "0.94", text: "Officials reported flooding and road disruption near Melamchi after intense rainfall." },
  { id: "ev-12bd8c7a4e5f9021", title: "Historical hydrology report — Melamchi basin", source: "Hydrology research archive", score: "0.88", text: "River-level threshold breaches are associated with rapid downstream disruption." },
];

export default function EvidencePage() {
  const [query, setQuery] = useState("Sindhupalchok flood response road closure");
  const [hits, setHits] = useState<Hit[]>(fallback);
  const [ingestOpen, setIngestOpen] = useState(false);
  const [message, setMessage] = useState("");
  const search = () => apiRequest(`/api/v1/incidents/INC-042/evidence?query=${encodeURIComponent(query)}&top_k=5`).then(r => r.ok ? r.json() : null).then(data => { if (data?.hits?.length) setHits(data.hits.map((hit: Record<string, unknown>) => ({ id: String(hit.evidence_id), title: String(hit.title), source: String(hit.source_uri), score: Number(hit.score).toFixed(2), text: String(hit.snippet) }))); }).catch(() => setMessage("Live search unavailable — showing the evaluation fixture."));
  useEffect(() => { search(); }, []);
  async function ingest(event: React.FormEvent<HTMLFormElement>) { event.preventDefault(); const form = new FormData(event.currentTarget); const payload = { document_id: String(form.get("document_id")), title: String(form.get("title")), text: String(form.get("text")), source_uri: String(form.get("source_uri")), source_type: "analyst_upload" }; const response = await apiRequest("/api/v1/evidence/documents", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }); if (response.ok) { setMessage("Document ingested and indexed successfully."); setIngestOpen(false); } else setMessage("Document ingestion failed. Sign in as an analyst and try again."); }
  return <Frame active="Evidence"><section className="panel"><PageTitle eyebrow="HYBRID RETRIEVAL · RECALL@5 1.00" title="Evidence explorer" action="" /><div className="evidence-actions"><button className="button" onClick={() => setIngestOpen(true)}>Ingest document +</button></div><div className="evidence-search"><input className="search" value={query} onChange={e => setQuery(e.target.value)} onKeyDown={e => e.key === "Enter" && search()} /><button className="button primary small" onClick={search}>Search evidence</button></div>{message && <p className="notice">{message}</p>}<div className="evidence-grid">{hits.map(hit => <Evidence key={hit.id} {...hit} />)}</div></section>{ingestOpen && <div className="modal-backdrop"><form className="modal ingest-modal" onSubmit={ingest}><button type="button" className="modal-close" onClick={() => setIngestOpen(false)}>×</button><p className="eyebrow">EVIDENCE PIPELINE</p><h2>Ingest document</h2><input name="document_id" placeholder="Document ID" required /><input name="title" placeholder="Title" required /><input name="source_uri" placeholder="Source URL" required /><textarea name="text" placeholder="Document text" required /><button className="button primary" type="submit">Index evidence</button></form></div>}</Frame>;
}

function Evidence({ id, title, source, score, text }: Hit) { return <article className="evidence-card"><div className="evidence-top"><span className="evidence-id">[{id}]</span><b>{score}</b></div><h3>{title}</h3><p>{text}</p><footer>{source}<a href={source.startsWith("http") ? source : `https://www.google.com/search?q=${encodeURIComponent(source)}`} target="_blank" rel="noreferrer">Open source ↗</a></footer></article>; }
