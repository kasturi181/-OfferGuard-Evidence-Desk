// Evidence-linked finding: extracted text, source, result, what remains unverified.
// Field names are read defensively so it works with your existing finding shape.
const SEV = { strong: "Strong", medium: "Medium", weak: "Weak", info: "Info" };
const RESULT = {
  warning: "Warning", verified_match: "Match found", no_match: "No match found",
  unavailable: "Could not check", not_checked: "Not checked",
};

export default function EvidenceCard({ f }) {
  const sev = (f.severity || "info").toLowerCase();
  const text = f.matched_text || f.evidence;
  const unverified = f.unverified || f.uncertainty;
  const title = f.title || f.claim || f.rule || "Warning sign";
  return (
    <article className={`og-ev sev-border-${sev}`}>
      <header>
        <h4>{title}</h4>
        <span className={`og-sevtag sev-${sev}`}>{SEV[sev] || "Info"}</span>
      </header>

      {text && (
        <blockquote>
          <small>Found in the text</small>
          <mark>{text}</mark>
          {f.start != null && <small className="og-offset">characters {f.start}–{f.end}</small>}
        </blockquote>
      )}

      <dl className="og-ev-grid">
        {f.source && (<><dt>Source checked</dt><dd>{f.source}</dd></>)}
        {f.status && (<><dt>Result</dt><dd>{RESULT[f.status] || f.status}</dd></>)}
        {f.confidence && (<><dt>Confidence</dt><dd>{f.confidence}</dd></>)}
        {(f.why || f.why_it_matters) && (<><dt>Why it matters</dt><dd>{f.why || f.why_it_matters}</dd></>)}
      </dl>

      {unverified && <p className="og-unverified"><b>Still unverified:</b> {unverified}</p>}
      {f.next_action && <p className="og-next">→ {f.next_action}</p>}
    </article>
  );
}
