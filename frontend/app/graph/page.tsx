"use client";

import { useState } from "react";
import { Frame, PageTitle } from "../components/frame";

const allPaths = ["Flood incident → Araniko Highway", "Flood incident → Melamchi Hospital", "River spike → Flood incident"];

export default function GraphPage() {
  const [query, setQuery] = useState("");
  const [paths, setPaths] = useState(allPaths);
  const [message, setMessage] = useState("Showing BFS depth 3 from the active incident.");
  function traverse() { const value = query.trim().toLowerCase(); const filtered = value ? allPaths.filter(path => path.toLowerCase().includes(value)) : allPaths; setPaths(filtered); setMessage(`${filtered.length} impact path${filtered.length === 1 ? "" : "s"} found for ${value || "the active incident"}.`); }
  function reset() { setQuery(""); setPaths(allPaths); setMessage("Showing BFS depth 3 from the active incident."); }
  return <Frame active="Knowledge graph"><section className="panel"><PageTitle eyebrow="NEO4J IMPACT GRAPH · BFS DEPTH 3" title="Infrastructure dependency graph" action="" /><div className="graph-actions"><span className="graph-status">● LIVE GRAPH PROJECTION</span><button className="button small" onClick={reset}>Reset view</button></div><div className="graph-canvas"><div className="graph-edge e1" /><div className="graph-edge e2" /><div className="graph-edge e3" /><Node x="50%" y="45%" type="incident" label="Flood incident" /><Node x="23%" y="27%" type="event" label="River spike" /><Node x="76%" y="26%" type="event" label="Road closure" /><Node x="21%" y="71%" type="infra" label="Araniko Highway" /><Node x="78%" y="69%" type="infra" label="Melamchi Hospital" /><div className="graph-legend"><span><i className="node-dot incident" />Incident</span><span><i className="node-dot event" />Event</span><span><i className="node-dot infra" />Infrastructure</span></div></div></section><section className="bottom-grid"><div className="panel"><PageTitle eyebrow="TRAVERSAL" title="Impact paths" /><p className="notice">{message}</p>{paths.map(path => <div className="path-row" key={path}>{path}</div>)}</div><div className="panel"><PageTitle eyebrow="GRAPH QUERY" title="Explore dependencies" /><input className="search" value={query} onChange={e => setQuery(e.target.value)} onKeyDown={e => e.key === "Enter" && traverse()} placeholder="Search district, river, road..." /><button className="button primary small" onClick={traverse}>Run traversal</button></div></section></Frame>;
}
function Node({ x, y, type, label }: { x: string; y: string; type: string; label: string }) { return <div className="node-wrap" style={{ left: x, top: y }}><span className={`node-dot ${type}`} /><b>{label}</b><small>{type.toUpperCase()}</small></div>; }
