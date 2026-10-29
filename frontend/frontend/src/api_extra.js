// Uses the same env var as your existing api.js. No Supabase keys in the frontend, ever.
const BASE = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

async function j(path, opts) {
  const r = await fetch(BASE + path, opts);
  if (!r.ok) throw new Error(`${path} failed (${r.status})`);
  return r.json();
}

export const getStats = (days = 14) => j(`/dashboard/stats?days=${days}`);
export const getRecent = (verdict) => j(`/dashboard/recent${verdict ? `?verdict=${verdict}` : ""}`);
export const reportScam = (body) =>
  j("/report-scam", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
