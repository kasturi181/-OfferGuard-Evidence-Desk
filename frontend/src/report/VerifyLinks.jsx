// One-click independent checks. These open third-party sites; OfferGuard does not control their results.
const SKIP = new Set(["wa.me", "t.me", "bit.ly", "forms.gle", "docs.google.com"]);
const enc = encodeURIComponent;

export default function VerifyLinks({ fields }) {
  const f = fields || {};
  const doms = [...new Set([...(f.url_domains || []), ...(f.recruiter_emails || []).map((e) => e.split("@")[1]?.toLowerCase())])]
    .filter((d) => d && !SKIP.has(d) && !["gmail.com", "yahoo.com", "yahoo.in", "outlook.com", "hotmail.com", "rediffmail.com"].includes(d)).slice(0, 3);
  const cins = f.registration_ids || [];
  if (!doms.length && !f.company && !cins.length) return null;
  return (
    <section>
      <h3>Confirm it yourself in 60 seconds</h3>
      <p className="muted">OfferGuard can show evidence but cannot declare a site or company "genuine". These independent sources can help you decide. Open them in a new tab.</p>
      <div className="grid">
        {doms.map((d) => (
          <article className="card check" key={d}>
            <header><b>{d}</b><span className="pill">website</span></header>
            <ul className="vl">
              <li><a href={`https://transparencyreport.google.com/safe-browsing/search?url=${enc(d)}`} target="_blank" rel="noreferrer noopener">Google Safe Browsing status</a></li>
              <li><a href={`https://lookup.icann.org/en/lookup?name=${enc(d)}`} target="_blank" rel="noreferrer noopener">Who owns it and when it was registered (ICANN)</a></li>
              <li><a href={`https://www.google.com/search?q=${enc(`"${d}" scam OR fraud OR reviews`)}`} target="_blank" rel="noreferrer noopener">Search "{d}" scam reports</a></li>
              <li><a href={`https://web.archive.org/web/*/${enc(d)}`} target="_blank" rel="noreferrer noopener">Website history (Internet Archive)</a></li>
            </ul>
          </article>
        ))}
        {(f.company || cins.length > 0) && (
          <article className="card check">
            <header><b>{f.company || "Company"}</b><span className="pill">company</span></header>
            <ul className="vl">
              <li><a href="https://www.mca.gov.in/content/mca/global/en/mca/master-data/MDS.html" target="_blank" rel="noreferrer noopener">MCA Company master data{cins[0] ? ` (search ${cins[0]})` : ""}</a></li>
              {f.company && <li><a href={`https://www.linkedin.com/search/results/companies/?keywords=${enc(f.company)}`} target="_blank" rel="noreferrer noopener">LinkedIn company page</a></li>}
              {f.company && <li><a href={`https://www.google.com/search?q=${enc(`"${f.company}" fake job scam`)}`} target="_blank" rel="noreferrer noopener">Search "{f.company}" scam reports</a></li>}
              <li><a href="https://cybercrime.gov.in" target="_blank" rel="noreferrer noopener">Report at cybercrime.gov.in (helpline 1930)</a></li>
            </ul>
          </article>
        )}
      </div>
    </section>
  );
}
