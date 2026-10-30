import { useState } from "react";

function Draft({ d }) {
  const [done, setDone] = useState(false);
  const copy = async () => {
    try { await navigator.clipboard.writeText(d.text); }
    catch { const t = document.createElement("textarea"); t.value = d.text; document.body.appendChild(t); t.select(); document.execCommand("copy"); t.remove(); }
    setDone(true); setTimeout(() => setDone(false), 1500);
  };
  return (
    <article className="card draft">
      <header><b>{d.title}</b><button className="btn small noprint" onClick={copy}>{done ? "Copied ✓" : "Copy"}</button></header>
      <small className="muted">{d.hint}</small>
      <pre>{d.text}</pre>
    </article>
  );
}

export default function Drafts({ items }) {
  if (!items?.length) return null;
  return (
    <section>
      <h3>Ready-to-send messages</h3>
      <div className="grid">{items.map((d, i) => <Draft key={i} d={d} />)}</div>
    </section>
  );
}
