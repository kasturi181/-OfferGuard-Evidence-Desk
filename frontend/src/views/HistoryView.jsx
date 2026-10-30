import { useState } from "react";
import { getHistory, clearHistory } from "../auth.js";
import { RULE_NAMES } from "../fixtures/demoCases.js";

const LBL = { none: "No signals", some: "Some signals", elevated: "Elevated", high: "High concern" };

export default function HistoryView({ user }) {
  const [h, setH] = useState(getHistory());
  return (
    <>
      <section className="lp-sec" style={{ marginTop: 20 }}>
        <div className="eyebrow">MY CHECKS · DEMO</div>
        <h2>Hi {user.name}, your recent checks</h2>
        <p className="muted">Stored only in this browser. Only the risk level, company name and rule IDs are kept, never the offer text.</p>
      </section>
      {h.length === 0 && <p className="card muted">No checks yet. Analyze an offer and it will appear here.</p>}
      {h.map((x, i) => (
        <article className={`card hist lvl-${x.level}`} key={i}>
          <header className="between"><b>{LBL[x.level] || x.level}{x.company ? ` · ${x.company}` : ""}</b><small className="muted">{new Date(x.t).toLocaleString()}</small></header>
          <div className="chips2">{x.rules.length ? x.rules.map((r) => <span className="chip2" key={r}>{RULE_NAMES[r] || r}</span>) : <span className="muted">No findings</span>}</div>
        </article>
      ))}
      {h.length > 0 && <button className="ghost" onClick={() => { clearHistory(); setH([]); }}>Clear history</button>}
    </>
  );
}
