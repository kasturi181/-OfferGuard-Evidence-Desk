import { useState } from "react";
import AnalyzeView from "./views/AnalyzeView.jsx";
import DashboardView from "./views/DashboardView.jsx";
import ReportView from "./views/ReportView.jsx";

const TABS = [["analyze", "Analyze"], ["dashboard", "Dashboard"], ["report", "Report a scam"]];

export default function App() {
  const [tab, setTab] = useState("analyze");
  return (
    <div className="app">
      <header className="top">
        <div className="brand"><span className="logo" aria-hidden>🛡️</span><div><b>OfferGuard</b><small>Evidence Desk</small></div></div>
        <nav>{TABS.map(([k, l]) => <button key={k} className={tab === k ? "tab on" : "tab"} onClick={() => setTab(k)}>{l}</button>)}</nav>
      </header>
      <main>
        <div hidden={tab !== "analyze"}><AnalyzeView /></div>
        {tab === "dashboard" && <DashboardView />}
        {tab === "report" && <ReportView />}
      </main>
      <footer>Decision support, not legal advice. Signals ≠ proof of fraud. Demo uses synthetic company records.</footer>
    </div>
  );
}
