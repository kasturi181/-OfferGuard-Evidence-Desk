const ICON = { match: "✓", mismatch: "✕", not_checked: "–" };
const TEXT = { match: "Consistent", mismatch: "Mismatch", not_checked: "Not checked" };

export default function ConsistencyPanel({ rows = [] }) {
  if (!rows.length) return null;
  return (
    <section className="og-card">
      <div className="og-card-head"><h3>Cross-source consistency</h3></div>
      <p className="og-muted">Each comparison is judged on its own. “Consistent” is not proof of a genuine offer.</p>
      <div className="og-cons">
        {rows.map((r, i) => (
          <article key={i} className={`og-cons-row st-${r.status}`}>
            <div className="og-cons-icon" aria-hidden>{ICON[r.status]}</div>
            <div>
              <div className="og-cons-title">{r.check} <span className="og-badge">{TEXT[r.status]}</span></div>
              <p>{r.detail}</p>
              {r.evidence?.length > 0 && (
                <div className="og-chips">{r.evidence.map((e, k) => <code key={k}>{e}</code>)}</div>
              )}
              {r.unverified && <small className="og-unverified">Still unverified: {r.unverified}</small>}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
