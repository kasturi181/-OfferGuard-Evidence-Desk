// Full audit trail: every rule (triggered / clear / could not run), every check, and how the result was made. Reads report.audit.
const RS = { triggered: ["Triggered", "t"], clear: ["Clear", "c"], could_not_run: ["Could not run", "n"] };

export default function AuditTrail({ r }) {
  const a = r.audit;
  if (!a) return null;
  const download = () => {
    const data = { audit: a, assessment: r.assessment, brief: r.brief, findings: r.findings, checks: r.checks, intel: r.intel };
    const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }));
    const el = document.createElement("a");
    el.href = url; el.download = "offerguard-audit.json"; el.click();
    URL.revokeObjectURL(url);
  };
  return (
    <section>
      <div className="between"><h3>Audit trail</h3><button className="btn small noprint" onClick={download}>Download audit (JSON)</button></div>
      <p className="muted">How this result was produced, so you can check our work. {a.counts.triggered} triggered · {a.counts.clear} clear · {a.counts.could_not_run} could not run.</p>
      <details className="card" open>
        <summary>All {a.rules.length} rules</summary>
        <table className="plain">
          <thead><tr><th>Rule</th><th>What it looks for</th><th>Result</th></tr></thead>
          <tbody>{a.rules.map((x) => (
            <tr key={x.rule_id} className={`ar-${RS[x.status][1]}`}>
              <td>{x.rule_id}</td><td>{x.title}</td>
              <td><span className={`pill ar-pill-${RS[x.status][1]}`}>{RS[x.status][0]}{x.severity ? ` (${x.severity})` : ""}</span></td>
            </tr>
          ))}</tbody>
        </table>
      </details>
      <details className="card">
        <summary>Checks and data sources ({a.checks.length})</summary>
        <table className="plain">
          <thead><tr><th>Check</th><th>Status</th><th>Source</th></tr></thead>
          <tbody>{a.checks.map((c) => <tr key={c.name}><td>{c.name}</td><td><span className={`pill st-${c.status}`}>{c.status.replace("_", " ")}</span></td><td>{c.source}</td></tr>)}</tbody>
        </table>
      </details>
      <details className="card">
        <summary>How the result was made</summary>
        <ul>{a.method.map((m) => <li key={m}>{m}</li>)}</ul>
        <p className="muted"><small>{a.engine}. Analysed {a.analyzed_at.replace("T", " ")} UTC. Input: {a.input.characters} characters, {a.input.links} links, {a.input.emails} emails, {a.input.phones} phone numbers. The offer text is not stored.</small></p>
      </details>
    </section>
  );
}
