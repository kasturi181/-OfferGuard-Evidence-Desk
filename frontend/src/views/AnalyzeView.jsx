import { useState } from "react";
import { analyze, analyzePdf, ocrImage } from "../api.js";
import { demoCases } from "../fixtures/demoCases.js";
import EvidenceLedger from "../report/EvidenceLedger.jsx";

export default function AnalyzeView({ onReport }) {
  const [text, setText] = useState("");
  const [sim, setSim] = useState(false);
  const [report, setReport] = useState(null);
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const [ocr, setOcr] = useState(null);
  const [note, setNote] = useState("");

  // A lone domain such as "acme.com/join" is turned into a link so the live checks run on it.
  const norm = (t) => { const x = t.trim(); return /^[a-z0-9-]+(\.[a-z0-9-]+)+(\/\S*)?$/i.test(x) ? "https://" + x : x; };
  const run = async (fn) => {
    setBusy(true); setErr("");
    try { const r = await fn(); setReport(r); if (onReport) onReport(r); } catch (e) { setErr(e.message); setReport(null); }
    setBusy(false);
  };

  const readImage = async (file) => {
    setErr(""); setNote(""); setReport(null);
    if (file.size > 8_000_000) { setErr("Image is too large (max 8 MB)."); return; }
    setOcr(0);
    try {
      const t = await ocrImage(file, setOcr);
      if (t.length < 15) setErr("Could not find readable text in this image. Try a clearer screenshot, or paste the text.");
      else { setText(t); setNote("Text was read from your image on this device. Check it for mistakes, then click Analyze."); }
    } catch { setErr("Could not read the image. Paste the text instead."); }
    setOcr(null);
  };

  const go = (demo) => {
    if (demo) setText(demoCases[0].text);
    setTimeout(() => document.getElementById("tool")?.scrollIntoView({ behavior: "smooth", block: "start" }), 50);
  };

  return (
    <>
      <section className="lp-hero">
        <div className="lp-copy">
          <div className="eyebrow"><i className="dot" /> OFFERGUARD // EVIDENCE DESK</div>
          <h1>Don't just trust a job offer.<br /><span className="grad">Audit it.</span></h1>
          <p className="lead">Paste the message, a text PDF or a chat screenshot. OfferGuard looks up the domains live, decodes the company registration number and shows the exact words behind every warning. It never says "safe".</p>
          <div className="cta">
            <button className="primary" onClick={() => go(false)}>Check an offer</button>
            <button className="ghost" onClick={() => go(true)}>Try live demo (no sign-up)</button>
          </div>
          <div className="trust-row"><span>🔒 Text not stored</span><span>🧾 19 fixed rules</span><span>🔎 Live lookups</span><span>🇮🇳 CIN decoder</span></div>
        </div>
        <aside className="lp-panel" aria-label="Sample report">
          <div className="panel-top"><span className="mono">SAMPLE REPORT · FAKE OFFER</span><span className="live"><i className="dot" /> ILLUSTRATIVE</span></div>
          <div className="tiles">
            <div className="tile2 bad"><span>FEE DEMANDED</span><b>₹2,000</b><small>before joining</small></div>
            <div className="tile2 bad"><span>DOMAIN AGE</span><b>3 days</b><small>registered recently</small></div>
            <div className="tile2 bad"><span>MAIL SERVER</span><b>NONE</b><small>cannot receive replies</small></div>
            <div className="tile2 warn"><span>CIN CHECK</span><b>INVALID</b><small>type contradicts name</small></div>
          </div>
          <div className="callout">⛔ <b>HIGH RISK.</b> Do not pay or share documents.</div>
          <small className="muted">Illustrative values only, not a real result. Paste your own offer below.</small>
        </aside>
      </section>

      <section className="card input" id="tool">
        <div className="eyebrow"><i className="dot" /> CHECK AN OFFER</div>
        <div className="chips">{demoCases.map((d) => <button key={d.label} className="chip" onClick={() => setText(d.text)}>{d.label}</button>)}</div>
        <textarea rows={7} value={text} onChange={(e) => setText(e.target.value)} placeholder="Paste a recruitment message, or just a website link to check (for example acme-careers.com)…" />
        <div className="row">
          <button className="primary" disabled={busy || !text.trim()} onClick={() => run(() => analyze(norm(text), { simulateFailure: sim }))}>{busy ? "Analyzing…" : "Analyze"}</button>
          <label className="btn">Upload PDF<input type="file" accept="application/pdf" hidden onChange={(e) => { const f = e.target.files[0]; e.target.value = ""; if (f) run(() => analyzePdf(f)); }} /></label>
          <label className="btn">{ocr == null ? "Upload screenshot" : `Reading image… ${ocr}%`}<input type="file" accept="image/*" hidden disabled={ocr != null} onChange={(e) => { const f = e.target.files[0]; e.target.value = ""; if (f) readImage(f); }} /></label>
          <label className="check-l"><input type="checkbox" checked={sim} onChange={(e) => setSim(e.target.checked)} /> Simulate URL check failure</label>
        </div>
        {note && <p className="banner info">{note}</p>}
        {busy && <p className="muted">Running live lookups (domain age, DNS, redirects). Takes 5–15 seconds. The first request can take up to a minute while the free server wakes up.</p>}
      </section>
      {err && <p className="banner err">{err}</p>}
      {report && <EvidenceLedger r={report} />}

      <section className="lp-sec">
        <div className="eyebrow">THE REALITY</div>
        <h2>Fake offers follow a pattern</h2>
        <div className="cards3">
          <div className="fcard"><b>💸 Pay first, job never</b><p>Registration, training or "security" fees before you even start. Real employers do not charge candidates.</p></div>
          <div className="fcard"><b>🔑 OTPs and documents</b><p>Requests for OTPs, Aadhaar, PAN or bank details in the first message, often with a deadline.</p></div>
          <div className="fcard"><b>🎭 Look-alike domains</b><p>A brand-new website or email that imitates a real company's name, with no mail server behind it.</p></div>
        </div>
      </section>

      <section className="lp-sec">
        <div className="eyebrow">HOW IT WORKS</div>
        <h2>From message to evidence in seconds</h2>
        <div className="steps4">
          {[["01", "Paste", "Text, a text PDF or a screenshot (read on your device)."], ["02", "Extract", "Company, emails, links, CIN, salary and payment phrases."], ["03", "Check live", "Domain age, DNS and mail records, link redirects, CIN decoding."], ["04", "Evidence report", "Findings with exact words, a checklist and ready-to-send messages."]].map(([n, t, d]) => (
            <div className="step4" key={n}><span className="num">{n}</span><b>{t}</b><p>{d}</p></div>
          ))}
        </div>
      </section>

      <section className="lp-sec">
        <div className="eyebrow">FEATURES</div>
        <h2>Built to be checked, not trusted blindly</h2>
        <div className="cards4">
          {[["LIVE", "Live lookups", "Domain age (RDAP), DNS and mail servers, where links really lead. No API key."], ["INDIA", "CIN decoder", "Reads state, year and company type from the registration number and catches contradictions."], ["EXPLAINABLE", "Evidence highlighting", "Every finding points at the exact words in your message."], ["RULES", "19 fixed rules", "Same input, same answer. No AI guessing, fully auditable."], ["PRIVATE", "On-device OCR", "Screenshots are read in your browser and never uploaded."], ["ACTION", "What to do next", "A tailored checklist and ready-to-send verification messages."], ["HONEST", "Not checked, never safe", "Checks that could not run are listed openly."], ["MEASURED", "Evaluation tab", "Precision and recall on 20 labelled cases, failures shown."]].map(([tag, t, d]) => (
            <div className="fcard" key={t}><span className="tag">{tag}</span><b>{t}</b><p>{d}</p></div>
          ))}
        </div>
      </section>

      <section className="lp-sec">
        <div className="eyebrow">TRUST</div>
        <h2>Designed to be honest</h2>
        <div className="cards3">
          <div className="fcard"><b>🔒 Private by design</b><p>No account. Offer text is not stored. Screenshots stay on your device.</p></div>
          <div className="fcard"><b>🧮 Deterministic rules</b><p>No language model makes the decision, so there is nothing to hallucinate.</p></div>
          <div className="fcard"><b>⚖️ Clear limits</b><p>Warning signs are not proof. A clean result means "no known warning signs".</p></div>
        </div>
      </section>
    </>
  );
}
