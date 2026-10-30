const LEVELS = [["none", "No signals"], ["some", "Some signals"], ["elevated", "Elevated"], ["high", "High concern"]];

export default function RiskMeter({ a }) {
  const idx = LEVELS.findIndex(([k]) => k === a.level);
  return (
    <section className={`meter lvl-${a.level}`} aria-label="Risk indicator">
      <div className="meter-head">
        <h2>{LEVELS[idx][1]}</h2>
        <div className="counts">
          <span className="pill sev-strong">{a.counts.strong} strong</span>
          <span className="pill sev-medium">{a.counts.medium} medium</span>
          <span className="pill sev-weak">{a.counts.weak} weak</span>
        </div>
      </div>
      <div className="bar" role="img" aria-label={`Level ${a.level}`}>
        {LEVELS.map(([k], i) => <i key={k} className={i <= idx ? `on on-${a.level}` : ""} />)}
      </div>
      <p>{a.summary}</p>
      <small>{a.note}</small>
    </section>
  );
}
