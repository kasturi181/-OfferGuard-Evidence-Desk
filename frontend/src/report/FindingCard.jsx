export default function FindingCard({ f }) {
  return (
    <article className={`card sev-${f.severity}`}>
      <header><span className="badge">{f.severity} signal</span> <b>{f.rule_id} · {f.title}</b></header>
      <dl>
        <dt>Claim</dt><dd>{f.claim}</dd>
        <dt>Observed evidence</dt><dd><mark>{f.evidence}</mark>{f.start != null && <small> (chars {f.start}–{f.end})</small>}</dd>
        <dt>Source</dt><dd>{f.source}</dd>
        <dt>Check status</dt><dd><code>{f.status}</code></dd>
        <dt>Why it matters</dt><dd>{f.why}</dd>
        <dt>Uncertainty</dt><dd>{f.uncertainty}</dd>
        <dt>Next action</dt><dd>{f.action}</dd>
      </dl>
    </article>
  );
}
