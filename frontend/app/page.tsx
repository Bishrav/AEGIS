"use client";

import { useEffect, useState } from "react";

type User = { user_id: string; role: string };

const incidents = [
  { id: "INC-042", title: "Sindhupalchok flood risk", district: "Sindhupalchok", level: "CRITICAL", score: "0.82", age: "12 min ago" },
  { id: "INC-041", title: "Melamchi river threshold breach", district: "Sindhupalchok", level: "HIGH", score: "0.67", age: "38 min ago" },
  { id: "INC-039", title: "Araniko Highway disruption", district: "Dolakha", level: "MODERATE", score: "0.44", age: "1 hr ago" },
];

export default function Dashboard() {
  const [user, setUser] = useState<User | null>(null);
  const [loginOpen, setLoginOpen] = useState(false);
  const [credentials, setCredentials] = useState({ username: "analyst", password: "analyst-dev" });

  useEffect(() => {
    fetch("http://localhost:8000/api/v1/me", { credentials: "include" })
      .then((response) => response.ok ? response.json() : null)
      .then(setUser)
      .catch(() => undefined);
  }, []);

  async function login(event: React.FormEvent) {
    event.preventDefault();
    const response = await fetch("http://localhost:8000/api/v1/auth/login", { method: "POST", credentials: "include", headers: { "Content-Type": "application/json" }, body: JSON.stringify(credentials) });
    if (response.ok) {
      setUser(await response.json());
      setLoginOpen(false);
    }
  }

  return <main className="shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">A</span><span>AEGIS</span></div>
      <p className="eyebrow">OPERATIONS CENTER</p>
      <nav><a className="active" href="#overview">Overview</a><a href="#incidents">Incidents</a><a href="#evidence">Evidence</a><a href="#graph">Knowledge graph</a><a href="#models">Model evaluation</a></nav>
      <div className="sidebar-footer"><span className="pulse" /> Systems nominal<br /><small>v0.6.0 · Nepal flood MVP</small></div>
    </aside>
    <section className="content">
      <header className="topbar"><div><p className="eyebrow">WEDNESDAY · 12 AUG 2026</p><h1>Flood intelligence overview</h1></div><div className="user-area">{user ? <><span className="avatar">{user.role[0]}</span><span>{user.role}</span></> : <button className="button" onClick={() => setLoginOpen(true)}>Sign in</button>}</div></header>
      <section id="overview" className="metrics"><Metric label="Active incidents" value="12" hint="+3 since 06:00" tone="red" /><Metric label="Critical risk" value="02" hint="Requires attention" tone="amber" /><Metric label="Signals processed" value="4,281" hint="Last 24 hours" /><Metric label="Source health" value="98.4%" hint="4 / 4 connected" tone="green" /></section>
      <section className="hero-grid"><div className="map-card"><div className="card-heading"><div><p className="eyebrow">SPATIAL VIEW</p><h2>Risk activity map</h2></div><span className="live-tag"><span className="pulse" /> LIVE REPLAY</span></div><div className="map"><div className="map-grid" /><div className="mountain m1" /><div className="mountain m2" /><Pin x="58%" y="34%" level="critical" label="Sindhupalchok" /><Pin x="48%" y="61%" level="high" label="Melamchi" /><Pin x="72%" y="50%" level="moderate" label="Dolakha" /><div className="map-label">NEPAL · FLOOD RISK SIGNALS</div></div></div><div className="risk-card"><p className="eyebrow">RISK DISTRIBUTION</p><h2>Current posture</h2><div className="donut"><strong>12</strong><span>active<br />incidents</span></div><div className="legend"><Legend color="red" label="Critical" value="2" /><Legend color="orange" label="High" value="4" /><Legend color="yellow" label="Moderate" value="6" /></div></div></section>
      <section id="incidents" className="panel"><div className="card-heading"><div><p className="eyebrow">PRIORITIZED QUEUE</p><h2>Active incidents</h2></div><button className="text-button">View all incidents →</button></div><div className="incident-list">{incidents.map((incident) => <article className="incident" key={incident.id}><div className={`severity ${incident.level.toLowerCase()}`} /><div className="incident-main"><div className="incident-title"><strong>{incident.title}</strong><span className={`badge ${incident.level.toLowerCase()}`}>{incident.level}</span></div><p>{incident.id} · {incident.district} · {incident.age}</p></div><div className="score"><strong>{incident.score}</strong><small>risk score</small></div><button className="arrow">→</button></article>)}</div></section>
      <section className="bottom-grid"><div id="evidence" className="panel stream"><div className="card-heading"><div><p className="eyebrow">NORMALIZED SIGNALS</p><h2>Event stream</h2></div><span className="live-tag">4 SOURCES</span></div><div className="event"><span className="event-dot rain" /><div><strong>Heavy rainfall detected</strong><p>Open-Meteo · Sindhupalchok</p></div><time>09:00</time></div><div className="event"><span className="event-dot river" /><div><strong>River threshold breached</strong><p>BIPAD Hydrology · Melamchi</p></div><time>10:15</time></div><div className="event"><span className="event-dot road" /><div><strong>Road closure reported</strong><p>BIPAD Infrastructure · Araniko Highway</p></div><time>11:10</time></div></div><div id="models" className="panel readiness"><p className="eyebrow">PLATFORM READINESS</p><h2>Processing pipeline</h2><div className="progress-line"><span style={{ width: "92%" }} /></div><div className="readiness-row"><span>Ingestion</span><b>Healthy</b></div><div className="readiness-row"><span>ML inference</span><b>Healthy</b></div><div className="readiness-row"><span>Correlation</span><b>Healthy</b></div><div className="readiness-row"><span>Evidence retrieval</span><b>Healthy</b></div></div></section>
    </section>
    {loginOpen && <div className="modal-backdrop"><form className="modal" onSubmit={login}><button type="button" className="modal-close" onClick={() => setLoginOpen(false)}>×</button><p className="eyebrow">SECURE ACCESS</p><h2>Sign in to AEGIS</h2><label>Username<input value={credentials.username} onChange={(e) => setCredentials({ ...credentials, username: e.target.value })} /></label><label>Password<input type="password" value={credentials.password} onChange={(e) => setCredentials({ ...credentials, password: e.target.value })} /></label><button className="button primary" type="submit">Open operations center</button></form></div>}
  </main>;
}

function Metric({ label, value, hint, tone }: { label: string; value: string; hint: string; tone?: string }) { return <div className="metric"><p>{label}</p><strong className={tone}>{value}</strong><small>{hint}</small></div>; }
function Legend({ color, label, value }: { color: string; label: string; value: string }) { return <div className="legend-row"><span className={`legend-dot ${color}`} />{label}<strong>{value}</strong></div>; }
function Pin({ x, y, level, label }: { x: string; y: string; level: string; label: string }) { return <div className="pin-wrap" style={{ left: x, top: y }}><span className={`pin ${level}`} /><small>{label}</small></div>; }
