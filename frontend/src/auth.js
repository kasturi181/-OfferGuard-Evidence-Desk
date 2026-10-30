// DEMO sign-in. Nothing is sent to a server. Data lives only in this browser (localStorage), outcome only, never offer text.
const K = "og_demo_user", H = "og_demo_hist";
const rd = (k, d) => { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch { return d; } };
const wr = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* storage unavailable: app still works */ } };
export const getUser = () => rd(K, null);
export const login = (name, email) => { const u = { name: (name || "").trim() || "Guest", email: (email || "").trim() }; wr(K, u); return u; };
export const logout = () => { try { localStorage.removeItem(K); } catch { /* ignore */ } };
export const getHistory = () => rd(H, []);
export const addHistory = (r) => {
  const h = [{ t: new Date().toISOString(), level: r.assessment.level, counts: r.assessment.counts, company: r.extracted_fields?.company || "", rules: (r.findings || []).map((f) => f.rule_id) }, ...getHistory()].slice(0, 20);
  wr(H, h); return h;
};
export const clearHistory = () => wr(H, []);
