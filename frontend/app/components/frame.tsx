import Link from "next/link";

export function Frame({ children, active }: { children: React.ReactNode; active: string }) {
  const links = [["Overview", "/"], ["Incidents", "/incidents"], ["Evidence", "/evidence"], ["Knowledge graph", "/graph"], ["Model evaluation", "/models"], ["Source health", "/sources"], ["Observability", "/observability"]];
  return <main className="shell"><aside className="sidebar"><Link className="brand" href="/"><span className="brand-mark">A</span><span>AEGIS</span></Link><p className="eyebrow">OPERATIONS CENTER</p><nav>{links.map(([label, href]) => <Link className={active === label ? "active" : ""} href={href} key={href}>{label}</Link>)}</nav><div className="sidebar-footer"><span className="pulse" /> Systems nominal<br /><small>v0.6.0 · Nepal flood MVP</small></div></aside><section className="content"><header className="topbar"><div><p className="eyebrow">WEDNESDAY · 12 AUG 2026</p><h1>{active}</h1></div><div className="user-area"><span className="avatar">A</span><span>ANALYST</span></div></header>{children}</section></main>;
}

export function PageTitle({ eyebrow, title, action }: { eyebrow: string; title: string; action?: string }) { return <div className="card-heading page-title"><div><p className="eyebrow">{eyebrow}</p><h2>{title}</h2></div>{action && <button className="text-button">{action}</button>}</div>; }
