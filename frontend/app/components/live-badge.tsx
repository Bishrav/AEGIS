"use client";

import { useEffect, useState } from "react";
import { apiUrl } from "../lib/api";

export function LiveBadge() {
  const [connected, setConnected] = useState(false);
  useEffect(() => {
    const source = new EventSource(apiUrl("/api/v1/events/stream"), { withCredentials: true });
    source.onopen = () => setConnected(true);
    source.onerror = () => setConnected(false);
    return () => source.close();
  }, []);
  return <span className={`live-tag ${connected ? "connected" : ""}`}><span className="pulse" /> {connected ? "LIVE UPDATES" : "SIGN IN FOR LIVE"}</span>;
}
