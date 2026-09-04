import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { casesAPI } from "../lib/api";

function Subscriptions() {
  const [cases, setCases] = useState<any[]>([]);
  const [showRetryable, setShowRetryable] = useState(false);
  useEffect(() => {
    casesAPI
      .getAll({ source_type: "SUBSCRIPTION" })
      .then((data) => setCases(Array.isArray(data) ? data : []))
      .catch(console.error);
  }, []);
  const visibleCases = cases.filter(
    (item) =>
      !showRetryable ||
      !["expired_card", "invalid_payment_method"].includes(item.root_cause),
  );
  return (
    <div className="space-y-6">
      <header>
        <p className="section-kicker">Recurring revenue / retention</p>
        <h1 className="mt-2 text-3xl font-semibold text-slate-950">
          Subscriptions
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Protect recurring revenue with bounded mandate retries and
          payment-method recovery.
        </p>
      </header>
      <section className="panel overflow-hidden p-0">
        <div className="flex flex-col gap-3 border-b border-slate-100 p-5 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="section-kicker">Subscription health</p>
            <h2 className="section-title">Failed recurring payments</h2>
          </div>
          <button
            onClick={() => setShowRetryable(!showRetryable)}
            className={`filter-button ${showRetryable ? "filter-button-active" : ""}`}
          >
            {showRetryable ? "Showing retryable" : "Show retryable only"}
          </button>
        </div>
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>Subscriber</th>
                <th>Failure</th>
                <th>Retry progress</th>
                <th>Status</th>
                <th>Amount</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {visibleCases.map((item) => (
                <tr key={item.id}>
                  <td>
                    <div className="table-person">
                      <div className="avatar avatar-mint">SU</div>
                      <div>
                        <Link
                          className="font-semibold text-slate-800 hover:text-teal-700"
                          to={`/cases/${item.id}`}
                        >
                          {item.customer_name}
                        </Link>
                        <p className="mt-1 text-xs text-slate-400">
                          {item.case_number} ·{" "}
                          {item.root_cause || "payment failure"}
                        </p>
                      </div>
                    </div>
                  </td>
                  <td className="muted-cell">
                    {item.root_cause || "payment failure"}
                  </td>
                  <td className="text-sm text-slate-500">
                    Attempt {item.current_retry_count || 0} /{" "}
                    {item.max_retries || 3}
                  </td>
                  <td>
                    <span className="status-chip status-chip-danger">
                      {item.status?.replaceAll("_", " ")}
                    </span>
                  </td>
                  <td className="font-semibold">
                    ₹
                    {Math.round(item.amount_at_risk || 0).toLocaleString(
                      "en-IN",
                    )}
                  </td>
                  <td>
                    <Link
                      className="font-semibold text-teal-700"
                      to={`/cases/${item.id}`}
                    >
                      Manage →
                    </Link>
                  </td>
                </tr>
              ))}
              {!cases.length && (
                <p className="p-5 text-sm text-slate-500">
                  No failed subscriptions in the current portfolio.
                </p>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
export default Subscriptions;
