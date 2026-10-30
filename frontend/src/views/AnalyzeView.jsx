import { useState } from "react";
import { analyze, analyzePdf } from "../api.js";
import { demoCases } from "../fixtures/demoCases.js";
import EvidenceLedger from "../report/EvidenceLedger.jsx";

export default function AnalyzeView() {
  const [text, setText] = useState("");
  const [sim, setSim] = useState(false);
  const [report, setReport] = useState(null);
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  const run = async (fn) => {
    setBusy(true); setErr("");
    try { setReport(await fn()); } catch (e) { setErr(e.message); setReport(null); }
    setBusy(false);
  };

  return (
    <>
      <section className="hero">
        <h1>Check a job offer</h1>
        <p className="muted">Paste a recruitment message or upload a text PDF. You get evidence-linked warning signals, what could not be verified, and what to do next. Not a verdict.</p>
      </section>
      <section className="card input">
        <div className="chips">{demoCases.map((d) => <button key={d.label} className="chip" onClick={() => setText(d.text)}>{d.label}</button>)}</div>
        <textarea rows={7} value={text} onChange={(e) => setText(e.target.value)} placeholder="Paste recruitment message here…" />
        <div className="row">
          <button className="primary" disabled={busy || !text.trim()} onClick={() => run(() => analyze(text, { simulateFailure: sim }))}>{busy ? "Analyzing…" : "Analyze"}</button>
          <label className="btn">Upload PDF<input type="file" accept="application/pdf" hidden onChange={(e) => { const f = e.target.files[0]; e.target.value = ""; if (f) run(() => analyzePdf(f)); }} /></label>
          <label className="check-l"><input type="checkbox" checked={sim} onChange={(e) => setSim(e.target.checked)} /> Simulate URL check failure</label>
        </div>
        {busy && <p className="muted">First request can take up to a minute while the free server wakes up.</p>}
      </section>
      {err && <p className="banner err">{err}</p>}
      {report && <EvidenceLedger r={report} />}
    </>
  );
}
