export default function NavTabs({ page, setPage }) {
  const tabs = [
    ["check", "Check an offer"],
    ["dashboard", "Dashboard"],
    ["report", "Report a scam"],
  ];
  return (
    <header className="og-nav">
      <div className="og-brand">
        <span className="og-logo">🛡️</span>
        <div>
          <strong>OfferGuard</strong>
          <small>Evidence Desk</small>
        </div>
      </div>
      <nav role="tablist" aria-label="Sections">
        {tabs.map(([id, label]) => (
          <button key={id} role="tab" aria-selected={page === id}
            className={"og-tab" + (page === id ? " active" : "")}
            onClick={() => setPage(id)}>{label}</button>
        ))}
      </nav>
    </header>
  );
}
