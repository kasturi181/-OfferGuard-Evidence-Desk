import { useEffect, useState } from "react";
import { getStats } from "../api.js";
import { sampleStats, RULE_NAMES } from "../fixtures/demoCases.js";

const LV = [["high", "High concern"], ["elevated", "Elevated"], ["some", "Some signals"], ["none", "No signals"]];

function Bars({ rows, max, cls = "" }) {
  return (
    <ul className="bars">
      {rows.map(([label, n]) => (
        <li key={label}><span>{label}</span><div><i className={cls} style={{ width: `${max ? Math.max(3, (n / max) * 100) : 0}%` }} /></div><b>{n}</b></li>
      ))}
    </ul>
  );
}

export default function DashboardView() {
  const [s, setS] = useState(null);
  const [note, setNote] = useState("");
  useEffect(() => {
    getStats().then((d) => { if (d.enabled) setS(d); else { setS({ ...sampleStats, companies_in_dataset: d.companies_in_dataset ?? 3 }); setNote("Database not connected. Showing SAMPLE numbers."); } })
      .catch(() => { setS(sampleStats); setNote("Backend unreachable. Showing SAMPLE numbers."); });
  }, []);
  if (!s) return <p className="muted">Loading dashboard…</p>;
  const highPct = s.total_analyses ? Math.round((s.by_level.high / s.total_analyses) * 100) : 0;
  const maxDay = Math.max(1, ...s.daily.map((d) => d.count));
  return (
    <>
      <section className="hero"><h1>Dashboard</h1><p className="muted">Aggregate view of analyses and user reports. No offer text is stored.</p></section>
      {note && <p className="banner warn">{note} Connect Supabase to see live data.</p>}
      <div className="tiles">
        <div className="tile"><b>{s.total_analyses}</b><span>analyses</span></div>
        <div className="tile"><b>{highPct}%</b><span>high concern</span></div>
        <div className="tile"><b>{s.scam_reports.total}</b><span>user reports (unverified)</span></div>
        <div className="tile"><b>{s.companies_in_dataset}</b><span>companies in dataset</span></div>
      </div>
      <div className="grid2">
        <section className="card"><h3>Risk levels</h3><Bars rows={LV.map(([k, l]) => [l, s.by_level[k]])} max={Math.max(1, ...Object.values(s.by_level))} cls="b-lvl" /></section>
        <section className="card"><h3>Most common signals</h3><Bars rows={s.top_rules.map((r) => [RULE_NAMES[r.rule_id] || r.rule_id, r.count])} max={Math.max(1, ...s.top_rules.map((r) => r.count))} /></section>
        <section className="card"><h3>Last 7 days</h3>
          <div className="spark">{s.daily.map((d, i) => <div key={i} title={`${d.date}: ${d.count}`}><i style={{ height: `${(d.count / maxDay) * 100}%` }} /><small>{d.date.slice(-2)}</small></div>)}</div>
        </section>
        <section className="card"><h3>Recent user reports</h3>
          {s.scam_reports.recent.length === 0 && <p className="muted">None yet.</p>}
          <ul className="reports">{s.scam_reports.recent.map((r, i) => <li key={i}><span className="pill">{r.kind}</span> <code>{r.value}</code><br /><small className="muted">{r.description} · {r.created_at}</small></li>)}</ul>
          <small className="muted">Reports are unverified and shown masked.</small>
        </section>
      </div>
    </>
  );
}
