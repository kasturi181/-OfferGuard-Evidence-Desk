export default function FindingCard({ f }) {
  return (
    <article className={`card finding sev-${f.severity}`}>
      <header>
        <span className={`pill sev-${f.severity}`}>{f.severity === "info" ? "info" : `${f.severity} signal`}</span>
        <b>{f.rule_id} · {f.title}</b>
      </header>
      <dl>
        <dt>Claim</dt><dd>{f.claim}</dd>
        <dt>Evidence</dt><dd><mark className={`hl hl-${f.severity}`}>{f.evidence}</mark>{f.start != null && <small> (chars {f.start}–{f.end})</small>}</dd>
        <dt>Source</dt><dd>{f.source}</dd>
        <dt>Status</dt><dd><code>{f.status}</code></dd>
        <dt>Why it matters</dt><dd>{f.why}</dd>
        <dt>Uncertainty</dt><dd>{f.uncertainty}</dd>
        <dt>Next action</dt><dd><b>{f.action}</b></dd>
      </dl>
    </article>
  );
}
