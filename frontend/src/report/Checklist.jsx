import { useState } from "react";

export default function Checklist({ items }) {
  const [done, setDone] = useState({});
  if (!items?.length) return null;
  return (
    <section>
      <h3>What to do next</h3>
      <div className="grid">
        {items.map((it, i) => (
          <article key={i} className={`card step ${it.tied_to ? "tied" : ""}`}>
            <header><b>{it.title}</b>{it.tied_to && <span className="pill">{it.tied_to}</span>}</header>
            <ul className="todo">
              {it.steps.map((s, j) => {
                const k = `${i}-${j}`;
                return (
                  <li key={k}>
                    <label><input type="checkbox" checked={!!done[k]} onChange={() => setDone({ ...done, [k]: !done[k] })} /> <span className={done[k] ? "struck" : ""}>{s}</span></label>
                  </li>
                );
              })}
            </ul>
          </article>
        ))}
      </div>
    </section>
  );
}
