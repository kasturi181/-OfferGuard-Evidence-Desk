import { useState } from "react";
import { submitReport } from "../api.js";

export default function ReportView() {
  const [kind, setKind] = useState("email");
  const [value, setValue] = useState("");
  const [description, setDescription] = useState("");
  const [ok, setOk] = useState(false);
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);

  const send = async () => {
    setBusy(true); setMsg("");
    try { const r = await submitReport({ kind, value, description }); setMsg(r.message); setValue(""); setDescription(""); }
    catch (e) { setMsg(e.message.includes("Failed to fetch") ? "Backend unreachable." : e.message); }
    setBusy(false);
  };
  return (
    <>
      <section className="hero"><h1>Report a suspicious offer</h1><p className="muted">Share an email, domain, company or phone number. When someone else analyses an offer with the same detail, OfferGuard shows a weak, unverified signal.</p></section>
      <section className="card form">
        <label>What are you reporting?
          <select value={kind} onChange={(e) => setKind(e.target.value)}>
            <option value="email">Recruiter email address</option><option value="domain">Website / domain</option>
            <option value="company">Company name</option><option value="phone">Phone number</option>
          </select>
        </label>
        <label>Value
          <input value={value} onChange={(e) => setValue(e.target.value)} placeholder={kind === "email" ? "hr@example.com" : kind === "domain" ? "example-jobs.com" : kind === "phone" ? "9876543210" : "Company name"} maxLength={200} />
        </label>
        <label>What happened? (optional)
          <textarea rows={3} value={description} onChange={(e) => setDescription(e.target.value)} maxLength={500} placeholder="e.g. Asked for a ₹2,000 registration fee" />
        </label>
        <label className="check-l"><input type="checkbox" checked={ok} onChange={(e) => setOk(e.target.checked)} /> I understand reports are stored as unverified and shown masked. I will not include personal details of other people.</label>
        <div className="row"><button className="primary" disabled={!ok || busy || value.trim().length < 3} onClick={send}>{busy ? "Sending…" : "Submit report"}</button></div>
        {msg && <p className="banner info">{msg}</p>}
      </section>
      <p className="muted">Do not report someone only because you dislike them. False reports can harm real people.</p>
    </>
  );
}
