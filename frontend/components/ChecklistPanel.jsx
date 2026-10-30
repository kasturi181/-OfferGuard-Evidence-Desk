import { useState } from "react";

const LABEL = { now: "Do now", next: "Next", always: "Always" };

export default function ChecklistPanel({ steps = [] }) {
  const [done, setDone] = useState({});
  if (!steps.length) return null;
  const left = steps.filter((s) => !done[s.id]).length;
  return (
    <section className="og-card">
      <div className="og-card-head">
        <h3>Your safety checklist</h3>
        <span className="og-pill">{left} left</span>
      </div>
      <ul className="og-checklist">
        {steps.map((s) => (
          <li key={s.id} className={done[s.id] ? "done" : ""}>
            <label>
              <input type="checkbox" checked={!!done[s.id]}
                onChange={() => setDone({ ...done, [s.id]: !done[s.id] })} />
              <span>
                <span className={`og-tag og-tag-${s.priority}`}>{LABEL[s.priority]}</span>
                <b>{s.action}</b>
                <small>{s.why}{s.trigger !== "general" ? ` · from: ${s.trigger}` : ""}</small>
              </span>
            </label>
          </li>
        ))}
      </ul>
      <p className="og-muted">
        Report fraud: <a href="https://cybercrime.gov.in" target="_blank" rel="noreferrer">cybercrime.gov.in</a> or call <b>1930</b>.
      </p>
    </section>
  );
}
