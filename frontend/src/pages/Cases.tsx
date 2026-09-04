import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { casesAPI } from "../lib/api";

const formatMoney = (value: number) =>
  `₹${Math.round(value || 0).toLocaleString("en-IN")}`;
const statusClass = (status: string) =>
  status === "RECOVERED"
    ? "status-chip status-chip-success"
    : status === "ESCALATED"
      ? "status-chip status-chip-danger"
      : status === "STOPPED"
        ? "status-chip status-chip-muted"
        : "risk-chip";

function Cases() {
  const [cases, setCases] = useState<any[]>([]);
  const [filter, setFilter] = useState("");
  const [query, setQuery] = useState("");
  const [sortHighRisk, setSortHighRisk] = useState(false);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    casesAPI
      .getAll(filter ? { status: filter } : undefined)
      .then((data) => setCases(Array.isArray(data) ? data : []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [filter]);
  const visibleCases = cases
    .filter((item) =>
      `${item.customer_name} ${item.case_number} ${item.root_cause} ${item.source_type}`
        .toLowerCase()
        .includes(query.toLowerCase()),
    )
    .sort((a, b) =>
      sortHighRisk ? (b.risk_score || 0) - (a.risk_score || 0) : 0,
    );
  const exposure = cases.reduce(
    (total, item) => total + (item.amount_at_risk || 0),
    0,
  );
  const recovered = cases.reduce(
    (total, item) => total + (item.recovered_amount || 0),
    0,
  );
  const needsAttention = cases.filter((item) =>
    ["ESCALATED", "MANUAL_REVIEW"].includes(item.status),
  ).length;
  return (
    <div className="space-y-6">
      <header>
        <p className="section-kicker">Portfolio / intervention queue</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">
          Revenue risks
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Every case has a reason, a bounded action, and a measurable outcome.
        </p>
      </header>
      <div className="square-card-grid case-summary-grid">
        <div className="metric-card">
          <p className="section-kicker">Total exposure</p>
          <p className="mt-2 text-2xl font-semibold">{formatMoney(exposure)}</p>
          <p className="mt-1 text-xs text-slate-500">
            Across {cases.length} detected cases
          </p>
        </div>
        <div className="metric-card">
          <p className="section-kicker">Recovered</p>
          <p className="mt-2 text-2xl font-semibold text-teal-700">
            {formatMoney(recovered)}
          </p>
          <p className="mt-1 text-xs text-slate-500">Verified recovery value</p>
        </div>
        <div className="metric-card">
          <p className="section-kicker">Needs attention</p>
          <p className="mt-2 text-2xl font-semibold text-rose-700">
            {needsAttention}
          </p>
          <p className="mt-1 text-xs text-slate-500">
            Escalated or manual review
          </p>
        </div>
        <div className="metric-card">
          <p className="section-kicker">Highest risk</p>
          <p className="mt-2 text-2xl font-semibold text-amber-700">
            {Math.round(
              Math.max(0, ...cases.map((item) => item.risk_score || 0)),
            )}
            /100
          </p>
          <p className="mt-1 text-xs text-slate-500">Priority score</p>
        </div>
      </div>
      <div className="panel overflow-hidden p-0">
        <div className="flex flex-col gap-3 border-b border-slate-100 p-5 sm:flex-row sm:items-center sm:justify-between">
          <div className="text-sm font-semibold text-slate-700">
            {visibleCases.length} of {cases.length} cases detected
          </div>
          <div className="flex flex-wrap gap-2">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search customer or case"
              className="control-input"
            />
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="control-input"
            >
              <option value="">All statuses</option>
              <option value="DETECTED">Detected</option>
              <option value="RECOVERED">Recovered</option>
              <option value="ESCALATED">Escalated</option>
              <option value="STOPPED">Stopped</option>
            </select>
            <button
              onClick={() => setSortHighRisk(!sortHighRisk)}
              className={`filter-button ${sortHighRisk ? "filter-button-active" : ""}`}
            >
              Highest risk
            </button>
          </div>
        </div>
        {loading ? (
          <div className="p-8 text-sm text-slate-500">
            Loading risk portfolio...
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="data-table cases-table">
              <thead>
                <tr>
                  <th>Case / customer</th>
                  <th>Risk type</th>
                  <th>Amount at risk</th>
                  <th>Risk score</th>
                  <th>Attempts</th>
                  <th>Status</th>
                  <th>Recovered</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {visibleCases.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <div className="table-person">
                        <span className="table-index">
                          {String(item.case_number || "CASE").replace(
                            "CASE-",
                            "",
                          )}
                        </span>
                        <div>
                          <Link
                            className="font-semibold text-slate-900 hover:text-teal-700"
                            to={`/cases/${item.id}`}
                          >
                            {item.customer_name}
                          </Link>
                          <div className="mt-1 text-xs text-slate-400">
                            {item.case_number}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className="font-medium text-slate-700">
                        {String(item.source_type || "").replaceAll("_", " ")}
                      </span>
                      <div className="mt-1 text-xs text-slate-400">
                        {item.root_cause || "Awaiting diagnosis"}
                      </div>
                    </td>
                    <td className="font-semibold">
                      {formatMoney(item.amount_at_risk)}
                    </td>
                    <td>
                      <span className="font-semibold">
                        {Math.round(item.risk_score || 0)}
                      </span>
                      <span className="ml-1 text-xs text-slate-400">/ 100</span>
                    </td>
                    <td className="muted-cell">
                      {item.current_retry_count || 0} / {item.max_retries || 3}
                    </td>
                    <td>
                      <span className={statusClass(item.status)}>
                        {String(item.status || "").replaceAll("_", " ")}
                      </span>
                    </td>
                    <td className="font-semibold text-teal-700">
                      {formatMoney(item.recovered_amount)}
                    </td>
                    <td>
                      <Link
                        className="font-semibold text-teal-700"
                        to={`/cases/${item.id}`}
                      >
                        Review →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {!loading && !visibleCases.length && (
          <div className="empty-state table-empty">
            No cases match this view.
          </div>
        )}
      </div>
    </div>
  );
}

export default Cases;
