import { useEffect, useState } from "react";
import { getHealth } from "./api.js";
import { getUser, login, logout, addHistory } from "./auth.js";
import AnalyzeView from "./views/AnalyzeView.jsx";
import DashboardView from "./views/DashboardView.jsx";
import EvalView from "./views/EvalView.jsx";
import ReportView from "./views/ReportView.jsx";
import HistoryView from "./views/HistoryView.jsx";
import LoginModal from "./LoginModal.jsx";

export default function App() {
  const [tab, setTab] = useState("analyze");
  const [db, setDb] = useState(false);
  const [user, setUser] = useState(getUser());
  const [showLogin, setShowLogin] = useState(false);
  useEffect(() => { getHealth().then((h) => setDb(!!h.database)).catch(() => {}); }, []);
  const TABS = [["analyze", "Analyze"], ...(user ? [["history", "My checks"]] : []), ...(db ? [["dashboard", "Dashboard"]] : []), ["eval", "Evaluation"], ...(db ? [["report", "Report a scam"]] : [])];
  const initials = user ? user.name.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase() : "";
  return (
    <div className="app">
      <header className="top">
        <div className="brand"><span className="logo" aria-hidden>🛡️</span><div><b>OfferGuard</b><small className="mono">EVIDENCE DESK</small></div></div>
        <nav>
          {TABS.map(([k, l]) => <button key={k} className={tab === k ? "tab on" : "tab"} onClick={() => setTab(k)}>{l}</button>)}
          {user ? (
            <span className="who"><span className="avatar" title={user.name}>{initials}</span><button className="tab" onClick={() => { logout(); setUser(null); if (tab === "history") setTab("analyze"); }}>Sign out</button></span>
          ) : <button className="tab signin" onClick={() => setShowLogin(true)}>Sign in (demo)</button>}
        </nav>
      </header>
      <main>
        <div hidden={tab !== "analyze"}><AnalyzeView onReport={(r) => { if (getUser()) addHistory(r); }} /></div>
        {tab === "history" && user && <HistoryView user={user} />}
        {tab === "dashboard" && <DashboardView />}
        {tab === "eval" && <EvalView />}
        {tab === "report" && <ReportView />}
      </main>
      {showLogin && <LoginModal onClose={() => setShowLogin(false)} onLogin={(n, e) => { setUser(login(n, e)); setShowLogin(false); }} />}
      <footer>Decision support, not legal advice. Signals ≠ proof of fraud. Company records are a small synthetic sample. Sign-in is a demo (no real accounts).</footer>
    </div>
  );
}
