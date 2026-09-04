import { useEffect, useState } from "react";
import { batchAPI, auditAPI } from "../lib/api";
function AgentRuns() {
  const [events, setEvents] = useState<any[]>([]);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const load = () =>
    auditAPI
      .getAll({ limit: 50, offset: 0 })
      .then((data: any) => setEvents(data?.events || []))
      .catch(console.error);
  useEffect(load, []);
  const run = async () => {
    setRunning(true);
    try {
      setResult(await batchAPI.run());
      await load();
    } catch (e) {
      console.error(e);
    } finally {
      setRunning(false);
    }
  };
  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="section-kicker">
            Autonomous operations / batch control
          </p>
          <h1 className="mt-2 text-3xl font-semibold text-slate-950">
            Agent runs
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Observe every detect, decide, act, verify, and stop transition.
          </p>
        </div>
        <button
          disabled={running}
          onClick={run}
          className="rounded-lg bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white"
        >
          {running ? "Running batch..." : "Run full batch"}
        </button>
      </header>
      {result && (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <div className="metric-card">
            <p className="section-kicker">Processed</p>
            <p className="mt-2 text-2xl font-semibold">
              {result.cases_processed || 0}
            </p>
          </div>
          <div className="metric-card">
            <p className="section-kicker">Recovered</p>
            <p className="mt-2 text-2xl font-semibold text-emerald-700">
              ₹
              {Math.round(result.recovered_amount || 0).toLocaleString("en-IN")}
            </p>
          </div>
          <div className="metric-card">
            <p className="section-kicker">Rate</p>
            <p className="mt-2 text-2xl font-semibold">
              {result.recovery_rate || 0}%
            </p>
          </div>
          <div className="metric-card">
            <p className="section-kicker">Batch</p>
            <p className="mt-2 text-2xl font-semibold">
              #{result.batch_id || "new"}
            </p>
          </div>
        </div>
      )}
      <section className="panel">
        <p className="section-kicker">Latest events</p>
        <h2 className="section-title">Decision stream</h2>
        <div className="mt-5 divide-y divide-slate-100">
          {events.map((event) => (
            <div
              key={event.id}
              className="flex flex-col gap-2 py-4 sm:flex-row sm:items-center sm:justify-between"
            >
              <div>
                <span className="mr-2 rounded-full bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600">
                  {event.actor}
                </span>
                <span className="font-semibold text-slate-800">
                  {event.event_type?.replaceAll("_", " ")}
                </span>
                <p className="mt-2 text-sm text-slate-500">
                  {event.details ||
                    event.action_result ||
                    "Event recorded by the recovery workflow"}
                </p>
              </div>
              <div className="text-right text-sm">
                <div className="font-semibold text-emerald-700">
                  ₹
                  {Math.round(event.recovery_amount || 0).toLocaleString(
                    "en-IN",
                  )}
                </div>
                <div className="mt-1 text-xs text-slate-400">
                  {event.timestamp
                    ? new Date(event.timestamp).toLocaleString()
                    : ""}
                </div>
              </div>
            </div>
          ))}
          {!events.length && (
            <p className="py-5 text-sm text-slate-500">No runs recorded yet.</p>
          )}
        </div>
      </section>
    </div>
  );
}

export default AgentRuns;
