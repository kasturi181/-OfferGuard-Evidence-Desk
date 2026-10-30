import { useState } from "react";
import { analyze, analyzePdf, ocrImage } from "../api.js";
import { demoCases } from "../fixtures/demoCases.js";
import EvidenceLedger from "../report/EvidenceLedger.jsx";

export default function AnalyzeView() {
  const [text, setText] = useState("");
  const [sim, setSim] = useState(false);
  const [report, setReport] = useState(null);
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const [ocr, setOcr] = useState(null);
  const [note, setNote] = useState("");

  const run = async (fn) => {
    setBusy(true); setErr("");
    try { setReport(await fn()); } catch (e) { setErr(e.message); setReport(null); }
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

  return (
    <>
      <section className="hero">
        <h1>Is this job offer real? <span className="grad">Check the evidence.</span></h1>
        <p className="muted">Paste the message, a text PDF or a chat screenshot. OfferGuard looks up the domains live, decodes the company's registration number, and shows the exact words behind every warning. It never says "safe".</p>
        <div className="why">
          <div><b>🔎 Live lookups</b><span>Domain age, DNS and mail servers, where links really lead. Facts a chatbot cannot see.</span></div>
          <div><b>🧾 Every claim is traceable</b><span>Fixed rules, same answer every time, each one points at your exact words. No guessing.</span></div>
          <div><b>🔒 Private</b><span>No account. Offer text is not stored. Screenshots are read on your device.</span></div>
        </div>
      </section>
      <section className="card input">
        <div className="chips">{demoCases.map((d) => <button key={d.label} className="chip" onClick={() => setText(d.text)}>{d.label}</button>)}</div>
        <textarea rows={7} value={text} onChange={(e) => setText(e.target.value)} placeholder="Paste recruitment message here…" />
        <div className="row">
          <button className="primary" disabled={busy || !text.trim()} onClick={() => run(() => analyze(text, { simulateFailure: sim }))}>{busy ? "Analyzing…" : "Analyze"}</button>
          <label className="btn">Upload PDF<input type="file" accept="application/pdf" hidden onChange={(e) => { const f = e.target.files[0]; e.target.value = ""; if (f) run(() => analyzePdf(f)); }} /></label>
          <label className="btn">{ocr == null ? "Upload screenshot" : `Reading image… ${ocr}%`}<input type="file" accept="image/*" hidden disabled={ocr != null} onChange={(e) => { const f = e.target.files[0]; e.target.value = ""; if (f) readImage(f); }} /></label>
          <label className="check-l"><input type="checkbox" checked={sim} onChange={(e) => setSim(e.target.checked)} /> Simulate URL check failure</label>
        </div>
        {note && <p className="banner info">{note}</p>}
        {busy && <p className="muted">Running live lookups (domain age, DNS, redirects). Takes 5–15 seconds. The first request can take up to a minute while the free server wakes up.</p>}
      </section>
      {err && <p className="banner err">{err}</p>}
      {report && <EvidenceLedger r={report} />}
    </>
  );
}
