import { useState } from "react";
import { authEnabled, signInWithEmail, signOut } from "./auth.js";

export default function AuthBar({ session }) {
  const [open, setOpen] = useState(false);
  const [email, setEmail] = useState("");
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);
  if (!authEnabled) return null;

  if (session) {
    return (
      <div className="authbar">
        <small className="muted" title={session.user?.email}>{session.user?.email}</small>
        <button className="btn small" onClick={signOut}>Sign out</button>
      </div>
    );
  }
  const send = async (e) => {
    e.preventDefault(); setBusy(true); setMsg("");
    try { await signInWithEmail(email.trim()); setMsg("Check your email for the sign-in link."); }
    catch (err) { setMsg(err.message); }
    setBusy(false);
  };
  return (
    <div className="authbar">
      {!open ? <button className="btn small" onClick={() => setOpen(true)}>Sign in</button> : (
        <form onSubmit={send} className="authform">
          <input type="email" required placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} aria-label="Email address" />
          <button className="primary small" disabled={busy || !email}>{busy ? "…" : "Email me a link"}</button>
          {msg && <small className="muted">{msg}</small>}
        </form>
      )}
    </div>
  );
}
