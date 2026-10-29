function Group({ title, items }) {
  if (!items?.length) return null;
  return (
    <div className="og-guide-group">
      <h4>{title}</h4>
      <ol>{items.map((s, i) => <li key={i}>{s}</li>)}</ol>
    </div>
  );
}

export default function GuidancePanel({ guidance }) {
  if (!guidance) return null;
  return (
    <section className="og-card">
      <div className="og-card-head"><h3>How to verify this employer yourself</h3></div>
      <div className="og-guide">
        <Group title="1 · Contact the employer through a trusted channel" items={guidance.contact_employer} />
        <Group title="2 · Confirm the vacancy" items={guidance.confirm_vacancy} />
        <Group title="3 · Report suspected fraud" items={guidance.report_fraud} />
      </div>
      <div className="og-links">
        {guidance.links?.map((l) => (
          <a key={l.url} href={l.url} target="_blank" rel="noreferrer noopener">{l.label} ↗</a>
        ))}
        <span className="og-helpline">Helpline <b>{guidance.helpline}</b></span>
      </div>
    </section>
  );
}
