import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { agentAPI, casesAPI } from "../lib/api";

function CaseDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [item, setItem] = useState<any>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const load = () =>
    id && casesAPI.getDetail(id).then(setItem).catch(console.error);
  useEffect(load, [id]);
  const execute = async (action: () => Promise<any>, label: string) => {
    setBusy(true);
    setMessage("");
    try {
      await action();
      setMessage(`${label} completed.`);
      load();
    } catch (error: any) {
      setMessage(error?.response?.data?.detail || `${label} failed.`);
    } finally {
      setBusy(false);
    }
  };
  if (!item)
    return <div className="text-sm text-slate-500">Loading case...</div>;
  return (
    <div className="space-y-6">
      <Link to="/cases" className="text-sm font-semibold text-teal-700">
        ← Back to risk portfolio
      </Link>
      <header className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="section-kicker">
            {item.case_number} / case investigation
          </p>
          <h1 className="mt-2 text-3xl font-semibold text-slate-950">
            {item.customer_name}
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            {item.source_type?.replaceAll("_", " ")} ·{" "}
            {item.customer_segment || "Standard segment"}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            disabled={busy}
            onClick={() => execute(() => agentAPI.analyze(id!), "Analysis")}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700"
          >
            Analyze
          </button>
          <button
            disabled={busy}
            onClick={() => execute(() => casesAPI.runCase(id!), "Recovery run")}
            className="rounded-lg bg-slate-950 px-3 py-2 text-sm font-semibold text-white"
          >
            Run recovery
          </button>
          {item.status !== "STOPPED" && item.status !== "RECOVERED" && (
            <button
              disabled={busy}
              onClick={() => execute(() => casesAPI.stop(id!), "Stop")}
              className="rounded-lg border border-rose-200 px-3 py-2 text-sm font-semibold text-rose-700"
            >
              Stop
            </button>
          )}
        </div>
      </header>
      {message && (
        <div className="rounded-lg bg-teal-50 px-4 py-3 text-sm font-medium text-teal-800">
          {message}
        </div>
      )}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <section className="panel lg:col-span-2">
          <div className="grid grid-cols-2 gap-5 sm:grid-cols-4">
            <div>
              <p className="section-kicker">At risk</p>
              <p className="mt-2 text-xl font-semibold">
                ₹{Math.round(item.amount_at_risk || 0).toLocaleString("en-IN")}
              </p>
            </div>
            <div>
              <p className="section-kicker">Recovered</p>
              <p className="mt-2 text-xl font-semibold text-emerald-700">
                ₹
                {Math.round(item.recovered_amount || 0).toLocaleString("en-IN")}
              </p>
            </div>
            <div>
              <p className="section-kicker">Risk score</p>
              <p className="mt-2 text-xl font-semibold">
                {Math.round(item.risk_score || 0)}
                <small className="text-sm text-slate-400"> / 100</small>
              </p>
            </div>
            <div>
              <p className="section-kicker">Attempts</p>
              <p className="mt-2 text-xl font-semibold">
                {item.current_retry_count || 0}
                <small className="text-sm text-slate-400">
                  {" "}
                  / {item.max_retries || 3}
                </small>
              </p>
            </div>
          </div>
          <div className="mt-8 border-t border-slate-100 pt-6">
            <p className="section-kicker">Agent reasoning</p>
            <h2 className="section-title">
              {item.root_cause || "Diagnosis pending"}
            </h2>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              {item.action_reasoning ||
                "Run analysis to classify the root cause and recommend a safe intervention."}
            </p>
            <div className="mt-5 rounded-lg bg-slate-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Recommended action
              </p>
              <p className="mt-2 font-semibold text-slate-800">
                {item.recommended_action || "Awaiting agent decision"}
              </p>
            </div>
          </div>
        </section>
        <section className="panel">
          <p className="section-kicker">Customer profile</p>
          <h2 className="section-title">Account context</h2>
          <dl className="mt-5 space-y-4 text-sm">
            <div>
              <dt className="text-slate-400">Email</dt>
              <dd className="mt-1 font-medium">
                {item.customer_email || "Not available"}
              </dd>
            </div>
            <div>
              <dt className="text-slate-400">Historical success</dt>
              <dd className="mt-1 font-medium">
                {Math.round((item.historical_success_rate || 0) * 100)}%
              </dd>
            </div>
            <div>
              <dt className="text-slate-400">Recent success</dt>
              <dd className="mt-1 font-medium">
                {Math.round((item.recent_success_rate || 0) * 100)}%
              </dd>
            </div>
            <div>
              <dt className="text-slate-400">Workflow status</dt>
              <dd className="mt-1 font-semibold text-teal-700">
                {item.status?.replaceAll("_", " ")}
              </dd>
            </div>
          </dl>
        </section>
      </div>
      <section className="panel">
        <p className="section-kicker">Execution log</p>
        <h2 className="section-title">Actions and audit events</h2>
        <div className="mt-5 divide-y divide-slate-100">
          {[...(item.audit_events || [])].reverse().map((event: any) => (
            <div
              key={event.id}
              className="flex flex-col gap-1 py-4 sm:flex-row sm:items-start sm:justify-between"
            >
              <div>
                <p className="font-semibold text-slate-800">
                  {event.event_type?.replaceAll("_", " ")}
                </p>
                <p className="mt-1 text-sm text-slate-500">
                  {event.details ||
                    event.action_result ||
                    "Workflow event recorded"}
                </p>
              </div>
              <time className="text-xs text-slate-400">
                {event.timestamp
                  ? new Date(event.timestamp).toLocaleString()
                  : "Just now"}
              </time>
            </div>
          ))}
          {!(item.audit_events || []).length && (
            <p className="py-4 text-sm text-slate-500">
              No actions recorded yet.
            </p>
          )}
        </div>
      </section>
    </div>
  );
}

export default CaseDetail;
