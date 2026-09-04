import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { auditAPI } from "../lib/api";
function AuditTrail() {
  const [events, setEvents] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  useEffect(() => {
    auditAPI
      .getAll({ limit: 100, offset: 0 })
      .then((data: any) => {
        setEvents(data?.events || []);
        setTotal(data?.total || 0);
      })
      .catch(console.error);
  }, []);
  return (
    <div className="space-y-6">
      <header>
        <p className="section-kicker">Governance / immutable activity</p>
        <h1 className="mt-2 text-3xl font-semibold text-slate-950">
          Audit trail
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          A complete record of policy gates, actions, outcomes, and recovery
          amounts.
        </p>
      </header>
      <section className="panel overflow-hidden p-0">
        <div className="border-b border-slate-100 p-5 text-sm font-semibold text-slate-700">
          {total} events recorded
        </div>
        <div className="divide-y divide-slate-100">
          {events.map((event) => (
            <div
              key={event.id}
              className="grid gap-3 px-5 py-4 md:grid-cols-[120px_1fr_140px]"
            >
              <div>
                <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600">
                  {event.actor}
                </span>
                <p className="mt-2 text-xs text-slate-400">
                  {event.timestamp
                    ? new Date(event.timestamp).toLocaleString()
                    : ""}
                </p>
              </div>
              <div>
                <Link
                  to={event.case_id ? `/cases/${event.case_id}` : "/agent-runs"}
                  className="font-semibold text-slate-800 hover:text-teal-700"
                >
                  {event.event_type?.replaceAll("_", " ")}
                </Link>
                <p className="mt-1 text-sm text-slate-500">
                  {event.details ||
                    event.action_result ||
                    "No additional detail"}
                </p>
              </div>
              <div className="text-left font-semibold text-emerald-700 md:text-right">
                ₹
                {Math.round(event.recovery_amount || 0).toLocaleString("en-IN")}
              </div>
            </div>
          ))}
          {!events.length && (
            <p className="p-5 text-sm text-slate-500">
              The audit trail is empty.
            </p>
          )}
        </div>
      </section>
    </div>
  );
}

export default AuditTrail;
