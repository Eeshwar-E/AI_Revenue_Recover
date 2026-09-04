import { useEffect, useState } from "react";
import { batchAPI, auditAPI } from "../lib/api";
function AgentRuns() {
  const [events, setEvents] = useState<any[]>([]);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [showRecovered, setShowRecovered] = useState(false);
  const load = () =>
    auditAPI
      .getAll({ limit: 50, offset: 0 })
      .then((data: any) => setEvents(data?.events || []))
      .catch(console.error);
  useEffect(() => {
    void load();
  }, []);
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
      <section className="agent-run-board panel">
        <div>
          <p className="section-kicker">Ready to execute</p>
          <h2 className="section-title">Bounded recovery workflow</h2>
          <p className="run-copy">
            The agent will process unresolved cases through deterministic policy
            gates and mock payment adapters.
          </p>
        </div>
        <div className="workflow-track">
          {["Detect", "Diagnose", "Decide", "Policy", "Execute", "Verify"].map(
            (step, index) => (
              <div className="workflow-node" key={step}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <b>{step}</b>
              </div>
            ),
          )}
        </div>
      </section>
      <section className="panel">
        <p className="section-kicker">Latest events</p>
        <h2 className="section-title">Decision stream</h2>
        <div className="mt-5 table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>Actor</th>
                <th>Event</th>
                <th>Result</th>
                <th>Recovered</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {events
                .filter(
                  (event) => !showRecovered || (event.recovery_amount || 0) > 0,
                )
                .map((event) => (
                  <tr key={event.id}>
                    <td>
                      <span className="status-pill">{event.actor}</span>
                    </td>
                    <td>
                      <b className="text-slate-800">
                        {event.event_type?.replaceAll("_", " ")}
                      </b>
                      <p className="mt-1 text-sm text-slate-500">
                        {event.details ||
                          event.action_result ||
                          "Event recorded by the recovery workflow"}
                      </p>
                    </td>
                    <td className="muted-cell">
                      {event.action_result || "Recorded"}
                    </td>
                    <td className="font-semibold text-emerald-700">
                      ₹
                      {Math.round(event.recovery_amount || 0).toLocaleString(
                        "en-IN",
                      )}
                    </td>
                    <td className="muted-cell">
                      {event.timestamp
                        ? new Date(event.timestamp).toLocaleString()
                        : ""}
                    </td>
                  </tr>
                ))}
              {!events.length && (
                <tr>
                  <td colSpan={5}>
                    <div className="run-empty">
                      <div className="run-empty-icon">✦</div>
                      <b>No agent run recorded yet</b>
                      <span>
                        Start a full recovery batch to populate this decision
                        stream.
                      </span>
                      <button
                        disabled={running}
                        onClick={run}
                        className="primary-button"
                      >
                        {running ? "Running batch..." : "Run first batch"}
                      </button>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <button
          onClick={() => setShowRecovered(!showRecovered)}
          className="filter-button mt-4"
        >
          {showRecovered ? "Show all events" : "Show recovered events only"}
        </button>
      </section>
    </div>
  );
}

export default AgentRuns;
