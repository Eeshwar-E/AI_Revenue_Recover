import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { casesAPI } from "../lib/api";

const formatMoney = (value: number) =>
  `₹${Math.round(value || 0).toLocaleString("en-IN")}`;
const statusClass = (status: string) =>
  status === "RECOVERED"
    ? "text-emerald-700 bg-emerald-50"
    : status === "ESCALATED"
      ? "text-rose-700 bg-rose-50"
      : "text-amber-700 bg-amber-50";

function Cases() {
  const [cases, setCases] = useState<any[]>([]);
  const [filter, setFilter] = useState("");
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    casesAPI
      .getAll(filter ? { status: filter } : undefined)
      .then((data) => setCases(Array.isArray(data) ? data : []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [filter]);
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
      <div className="panel overflow-hidden p-0">
        <div className="flex flex-col gap-3 border-b border-slate-100 p-5 sm:flex-row sm:items-center sm:justify-between">
          <div className="text-sm font-semibold text-slate-700">
            {cases.length} cases detected
          </div>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-600"
          >
            <option value="">All statuses</option>
            <option value="DETECTED">Detected</option>
            <option value="RECOVERED">Recovered</option>
            <option value="ESCALATED">Escalated</option>
            <option value="STOPPED">Stopped</option>
          </select>
        </div>
        {loading ? (
          <div className="p-8 text-sm text-slate-500">
            Loading risk portfolio...
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[720px] text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase tracking-wider text-slate-500">
                <tr>
                  <th className="px-5 py-3">Case</th>
                  <th className="px-5 py-3">Risk type</th>
                  <th className="px-5 py-3">Exposure</th>
                  <th className="px-5 py-3">Risk</th>
                  <th className="px-5 py-3">Status</th>
                  <th className="px-5 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {cases.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50">
                    <td className="px-5 py-4">
                      <Link
                        className="font-semibold text-slate-900 hover:text-teal-700"
                        to={`/cases/${item.id}`}
                      >
                        {item.customer_name}
                      </Link>
                      <div className="mt-1 text-xs text-slate-400">
                        {item.case_number}
                      </div>
                    </td>
                    <td className="px-5 py-4">
                      <span className="font-medium text-slate-700">
                        {String(item.source_type || "").replaceAll("_", " ")}
                      </span>
                      <div className="mt-1 text-xs text-slate-400">
                        {item.root_cause || "Awaiting diagnosis"}
                      </div>
                    </td>
                    <td className="px-5 py-4 font-semibold">
                      {formatMoney(item.amount_at_risk)}
                    </td>
                    <td className="px-5 py-4">
                      <span className="font-semibold">
                        {Math.round(item.risk_score || 0)}
                      </span>
                      <span className="ml-1 text-xs text-slate-400">/ 100</span>
                    </td>
                    <td className="px-5 py-4">
                      <span
                        className={`rounded-full px-2.5 py-1 text-xs font-semibold ${statusClass(item.status)}`}
                      >
                        {String(item.status || "").replaceAll("_", " ")}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-right">
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
      </div>
    </div>
  );
}

export default Cases;
