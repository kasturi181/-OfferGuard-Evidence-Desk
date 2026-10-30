import { useState } from "react";
import { reportScam } from "../api_extra";

const TYPES = ["Upfront fee", "OTP / credential theft", "Fake company", "Fake interview link", "Document harvesting", "Other"];

export default function ReportScamForm() {
  const [f, setF] = useState({ company_name: "", recruiter_domain: "", scam_type: TYPES[0], description: "" });
  const [state, setState] = useState({ busy: false, msg: "", ok: null });
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setState({ busy: true, msg: "", ok: null });
    try {
      const r = await reportScam(f);
      setState({ busy: false, msg: r.message, ok: r.saved });
      if (r.saved) setF({ ...f, company_name: "", recruiter_domain: "", description: "" });
    } catch {
      setState({ busy: false, ok: false, msg: "Could not reach the server. Report at cybercrime.gov.in or call 1930." });
    }
  }

  return (
    <section className="og-card og-narrow">
      <h2>Report a suspected scam</h2>
      <p className="og-muted">
        Do not include phone numbers or emails of people. Reports are anonymous and help other job seekers.
        This does not replace a police report: <a href="https://cybercrime.gov.in" target="_blank" rel="noreferrer">cybercrime.gov.in</a> · <b>1930</b>.
      </p>
      <form onSubmit={submit} className="og-form">
        <label>Company name<input value={f.company_name} onChange={set("company_name")} maxLength={120} /></label>
        <label>Recruiter email domain<input placeholder="example.com" value={f.recruiter_domain} onChange={set("recruiter_domain")} maxLength={120} /></label>
        <label>Type
          <select value={f.scam_type} onChange={set("scam_type")}>{TYPES.map((t) => <option key={t}>{t}</option>)}</select>
        </label>
        <label>What happened<textarea rows={4} value={f.description} onChange={set("description")} maxLength={1000} /></label>
        <button className="og-btn" disabled={state.busy}>{state.busy ? "Sending…" : "Submit report"}</button>
        {state.msg && <p role="status" className={state.ok ? "og-ok" : "og-warn"}>{state.msg}</p>}
      </form>
    </section>
  );
}
