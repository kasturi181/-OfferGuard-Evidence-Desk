import { useEffect, useState } from "react";
import { getStats, getRecent } from "../api_extra";

const VERDICTS = { likely_fraudulent: "Likely fraudulent", suspicious: "Suspicious", low_risk: "Low risk" };

function Card({ label, value, hint, tone }) {
  return (
    <div className={`og-stat ${tone || ""}`}>
      <span>{label}</span><strong>{value}</strong>{hint && <small>{hint}</small>}
    </div>
  );
}

function Bars({ data }) {
  const max = Math.max(1, ...data.map((d) => d.count));
  return (
    <ul className="og-bars">
      {data.map((d) => (
        <li key={d.rule}>
          <span className="og-bar-label">{d.rule}</span>
          <span className="og-bar-track"><i style={{ width: `${(d.count / max) * 100}%` }} /></span>
          <b>{d.count}</b>
        </li>
      ))}
    </ul>
  );
}

function VerdictSplit({ v, total }) {
  const parts = [["likely_fraudulent", "v-red"], ["suspicious", "v-amber"], ["low_risk", "v-blue"]];
  return (
    <>
      <div className="og-split" role="img" aria-label="Verdict split">
        {parts.map(([k, c]) => <i key={k} className={c} style={{ width: `${total ? (v[k] / total) * 100 : 0}%` }} />)}
      </div>
      <ul className="og-legend">
        {parts.map(([k, c]) => <li key={k}><span className={`og-dotbox ${c}`} />{VERDICTS[k]} <b>{v[k]}</b></li>)}
      </ul>
    </>
  );
}

function Line({ data }) {
  const W = 560, H = 140, P = 8;
  const max = Math.max(1, ...data.map((d) => d.count));
  const x = (i) => P + (i * (W - 2 * P)) / Math.max(1, data.length - 1);
  const y = (c) => H - P - (c / max) * (H - 2 * P);
  const pts = data.map((d, i) => `${x(i)},${y(d.count)}`).join(" ");
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="og-line" role="img" aria-label="Checks per day">
      <polyline points={`${P},${H - P} ${pts} ${W - P},${H - P}`} className="og-area" />
      <polyline points={pts} className="og-stroke" fill="none" />
      {data.map((d, i) => <circle key={d.date} cx={x(i)} cy={y(d.count)} r="3"><title>{d.date}: {d.count}</title></circle>)}
    </svg>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [recent, setRecent] = useState({ items: [], sample: true });
  const [verdict, setVerdict] = useState("");
  const [err, setErr] = useState("");

  useEffect(() => { getStats().then(setStats).catch(() => setErr("Backend not reachable. Render may be waking up: open /health once, then refresh.")); }, []);
  useEffect(() => { getRecent(verdict).then(setRecent).catch(() => {}); }, [verdict]);

  if (err) return <section className="og-card og-warn">{err}</section>;
  if (!stats) return <section className="og-card">Loading dashboard…</section>;
  const pctUnv = stats.total ? Math.round((stats.with_unverified / stats.total) * 100) : 0;
  const v = stats.verdicts || { likely_fraudulent: 0, suspicious: 0, low_risk: 0 };

  return (
    <div className="og-dash">
      <div className="og-dash-head">
        <div>
          <h2>Institutional dashboard</h2>
          <p className="og-muted">Aggregate warning-sign patterns across checked offers. Not fraud verdicts about any company.</p>
        </div>
        {stats.sample && <span className="og-sample" title={stats.note}>Sample data · fictional</span>}
      </div>

      <div className="og-stats">
        <Card label="Offers checked" value={stats.total} />
        <Card label="Likely fraudulent" value={v.likely_fraudulent} tone="red" hint="any strong sign, or score 60+" />
        <Card label="Had unverified items" value={`${pctUnv}%`} tone="amber" hint="checks not run or not possible" />
        <Card label="Top signal" value={stats.top_rules[0]?.rule || "–"} tone="small" />
      </div>

      <div className="og-grid2">
        <section className="og-card"><h3>Verdict split</h3><VerdictSplit v={v} total={stats.total} /></section>
        <section className="og-card">
          <h3>Checks per day</h3><Line data={stats.per_day} />
          <div className="og-axis"><span>{stats.per_day[0]?.date}</span><span>{stats.per_day.at(-1)?.date}</span></div>
        </section>
      </div>

      <section className="og-card"><h3>Most triggered warning signs</h3><Bars data={stats.top_rules} /></section>

      <section className="og-card">
        <div className="og-card-head">
          <h3>Recent checks</h3>
          <select value={verdict} onChange={(e) => setVerdict(e.target.value)} aria-label="Filter by verdict">
            <option value="">All verdicts</option>
            {Object.entries(VERDICTS).map(([k, l]) => <option key={k} value={k}>{l}</option>)}
          </select>
        </div>
        <div className="og-table-wrap">
          <table className="og-table">
            <thead><tr><th>When</th><th>Verdict</th><th>Top signal</th><th>Domain</th></tr></thead>
            <tbody>
              {recent.items.map((r) => (
                <tr key={r.id}>
                  <td>{new Date(r.created_at).toLocaleString()}</td>
                  <td><span className={`og-lvl ${r.verdict === "likely_fraudulent" ? "lvl-high" : r.verdict === "suspicious" ? "lvl-elevated" : "lvl-some"}`}>{VERDICTS[r.verdict] || "–"}</span></td>
                  <td>{r.top_signal}</td>
                  <td><code>{r.domain || "–"}</code></td>
                </tr>
              ))}
              {!recent.items.length && <tr><td colSpan="4" className="og-muted">Nothing here yet.</td></tr>}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
