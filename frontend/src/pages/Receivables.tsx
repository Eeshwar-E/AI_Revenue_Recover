import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { casesAPI } from "../lib/api";

function Receivables() {
  const [cases, setCases] = useState<any[]>([]);
  const [riskFilter, setRiskFilter] = useState("ALL");
  const [query, setQuery] = useState("");
  useEffect(() => {
    casesAPI
      .getAll({ source_type: "RECEIVABLE" })
      .then((data) => setCases(Array.isArray(data) ? data : []))
      .catch(console.error);
  }, []);
  const visibleCases = cases.filter(
    (item) =>
      (riskFilter === "ALL" || item.risk_level === riskFilter) &&
      `${item.customer_name} ${item.case_number}`
        .toLowerCase()
        .includes(query.toLowerCase()),
  );
  return (
    <div className="space-y-6">
      <header>
        <p className="section-kicker">Collections / B2B receivables</p>
        <h1 className="mt-2 text-3xl font-semibold text-slate-950">
          Receivables
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Overdue invoices are prioritized by risk, value, and recovery
          probability.
        </p>
      </header>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="metric-card">
          <p className="section-kicker">Open invoices</p>
          <p className="mt-2 text-2xl font-semibold">{cases.length}</p>
        </div>
        <div className="metric-card">
          <p className="section-kicker">Exposure</p>
          <p className="mt-2 text-2xl font-semibold">
            ₹
            {Math.round(
              cases.reduce((sum, item) => sum + (item.amount_at_risk || 0), 0),
            ).toLocaleString("en-IN")}
          </p>
        </div>
        <div className="metric-card">
          <p className="section-kicker">Escalation rule</p>
          <p className="mt-2 text-2xl font-semibold text-rose-700">30+ days</p>
        </div>
      </div>
      <section className="panel overflow-hidden p-0">
        <div className="flex flex-col gap-3 border-b border-slate-100 p-5 sm:flex-row sm:items-center sm:justify-between">
          <div className="text-sm font-semibold text-slate-700">
            Receivables intervention queue
          </div>
          <div className="flex flex-wrap gap-2">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search account"
              className="control-input"
            />
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="control-input"
            >
              <option value="ALL">All risk</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>
        </div>
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>Account / invoice</th>
                <th>Risk</th>
                <th>Amount at risk</th>
                <th>Root cause</th>
                <th>Next step</th>
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
                          className="font-semibold text-slate-800 hover:text-teal-700"
                          to={`/cases/${item.id}`}
                        >
                          {item.customer_name}
                        </Link>
                        <p className="mt-1 text-xs text-slate-400">
                          {item.case_number} ·{" "}
                          {item.root_cause || "invoice overdue"}
                        </p>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span className="risk-chip">{item.risk_level}</span>
                  </td>
                  <td className="font-semibold">
                    ₹
                    {Math.round(item.amount_at_risk || 0).toLocaleString(
                      "en-IN",
                    )}
                  </td>
                  <td className="muted-cell">
                    {item.root_cause || "invoice overdue"}
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
              {!visibleCases.length && (
                <p className="p-5 text-sm text-slate-500">
                  No receivables match this filter.
                </p>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
export default Receivables;
