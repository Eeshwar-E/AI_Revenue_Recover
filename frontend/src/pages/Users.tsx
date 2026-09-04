import { useState } from "react";

const users = [
  {
    initials: "AK",
    name: "Aarav Kapoor",
    email: "aarav@revenuerecover.ai",
    role: "Owner",
    access: "Full access",
    active: true,
    tone: "peach",
  },
  {
    initials: "NS",
    name: "Nisha Shah",
    email: "nisha@revenuerecover.ai",
    role: "Revenue operator",
    access: "Cases + runs",
    active: true,
    tone: "mint",
  },
  {
    initials: "RM",
    name: "Rohan Mehta",
    email: "rohan@revenuerecover.ai",
    role: "Risk analyst",
    access: "Read only",
    active: true,
    tone: "blue",
  },
  {
    initials: "SP",
    name: "Sana Pillai",
    email: "sana@revenuerecover.ai",
    role: "Finance reviewer",
    access: "Approvals",
    active: false,
    tone: "lavender",
  },
];

function Users() {
  const [inviteOpen, setInviteOpen] = useState(false);
  const [roleFilter, setRoleFilter] = useState("ALL");
  const [notice, setNotice] = useState("");
  const visibleUsers = users.filter(
    (user) => roleFilter === "ALL" || user.role === roleFilter,
  );
  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="section-kicker">Workspace / access control</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">
            Users & access
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Manage operators, approvals, and the people trusted with recovery
            workflows.
          </p>
        </div>
        <button
          className="primary-button"
          onClick={() => setInviteOpen(!inviteOpen)}
        >
          + Invite user
        </button>
      </header>
      {inviteOpen && (
        <div className="invite-banner">
          <div>
            <strong>Invite a teammate</strong>
            <p>
              New members start with read-only access until an owner approves
              their role.
            </p>
          </div>
          <button
            className="secondary-button"
            onClick={() => setInviteOpen(false)}
          >
            Close
          </button>
        </div>
      )}
      <div className="square-card-grid">
        <div className="metric-card square-card">
          <p className="section-kicker">Members</p>
          <p className="mt-2 text-2xl font-semibold">{users.length}</p>
          <p className="mt-1 text-xs text-slate-500">Across this workspace</p>
        </div>
        <div className="metric-card square-card">
          <p className="section-kicker">Active now</p>
          <p className="mt-2 text-2xl font-semibold text-teal-700">
            {users.filter((user) => user.active).length}
          </p>
          <p className="mt-1 text-xs text-slate-500">Verified operators</p>
        </div>
        <div className="metric-card square-card">
          <p className="section-kicker">Security posture</p>
          <p className="mt-2 text-2xl font-semibold text-emerald-700">Strong</p>
          <p className="mt-1 text-xs text-slate-500">MFA and policy gates on</p>
        </div>
        <div className="metric-card square-card">
          <p className="section-kicker">Approval guard</p>
          <p className="mt-2 text-2xl font-semibold text-slate-800">₹1L+</p>
          <p className="mt-1 text-xs text-slate-500">Manual review threshold</p>
        </div>
      </div>
      <section className="panel overflow-hidden p-0">
        <div className="border-b border-slate-100 p-5">
          <p className="section-kicker">Team directory</p>
          <h2 className="section-title">Workspace members</h2>
        </div>
        <div className="flex justify-end border-b border-slate-100 p-4">
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="control-input"
          >
            <option value="ALL">All roles</option>
            {Array.from(new Set(users.map((user) => user.role))).map((role) => (
              <option key={role} value={role}>
                {role}
              </option>
            ))}
          </select>
        </div>
        <div className="divide-y divide-slate-100">
          {visibleUsers.map((user) => (
            <div className="user-row" key={user.email}>
              <div className={`avatar avatar-${user.tone}`}>
                {user.initials}
              </div>
              <div className="min-w-0 flex-1">
                <p className="font-semibold text-slate-800">{user.name}</p>
                <p className="truncate text-sm text-slate-500">{user.email}</p>
              </div>
              <div className="hidden text-sm text-slate-600 md:block">
                {user.role}
              </div>
              <div className="hidden rounded-full bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-500 sm:block">
                {user.access}
              </div>
              <span
                className={`user-status ${user.active ? "user-status-active" : ""}`}
              >
                <i />
                {user.active ? "Active" : "Invited"}
              </span>
              <button
                className="row-action"
                aria-label={`Manage ${user.name}`}
                onClick={() =>
                  setNotice(
                    `${user.name}'s access controls are ready for review.`,
                  )
                }
              >
                •••
              </button>
            </div>
          ))}
        </div>
      </section>
      {notice && (
        <div className="notice-banner" role="status">
          {notice}
          <button onClick={() => setNotice("")}>Dismiss</button>
        </div>
      )}
      <section className="panel">
        <div className="flex items-start gap-3">
          <span className="security-icon">✓</span>
          <div>
            <p className="section-kicker">Security controls</p>
            <h2 className="section-title">Bounded autonomy is protected</h2>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
              Only approved operators can execute actions. Every recovery
              attempt is rate-limited, policy checked, and written to the audit
              trail.
            </p>
          </div>
        </div>
        <div className="security-grid">
          <span>✓ Role-based access</span>
          <span>✓ Manual approval above threshold</span>
          <span>✓ Two-factor authentication</span>
          <span>✓ Immutable audit events</span>
        </div>
      </section>
    </div>
  );
}

export default Users;
