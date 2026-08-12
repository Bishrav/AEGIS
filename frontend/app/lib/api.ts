export const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "");

export function apiUrl(path: string): string {
  return `${API_URL}${path.startsWith("/") ? path : `/${path}`}`;
}

export const apiRequest = (path: string, init: RequestInit = {}) =>
  fetch(apiUrl(path), { ...init, credentials: "include" });
