import { useState } from "react";
import { analyze, analyzePdf } from "./api.js";
import { demoCases } from "./fixtures/demoCases.js";
import EvidenceLedger from "./report/EvidenceLedger.jsx";

export default function App() {
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
    <main>
      <h1>🛡️ OfferGuard Evidence Desk</h1>
      <p className="sub">Paste a job offer or upload a text PDF. Get evidence-linked warning signals — not a verdict.</p>
      <div className="chips">{demoCases.map((d) => <button key={d.label} className="chip" onClick={() => setText(d.text)}>{d.label}</button>)}</div>
      <textarea rows={8} value={text} onChange={(e) => setText(e.target.value)} placeholder="Paste recruitment message here…" />
      <div className="row">
        <button disabled={busy || !text.trim()} onClick={() => run(() => analyze(text, { simulateFailure: sim }))}>{busy ? "Analyzing…" : "Analyze"}</button>
        <label className="file">Upload PDF<input type="file" accept="application/pdf" hidden onChange={(e) => e.target.files[0] && run(() => analyzePdf(e.target.files[0]))} /></label>
        <label><input type="checkbox" checked={sim} onChange={(e) => setSim(e.target.checked)} /> Simulate URL check failure</label>
      </div>
      {err && <p className="banner err">{err}</p>}
      {report && <EvidenceLedger r={report} />}
      <footer>Demo uses synthetic company records. Not legal advice. Signals ≠ proof of fraud.</footer>
    </main>
  );
}
