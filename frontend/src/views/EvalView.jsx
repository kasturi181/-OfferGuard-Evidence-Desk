import { useEffect, useState } from "react";
import { getBenchmark } from "../api.js";

export default function EvalView() {
  const [b, setB] = useState(null);
  const [err, setErr] = useState("");
  useEffect(() => { getBenchmark().then(setB).catch((e) => setErr(e.message)); }, []);
  if (err) return <p className="banner err">Could not load evaluation: {err}</p>;
  if (!b) return <p className="muted">Running evaluation… (the free server may take a minute to wake)</p>;
  const pct = (x) => (x == null ? "–" : `${Math.round(x * 100)}%`);
  return (
    <>
      <section className="hero"><h1>How well do the rules work?</h1><p className="muted">{b.note}</p></section>
      <div className="tiles">
        <div className="tile"><b>{b.total}</b><span>labelled examples</span></div>
        <div className="tile"><b>{pct(b.precision)}</b><span>precision (flags that were right)</span></div>
        <div className="tile"><b>{pct(b.recall)}</b><span>recall (scams caught)</span></div>
        <div className="tile"><b>{pct(b.accuracy)}</b><span>accuracy</span></div>
      </div>
      <div className="card confusion">
        <table><thead><tr><th></th><th>Flagged</th><th>Not flagged</th></tr></thead>
          <tbody><tr><th>Scam</th><td className="good">{b.tp}</td><td className="bad">{b.fn} missed</td></tr>
            <tr><th>Benign</th><td className="bad">{b.fp} false alarm</td><td className="good">{b.tn}</td></tr></tbody></table>
      </div>
      <h3>Every example, including the failures</h3>
      <div className="evalrows">
        {b.cases.map((r) => (
          <article key={r.id} className={`card erow ${r.correct ? "" : "wrong"}`}>
            <header><b>{r.id}</b><span className="pill">{r.label}</span><span className={`pill ${r.correct ? "st-verified_match" : "sev-strong"}`}>{r.correct ? "correct" : r.flagged ? "false alarm" : "missed"}</span>
              <span className="pill">{r.level}</span></header>
            <p>{r.text}</p>
            <small className="muted">Rules found: {r.found.length ? r.found.join(", ") : "none"}{r.expected.length ? ` · expected: ${r.expected.join(", ")}` : ""}</small>
            {r.note && <small className="warnnote"> {r.note}</small>}
          </article>
        ))}
      </div>
    </>
  );
}
