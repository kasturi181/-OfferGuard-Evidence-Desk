const LEVELS = [["none", "No signals"], ["some", "Some signals"], ["elevated", "Elevated"], ["high", "High concern"]];
const VERDICT = {
  high: ["⛔", "HIGH RISK", "Do not pay or share anything until you verify this employer."],
  elevated: ["⚠️", "ELEVATED RISK", "Several warning signs. Verify the company before you act."],
  some: ["🔶", "SOME WARNING SIGNS", "Check the flagged items before you continue."],
  none: ["🔍", "NO WARNING SIGNS FOUND", "That is not proof the offer is genuine. Still verify the company yourself."],
};

export default function RiskMeter({ a }) {
  const idx = LEVELS.findIndex(([k]) => k === a.level);
  const [icon, head, sub] = VERDICT[a.level] || VERDICT.none;
  return (
    <section className={`meter lvl-${a.level}`} aria-label="Risk indicator">
      <div className="verdict">
        <span className="v-icon" aria-hidden>{icon}</span>
        <div><div className="v-head">{head}</div><div className="v-sub">{sub}</div></div>
      </div>
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
