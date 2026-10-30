export default function Explain({ data }) {
  if (!data?.en) return null;
  const d = data.en;
  return (
    <section className="card explain">
      <h3>In simple words</h3>
      <p className="lead">{d.summary}</p>
      {d.points.length > 0 && <ul>{d.points.map((p, i) => <li key={i}>{p}</li>)}</ul>}
      <b>What to do</b>
      <ul>{d.next.map((p, i) => <li key={i}>{p}</li>)}</ul>
    </section>
  );
}
