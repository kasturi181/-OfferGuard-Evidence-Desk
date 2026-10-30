// Website details for every company-looking domain: when it was registered and by whom. Reads report.intel.
export default function DomainIntel({ intel }) {
  if (!intel?.length) return null;
  return (
    <section>
      <h3>Website details</h3>
      <p className="muted">Public registration data for each website or company email domain in the message. A very new site is a weak warning. An old site proves nothing.</p>
      <div className="grid">
        {intel.map((d) => (
          <article key={d.domain} className={`card intel ${d.is_new ? "isnew" : ""}`}>
            <header><b>{d.domain}</b>{d.status === "ok" ? <span className={`pill ${d.is_new ? "sev-medium" : ""}`}>{d.is_new ? "new site" : "established"}</span> : <span className="pill st-unavailable">not available</span>}</header>
            {d.status === "ok" ? (
              <dl>
                <dt>Registered</dt><dd>{d.registered} ({d.age_days} days ago)</dd>
                <dt>Registrar</dt><dd>{d.registrar || "not published"}</dd>
              </dl>
            ) : <p className="muted">{d.note}</p>}
            <small className="muted">Source: RDAP public registration data</small>
          </article>
        ))}
      </div>
    </section>
  );
}
