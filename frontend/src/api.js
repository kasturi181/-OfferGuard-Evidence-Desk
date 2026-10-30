const BASE = (import.meta.env.VITE_API_BASE_URL || "https://offerguard-api-20f2.onrender.com").replace(/\/+$/, "");

async function request(path, init, ms = 60000) {
  const ctl = new AbortController();
  const t = setTimeout(() => ctl.abort(), ms);
  try {
    const r = await fetch(BASE + path, { ...init, signal: ctl.signal });
    if (!r.ok) {
      let msg = `Server error ${r.status} at ${BASE + path}`;
      try { const d = (await r.json()).detail; if (d) msg = typeof d === "string" ? d : JSON.stringify(d); } catch {}
      const e = new Error(msg); e.userFacing = true; throw e;
    }
    return await r.json();
  } finally { clearTimeout(t); }
}

// Reduced local fallback (4 rules). Clearly labelled; never claims the backend ran.
function localAnalyze(text, reason = "") {
  const rules = [
    ["RULE-01", "strong", "Upfront payment request", /(?:pay|deposit|transfer|send)[^.\n]{0,60}?(?:registration|processing|security|joining|training|refundable)[^.\n]{0,25}?(?:fee|fees|charges?|deposit)|(?:registration|processing|security|joining|refundable)\s+(?:fee|fees|charges?)[^.\n]{0,40}/i, "Do not pay until verified."],
    ["RULE-02", "strong", "Credential / OTP request", /(?:share|send|provide|give|enter)[^.\n]{0,40}\b(?:otp|password|pin|cvv)\b[^.\n]{0,20}/i, "Never share credentials."],
    ["RULE-07", "medium", "Guaranteed selection or pressure", /(?:guaranteed (?:job|selection)|100%\s*selection|last chance|today only|act now)[^.\n]{0,30}/i, "Take time. Verify first."],
    ["RULE-09", "weak", "Redirect to messaging app / form", /(?:telegram|whatsapp)[^.\n]{0,50}/i, "Prefer official portal."],
  ];
  const findings = [];
  for (const [id, sev, title, re, action] of rules) {
    const m = re.exec(text);
    if (m) findings.push({ rule_id: id, severity: sev, title, claim: title, evidence: m[0].trim(), start: m.index, end: m.index + m[0].length, source: "User-provided message (local fallback rules)", why: "Matched a deterministic local rule.", status: "matched_rule", uncertainty: "Text observation only.", action });
  }
  const c = { strong: 0, medium: 0, weak: 0, info: 0 };
  findings.forEach((f) => c[f.severity]++);
  const level = c.strong ? "high" : c.medium >= 2 ? "elevated" : findings.length ? "some" : "none";
  const now = new Date().toISOString();
  return {
    mode: "local_fallback", fallback_reason: reason, analyzed_text: text, extracted_fields: {}, findings, checklist: [],
    checks: ["url_reputation", "company_identity"].map((n) => ({ name: n, status: "not_checked", source: "-", checked_at: now, details: "Backend unreachable. Check NOT performed." })),
    assessment: { level, counts: c, summary: "Backend unreachable. Only 4 local rules ran. NOT proof of safety.", note: "Rule-count indicator. Not a fraud probability." },
    missing_checks: ["Backend analysis, URL reputation and company checks were NOT performed."],
    limitations: ["Local fallback runs a reduced rule set. The Python backend did not run."],
  };
}

export async function analyze(text, { simulateFailure = false } = {}) {
  try {
    return await request("/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text, simulate_url_failure: simulateFailure }) });
  } catch (e) {
    if (e.userFacing) throw e;
    return localAnalyze(text, `${e.name}: ${e.message} | calling ${BASE}/analyze`);
  }
}

export async function analyzePdf(file) {
  const fd = new FormData(); fd.append("file", file);
  try { return await request("/analyze-pdf", { method: "POST", body: fd }); }
  catch (e) {
    if (e.userFacing) throw e;
    throw new Error(`Backend unreachable. PDF analysis needs the backend. Paste the text instead. (${e.name}: ${e.message})`);
  }
}

export const getBenchmark = () => request("/benchmark", {}, 60000);

export const getStats = () => request("/stats", {}, 30000);

export const submitReport = (payload) =>
  request("/report", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });

// Reads text from a screenshot in the browser (Tesseract). The image never leaves the user's device.
export async function ocrImage(file, onProgress) {
  const { createWorker } = await import("tesseract.js");
  const worker = await createWorker("eng", 1, {
    logger: (m) => { if (m.status === "recognizing text" && onProgress) onProgress(Math.round(m.progress * 100)); },
  });
  try {
    const { data } = await worker.recognize(file);
    return (data.text || "").trim();
  } finally {
    await worker.terminate();
  }
}
