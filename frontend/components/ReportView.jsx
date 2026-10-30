// Drop-in: <ReportView report={report} />  — renders the whole new report layout.
// Keep your existing input form and call setReport(response) as before.
import VerdictBanner from "./VerdictBanner";
import EvidenceCard from "./EvidenceCard";
import ConsistencyPanel from "./ConsistencyPanel";
import ChecklistPanel from "./ChecklistPanel";
import GuidancePanel from "./GuidancePanel";

const ORDER = { strong: 0, medium: 1, weak: 2, info: 3 };
const STATUS = { warning: "Warning", verified_match: "Match", no_match: "No match", unavailable: "Could not run", not_checked: "Not checked" };

export default function ReportView({ report }) {
  if (!report) return null;
  const findings = [...(report.findings || [])].sort(
    (a, b) => (ORDER[a.severity] ?? 3) - (ORDER[b.severity] ?? 3));
  const checks = report.checks || [];
  const notChecked = checks.filter((c) => c.status === "unavailable" || c.status === "not_checked");

  return (
    <div className="og-report">
      {report.mode && report.mode !== "full" && (
        <div className="og-banner-warn">Reduced mode ({report.mode}): some checks did not run. Treat this result with extra caution.</div>
      )}

      <VerdictBanner verdict={report.verdict_detail} />

      {report.ai_explanation && (
        <section className="og-card og-ai">
          <div className="og-card-head"><h3>In simple words</h3><span className="og-pill">AI-written explanation</span></div>
          <p>{report.ai_explanation}</p>
          <small className="og-muted">The AI only rewords the findings below. It does not decide the verdict.</small>
        </section>
      )}

      <section>
        <div className="og-section-title">
          <h3>Evidence ({findings.length})</h3>
          <span className="og-muted">Strongest first</span>
        </div>
        {findings.length === 0 && <div className="og-card og-muted">No warning signs matched. This is not proof the offer is genuine.</div>}
        <div className="og-ev-list">{findings.map((f, i) => <EvidenceCard key={i} f={f} />)}</div>
      </section>

      <ConsistencyPanel rows={report.consistency} />

      <section className="og-card">
        <div className="og-card-head"><h3>External checks</h3></div>
        <ul className="og-checks">
          {checks.map((c, i) => (
            <li key={i}>
              <span className={`og-badge cs-${c.status}`}>{STATUS[c.status] || c.status}</span>
              <b>{c.name || c.id}</b>
              <small>{c.detail}{c.source ? ` · ${c.source}` : ""}</small>
            </li>
          ))}
        </ul>
      </section>

      {notChecked.length > 0 && (
        <section className="og-card og-notchecked">
          <h3>Not checked</h3>
          <p className="og-muted">These were not verified. “Not checked” never means “safe”.</p>
          <ul>{report.missing_checks?.map((m, i) => <li key={i}>{m}</li>)}</ul>
        </section>
      )}

      <ChecklistPanel steps={report.checklist} />
      <GuidancePanel guidance={report.guidance} />

      {report.limitations?.length > 0 && (
        <details className="og-card"><summary>Limitations of this tool</summary>
          <ul>{report.limitations.map((l, i) => <li key={i}>{l}</li>)}</ul>
        </details>
      )}
    </div>
  );
}
