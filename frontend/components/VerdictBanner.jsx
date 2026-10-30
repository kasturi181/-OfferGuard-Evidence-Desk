const TONE = {
  likely_fraudulent: { cls: "v-red", icon: "⚠️", title: "Likely fraudulent" },
  suspicious: { cls: "v-amber", icon: "🔎", title: "Suspicious" },
  low_risk: { cls: "v-blue", icon: "🛡️", title: "Low risk: no strong warning signs found" },
};

export default function VerdictBanner({ verdict }) {
  if (!verdict) return null;
  const t = TONE[verdict.verdict] || TONE.low_risk;
  const pct = Math.min(100, verdict.score || 0);
  return (
    <section className={`og-verdict ${t.cls}`} aria-live="polite">
      <div className="og-verdict-top">
        <span className="og-verdict-icon" aria-hidden>{t.icon}</span>
        <div>
          <h2>{t.title}</h2>
          <p>{verdict.summary}</p>
        </div>
      </div>

      <div className="og-meter" role="img" aria-label={`Warning-sign score ${pct} of 100`}>
        <div className="og-meter-bar" style={{ "--p": `${pct}%` }} />
        <div className="og-meter-scale"><span>0 · low</span><span>20 · suspicious</span><span>60 · likely fraud</span><span>100</span></div>
      </div>

      <div className="og-verdict-meta">
        <span>Confidence: <b>{verdict.confidence}</b></span>
        <span>Warning-sign score: <b>{verdict.score}/100</b></span>
        <span>Not a fraud probability</span>
      </div>

      {verdict.basis?.length > 0 && (
        <details className="og-why">
          <summary>How this was decided</summary>
          <ul>
            {verdict.basis.map((b, i) => (
              <li key={i}><span className={`og-dot sev-${b.severity}`} />{b.name} <small>({b.severity}, +{b.points})</small></li>
            ))}
          </ul>
          <small>Strong = 40, medium = 15, weak = 5, mismatch = 8. Any strong sign, or 60+, is “likely fraudulent”. 20+ is “suspicious”.</small>
        </details>
      )}
      <p className="og-disclaimer">{verdict.disclaimer}</p>
    </section>
  );
}
