"use client";

import { useEffect, useState } from "react";

export function LiveBadge() {
  const [connected, setConnected] = useState(false);
  useEffect(() => {
    const source = new EventSource("http://localhost:8000/api/v1/events/stream", { withCredentials: true });
    source.onopen = () => setConnected(true);
    source.onerror = () => setConnected(false);
    return () => source.close();
  }, []);
  return <span className={`live-tag ${connected ? "connected" : ""}`}><span className="pulse" /> {connected ? "LIVE UPDATES" : "SIGN IN FOR LIVE"}</span>;
}
