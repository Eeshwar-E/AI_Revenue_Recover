import { useState } from "react";
import { useLocation } from "react-router-dom";

const pageNames: Record<string, string> = {
  "/": "Overview",
  "/cases": "Revenue risks",
  "/agent-runs": "Agent runs",
  "/audit": "Audit trail",
  "/users": "Users & access",
  "/customers": "Customers",
  "/receivables": "Receivables",
  "/subscriptions": "Subscriptions",
};

function TopBar() {
  const location = useLocation();
  const [profileOpen, setProfileOpen] = useState(false);
  const pageName = location.pathname.startsWith("/cases/")
    ? "Case investigation"
    : pageNames[location.pathname] || "Operations";

  return (
    <header className="topbar">
      <div className="topbar-context">
        <span className="topbar-eyebrow">Operations console</span>
        <span className="topbar-divider">/</span>
        <span className="topbar-page">{pageName}</span>
      </div>
      <div className="topbar-actions">
        <label className="search-box">
          <span className="search-icon">⌕</span>
          <input aria-label="Search cases" placeholder="Search cases" />
          <kbd>⌘ K</kbd>
        </label>
        <div className="security-badge">
          <span className="shield">✓</span>
          <span>
            <b>Secure mode</b>
            <small>Policy gates active</small>
          </span>
        </div>
        <button className="icon-button" aria-label="Notifications">
          <span className="notification-dot" />◌
        </button>
        <div className="profile-wrap">
          <button
            className="profile-button"
            onClick={() => setProfileOpen(!profileOpen)}
            aria-expanded={profileOpen}
          >
            <span className="avatar">AK</span>
            <span className="profile-name">Aarav Kapoor</span>
            <span className="chevron">⌄</span>
          </button>
          {profileOpen && (
            <div className="profile-menu">
              <strong>Aarav Kapoor</strong>
              <span>Revenue operations</span>
              <hr />
              <button>Account settings</button>
              <button>Sign out</button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

export default TopBar;
