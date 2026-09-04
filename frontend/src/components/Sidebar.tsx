import { Link, useLocation } from "react-router-dom";

function Sidebar() {
  const location = useLocation();
  const links = [
    { href: "/", label: "Overview" },
    { href: "/cases", label: "Revenue risks" },
    { href: "/customers", label: "Customers" },
    { href: "/receivables", label: "Receivables" },
    { href: "/subscriptions", label: "Subscriptions" },
    { href: "/agent-runs", label: "Agent runs" },
    { href: "/audit", label: "Audit trail" },
    { href: "/users", label: "Users & access" },
  ];

  return (
    <nav className="sidebar">
      <Link to="/" className="brand">
        <span className="brand-mark">R</span>
        <span>
          RevenueRecover <b>AI</b>
        </span>
      </Link>
      <div className="sidebar-label">Workspace</div>
      <ul className="space-y-1">
        {links.map((link) => (
          <li key={link.href}>
            <Link
              to={link.href}
              className={`nav-link ${location.pathname === link.href || (link.href === "/cases" && location.pathname.startsWith("/cases/")) ? "nav-link-active" : ""}`}
            >
              {link.label}
            </Link>
          </li>
        ))}
      </ul>
      <div className="sidebar-divider" />
      <div className="sidebar-label">Guardrails</div>
      <div className="guardrail-list">
        <div>
          <span className="guardrail-check">✓</span> Max 3 attempts
        </div>
        <div>
          <span className="guardrail-check">✓</span> Human approval enabled
        </div>
        <div>
          <span className="guardrail-check">✓</span> Contact limits active
        </div>
      </div>
      <div className="sidebar-foot">
        <span className="live-dot" /> Mock gateway connected
        <span className="mt-1 block text-xs text-slate-500">
          Safe mode · bounded actions
        </span>
      </div>
    </nav>
  );
}

export default Sidebar;
