export default function HighlightedText({ text, findings }) {
  const spans = findings.filter((f) => f.start != null && f.end != null && f.end <= text.length).sort((a, b) => a.start - b.start);
  const parts = [];
  let pos = 0;
  for (const f of spans) {
    if (f.start < pos) continue;
    if (f.start > pos) parts.push(text.slice(pos, f.start));
    parts.push(
      <mark key={f.rule_id} className={`hl hl-${f.severity}`} title={`${f.rule_id}: ${f.title}`}>
        {text.slice(f.start, f.end)}<sup>{f.rule_id.replace("RULE-", "")}</sup>
      </mark>
    );
    pos = f.end;
  }
  parts.push(text.slice(pos));
  return <div className="msg">{parts}</div>;
}
