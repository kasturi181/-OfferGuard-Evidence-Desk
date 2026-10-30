// Top of every report: what the offer says, whether to proceed, and what you risk. Reads report.brief (backend/audit.py).
const STATE = {
  stop: { cls: "stop", icon: "⛔", label: "Do not proceed" },
  pause: { cls: "pause", icon: "⏸️", label: "Pause and verify" },
  verify: { cls: "verify-s", icon: "🔎", label: "Verify first" },
};
const ROWS = [["role", "What"], ["company", "Who"], ["location", "Where"], ["start", "When it starts"], ["mode", "How you work"], ["pay", "Pay"], ["contact", "Recruiter contact"]];

export default function OfferBrief({ brief }) {
  if (!brief || !brief.facts) return null;
  const s = STATE[brief.state] || STATE.verify;
  const c = brief.completeness;
  return (
    <section className="brief">
      <div className={`decision ${s.cls}`}>
        <span className="d-icon" aria-hidden>{s.icon}</span>
        <div>
          <small className="muted">Should you proceed?</small>
          <h2>{brief.headline}</h2>
          <p>{brief.subline}</p>
          {brief.because?.length > 0 && <p className="because"><b>Because:</b> {brief.because.join(" · ")}</p>}
        </div>
      </div>

      <div className="grid2">
        <article className="card">
          <h3>The offer, as stated in the message</h3>
          <dl className="facts">
            {ROWS.map(([k, label]) => (
              <div key={k}>
                <dt>{label}</dt>
                <dd className={brief.facts[k] ? "" : "notstated"}>{brief.facts[k] || "Not stated"}</dd>
              </div>
            ))}
          </dl>
          <p className="muted"><small>{c.stated} of {c.total} key details stated{c.missing.length ? `. Missing: ${c.missing.join(", ")}` : ""}. {c.note}</small></p>
        </article>

        <article className="card">
          <h3>What you risk if you go ahead without verifying</h3>
          <ul className="risks">{brief.risks_if_unverified.map((r) => <li key={r}>{r}</li>)}</ul>
          <h3>Confirm these before you accept</h3>
          <ul className="risks">{brief.must_verify.map((r) => <li key={r}>{r}</li>)}</ul>
          <p className="muted"><small>{brief.upside_note}</small></p>
        </article>
      </div>
    </section>
  );
}
