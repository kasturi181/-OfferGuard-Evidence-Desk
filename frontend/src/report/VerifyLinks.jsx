// "Verify it yourself in 60 seconds": one-click searches for everything we extracted.
// This turns "not checked" into action. These open other websites; we do not control their results.
const enc = encodeURIComponent;
const PERSONAL = ["gmail.com", "yahoo.com", "yahoo.in", "outlook.com", "hotmail.com", "rediffmail.com", "proton.me", "protonmail.com"];
const NEUTRAL = ["wa.me", "t.me", "bit.ly", "forms.gle", "docs.google.com", "linkedin.com", "naukri.com", "indeed.com"];

const google = (q) => `https://www.google.com/search?q=${enc(q)}`;

export default function VerifyLinks({ fields }) {
  const f = fields || {};
  const domains = [...new Set([
    ...(f.url_domains || []),
    ...(f.recruiter_emails || []).map((e) => e.split("@")[1]?.toLowerCase()),
  ])].filter((d) => d && !PERSONAL.includes(d) && !NEUTRAL.includes(d)).slice(0, 3);
  const emails = (f.recruiter_emails || []).slice(0, 2);
  const phones = (f.phones || []).slice(0, 2);

  const groups = [];
  if (f.company) {
    groups.push({ title: `Company: ${f.company}`, links: [
      ["Search for scam or fake-offer reports", google(`"${f.company}" fake job OR scam OR fraud`)],
      ["Find the real careers page", google(`${f.company} official careers`)],
      ["See the company on LinkedIn", `https://www.linkedin.com/search/results/companies/?keywords=${enc(f.company)}`],
      ["Check the office on Google Maps", `https://www.google.com/maps/search/${enc(f.company)}`],
      ["Look up registration on the MCA portal", "https://www.mca.gov.in"],
    ] });
  }
  domains.forEach((d) => groups.push({ title: `Website: ${d}`, links: [
    ["Google Safe Browsing status", `https://transparencyreport.google.com/safe-browsing/search?url=${enc(d)}`],
    ["Domain age and owner (WHOIS)", `https://who.is/whois/${enc(d)}`],
    ["Search for scam reports", google(`"${d}" scam OR fake OR fraud`)],
  ] }));
  emails.forEach((e) => groups.push({ title: `Email: ${e}`, links: [["Search for scam reports", google(`"${e}" scam OR fraud`)]] }));
  phones.forEach((p) => groups.push({ title: `Phone: ${p}`, links: [
    ["Search for scam reports", google(`"${p}" scam OR fraud`)],
    ["Look up on Truecaller", `https://www.truecaller.com/search/in/${enc(p)}`],
  ] }));
  groups.push({ title: "If you paid or shared details", links: [
    ["Report at cybercrime.gov.in", "https://cybercrime.gov.in"],
    ["Call the helpline 1930", "tel:1930"],
  ] });

  return (
    <section>
      <h3>Verify it yourself in 60 seconds</h3>
      <p className="muted">Checks we cannot do for you. One click each. These open other websites, and what they show is not proof either way.</p>
      <div className="grid">
        {groups.map((g) => (
          <article key={g.title} className="card verify">
            <b>{g.title}</b>
            <ul>{g.links.map(([label, href]) => (
              <li key={label}><a href={href} target="_blank" rel="noopener noreferrer">{label} ↗</a></li>
            ))}</ul>
          </article>
        ))}
      </div>
    </section>
  );
}
