import { useState } from "react";

export default function LoginModal({ onClose, onLogin }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  return (
    <div className="modal-bg" onClick={onClose} role="dialog" aria-modal="true" aria-label="Demo sign in">
      <form className="modal" onClick={(e) => e.stopPropagation()} onSubmit={(e) => { e.preventDefault(); onLogin(name, email); }}>
        <div className="eyebrow"><i className="dot" /> DEMO SIGN-IN</div>
        <h2>Welcome to OfferGuard</h2>
        <p className="muted">This is a <b>demo sign-in</b>: no password, no real account. Your name and a short list of past results (risk level only, never the offer text) stay in this browser.</p>
        <label>Name<input autoFocus value={name} onChange={(e) => setName(e.target.value)} placeholder="Your name" maxLength={40} /></label>
        <label>Email (optional)<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" maxLength={80} /></label>
        <div className="row"><button className="primary" type="submit">Continue</button><button type="button" className="ghost" onClick={onClose}>Cancel</button></div>
        <small className="muted">Real accounts (Supabase magic-link) are planned. See the supporting document.</small>
      </form>
    </div>
  );
}
