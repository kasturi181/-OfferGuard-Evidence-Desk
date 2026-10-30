import { useEffect, useState } from "react";
import { getHealth } from "./api.js";
import AnalyzeView from "./views/AnalyzeView.jsx";
import DashboardView from "./views/DashboardView.jsx";
import EvalView from "./views/EvalView.jsx";
import ReportView from "./views/ReportView.jsx";

const BASE_TABS = [["analyze", "Analyze"], ["eval", "Evaluation"]];
const DB_TABS = [["dashboard", "Dashboard"], ["report", "Report a scam"]];

export default function App() {
  const [tab, setTab] = useState("analyze");
  const [db, setDb] = useState(false);
  useEffect(() => { getHealth().then((h) => setDb(!!h.database)).catch(() => {}); }, []);
  const TABS = db ? [...BASE_TABS.slice(0, 1), ...DB_TABS.slice(0, 1), BASE_TABS[1], DB_TABS[1]] : BASE_TABS;
  return (
    <div className="app">
      <header className="top">
        <div className="brand"><span className="logo" aria-hidden>🛡️</span><div><b>OfferGuard</b><small>Evidence Desk</small></div></div>
        <nav>{TABS.map(([k, l]) => <button key={k} className={tab === k ? "tab on" : "tab"} onClick={() => setTab(k)}>{l}</button>)}</nav>
      </header>
      <main>
        <div hidden={tab !== "analyze"}><AnalyzeView /></div>
        {tab === "dashboard" && <DashboardView />}
        {tab === "eval" && <EvalView />}
        {tab === "report" && <ReportView />}
      </main>
      <footer>Decision support, not legal advice. Signals ≠ proof of fraud. Company records are a small synthetic sample.</footer>
    </div>
  );
}
