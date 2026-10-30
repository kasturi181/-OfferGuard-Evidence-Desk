import { useEffect, useState } from "react";
import AuthBar from "./AuthBar.jsx";
import HistoryView from "./views/HistoryView.jsx";
import { watchSession } from "./auth.js";
import AnalyzeView from "./views/AnalyzeView.jsx";
import DashboardView from "./views/DashboardView.jsx";
import EvalView from "./views/EvalView.jsx";
import ReportView from "./views/ReportView.jsx";

const TABS = [["analyze", "Analyze"], ["dashboard", "Dashboard"], ["eval", "Evaluation"], ["report", "Report a scam"]];

export default function App() {
  const [tab, setTab] = useState("analyze");
  const [session, setSession] = useState(null);
  useEffect(() => watchSession(setSession), []);
  const tabs = session ? [...TABS, ["history", "My checks"]] : TABS;
  return (
    <div className="app">
      <header className="top">
        <div className="brand"><span className="logo" aria-hidden>🛡️</span><div><b>OfferGuard</b><small>Evidence Desk</small></div></div>
        <nav>{tabs.map(([k, l]) => <button key={k} className={tab === k ? "tab on" : "tab"} onClick={() => setTab(k)}>{l}</button>)}</nav>
        <AuthBar session={session} />
      </header>
      <main>
        <div hidden={tab !== "analyze"}><AnalyzeView /></div>
        {tab === "dashboard" && <DashboardView />}
        {tab === "eval" && <EvalView />}
        {tab === "report" && <ReportView />}
        {tab === "history" && session && <HistoryView />}
      </main>
      <footer>Decision support, not legal advice. Signals ≠ proof of fraud. Demo uses synthetic company records.</footer>
    </div>
  );
}
