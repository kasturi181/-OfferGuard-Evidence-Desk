import FindingCard from "./FindingCard.jsx";

const LABEL = { high: "High concern", elevated: "Elevated", some: "Some signals", none: "No signals found" };

export default function EvidenceLedger({ r }) {
  const a = r.assessment;
  return (
    <section>
      {r.mode === "local_fallback" && <p className="banner warn">Backend unreachable — showing reduced local analysis.</p>}
      <div className={`summary lvl-${a.level}`}>
        <h2>{LABEL[a.level]}</h2>
        <p>{a.summary}</p>
        <small>{a.note} · strong {a.counts.strong} · medium {a.counts.medium} · weak {a.counts.weak}</small>
      </div>

      <h3>Findings</h3>
      {r.findings.length === 0 && <p>No findings.</p>}
      {r.findings.map((f) => <FindingCard key={f.rule_id} f={f} />)}

      <h3>Checks</h3>
      <table>
        <thead><tr><th>Check</th><th>Status</th><th>Source</th><th>Checked at</th><th>Details</th></tr></thead>
        <tbody>
          {r.checks.map((c) => (
            <tr key={c.name}><td>{c.name}</td><td><code>{c.status}</code></td><td>{c.source}</td><td>{c.checked_at}</td><td>{c.details}</td></tr>
          ))}
        </tbody>
      </table>
      {r.checks.some((c) => c.name === "url_reputation" && c.status !== "not_checked") && <small>URL advisory data: Google Safe Browsing. Potential risk only.</small>}

      {r.missing_checks.length > 0 && (<><h3>Not checked</h3><ul>{r.missing_checks.map((m, i) => <li key={i}>{m}</li>)}</ul></>)}

      <h3>Extracted fields</h3>
      <pre>{JSON.stringify(r.extracted_fields, null, 2)}</pre>

      <h3>Limitations</h3>
      <ul>{r.limitations.map((l, i) => <li key={i}>{l}</li>)}</ul>
    </section>
  );
}
