import { useEffect, useState } from "react";
import { getHistory } from "../api.js";
import { RULE_NAMES } from "../fixtures/demoCases.js";

const LV = { high: "High concern", elevated: "Elevated", some: "Some signals", none: "No signals" };

export default function HistoryView() {
  const [d, setD] = useState(null);
  const [err, setErr] = useState("");
  useEffect(() => { getHistory().then(setD).catch((e) => setErr(e.message)); }, []);
  if (err) return <p className="banner err">{err}</p>;
  if (!d) return <p className="muted">Loading your checks…</p>;
  return (
    <>
      <section className="hero"><h1>My checks</h1><p className="muted">Your last analyses while signed in. Only the outcome is saved (risk level, company name, rules triggered). The offer text is never stored.</p></section>
      {d.items.length === 0 ? <p className="muted">Nothing yet. Analyze an offer while signed in and it appears here.</p> : (
        <div className="card">
          <table className="plain">
            <thead><tr><th>Date</th><th>Level</th><th>Company</th><th>Signals</th></tr></thead>
            <tbody>{d.items.map((r) => (
              <tr key={r.id}>
                <td>{r.created_at.slice(0, 10)}</td>
                <td><span className={`pill lvl-pill-${r.risk_level}`}>{LV[r.risk_level] || r.risk_level}</span></td>
                <td>{r.company || "—"}</td>
                <td>{(r.rule_ids || []).map((x) => (RULE_NAMES && RULE_NAMES[x]) || x).join(", ") || "—"}</td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      )}
    </>
  );
}
