import FindingCard from "./FindingCard.jsx";
import RiskMeter from "./RiskMeter.jsx";
import HighlightedText from "./HighlightedText.jsx";
import Explain from "./Explain.jsx";
import Drafts from "./Drafts.jsx";
import Checklist from "./Checklist.jsx";

const NAMES = {
  url_reputation: "URL reputation", company_identity: "Company exists in dataset", email_domain_consistency: "Recruiter email domain",
  link_domain_consistency: "Links vs official domain", registration_id_consistency: "Registration ID (CIN)", location_consistency: "Location", community_reports: "User reports",
};
const LABEL = { verified_match: "matched", warning: "mismatch", no_match: "no known match", unavailable: "unavailable", not_checked: "not checked" };

export default function EvidenceLedger({ r }) {
  const f = r.extracted_fields || {};
  const chips = [
    f.company && ["Company", f.company], ...(f.recruiter_emails || []).map((e) => ["Email", e]), ...(f.url_domains || []).map((d) => ["Domain", d]),
    ...(f.registration_ids || []).map((c) => ["CIN", c]), ...(f.cities || []).map((c) => ["City", c]), ...(f.phones || []).map((p) => ["Phone", p]),
    ...(f.salaries || []).map((s) => ["Salary", `${s.raw} (~₹${s.monthly_inr.toLocaleString()}/mo)`]),
  ].filter(Boolean);
  return (
    <div className="report">
      {r.mode === "local_fallback" && (
        <p className="banner warn">Backend unreachable — showing reduced local analysis.<br /><small>{r.fallback_reason}</small></p>
      )}
      <RiskMeter a={r.assessment} />
      <div className="noprint right"><button className="btn small" onClick={() => window.print()}>Save report as PDF</button></div>
      <Explain data={r.explain} />

      <section>
        <h3>Your message, evidence highlighted</h3>
        <HighlightedText text={r.analyzed_text || ""} findings={r.findings} />
      </section>

      <Checklist items={r.checklist} />
      <Drafts items={r.drafts} />

      <section>
        <h3>Findings <span className="muted">({r.findings.length})</span></h3>
        {r.findings.length === 0 && <p className="muted">No findings.</p>}
        {r.findings.map((x) => <FindingCard key={x.rule_id} f={x} />)}
      </section>

      <section>
        <h3>Cross-source checks</h3>
        <div className="grid">
          {r.checks.map((c) => (
            <article key={c.name} className="card check">
              <header><b>{NAMES[c.name] || c.name}</b><span className={`pill st-${c.status}`}>{LABEL[c.status] || c.status}</span></header>
              <p>{c.details}</p>
              <small className="muted">{c.source} · {c.checked_at.replace("T", " ").slice(0, 19)} UTC</small>
            </article>
          ))}
        </div>
        {r.checks.some((c) => c.name === "url_reputation" && c.status !== "not_checked") && <small className="muted">URL advisory data: Google Safe Browsing. Potential risk only.</small>}
      </section>

      {chips.length > 0 && (
        <section>
          <h3>Extracted details</h3>
          <div className="chips2">{chips.map(([k, v], i) => <span key={i} className="chip2"><em>{k}</em> {v}</span>)}</div>
        </section>
      )}

      {r.missing_checks.length > 0 && (
        <details className="card"><summary>Not checked ({r.missing_checks.length})</summary><ul>{r.missing_checks.map((m, i) => <li key={i}>{m}</li>)}</ul></details>
      )}
      <details className="card"><summary>Limitations</summary><ul>{r.limitations.map((l, i) => <li key={i}>{l}</li>)}</ul></details>
    </div>
  );
}
