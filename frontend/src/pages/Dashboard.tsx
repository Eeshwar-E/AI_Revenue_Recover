import { useEffect, useState } from "react";
import {
  batchAPI,
  getSummary,
  getRecovery,
  getRiskDistribution,
  getFunnel,
  getFailureReasons,
} from "../lib/api";
import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const normalizeList = (value: unknown): any[] => {
  if (Array.isArray(value)) return value;
  if (value && typeof value === "object") {
    const objectValue = value as Record<string, unknown>;
    if (Array.isArray(objectValue.items)) return objectValue.items as any[];
    if (Array.isArray(objectValue.value)) return objectValue.value as any[];
    if (Array.isArray(objectValue.data)) return objectValue.data as any[];
  }
  return [];
};

function Dashboard() {
  const [summary, setSummary] = useState<Record<string, any>>({});
  const [recoveryByType, setRecoveryByType] = useState<any[]>([]);
  const [riskDist, setRiskDist] = useState<any[]>([]);
  const [funnel, setFunnel] = useState<any[]>([]);
  const [failureReasons, setFailureReasons] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [s, r, risk, funnelData, reasons] = await Promise.all([
          getSummary(),
          getRecovery(),
          getRiskDistribution(),
          getFunnel(),
          getFailureReasons(),
        ]);

        setSummary(s ?? {});
        setRecoveryByType(normalizeList(r));
        setRiskDist(normalizeList(risk));
        setFunnel(normalizeList(funnelData));
        setFailureReasons(normalizeList(reasons));
      } catch (e) {
        console.error("Dashboard data load failed:", e);
        setSummary({});
        setRecoveryByType([]);
        setRiskDist([]);
        setFunnel([]);
        setFailureReasons([]);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const failureReasonItems = normalizeList(failureReasons);
  const recoveryItems = normalizeList(recoveryByType);
  const funnelItems = normalizeList(funnel);
  const chartRecovery = recoveryItems.map((item) => ({
    ...item,
    label: String(item.type || "Other").replaceAll("_", " "),
  }));
  const chartRisk = riskDist.map((item) => ({
    ...item,
    name: item.risk_level || "Unknown",
  }));

  const runBatch = async () => {
    setLoading(true);
    try {
      await batchAPI.run();
      window.location.reload();
    } catch (error) {
      console.error("Batch run failed:", error);
      setLoading(false);
    }
  };

  if (loading)
    return (
      <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
    );

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-4 border-b border-slate-200 pb-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal-600">
            Control room / live portfolio
          </p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">
            Revenue recovery overview
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Detect leakage, deploy bounded interventions, and measure recovered
            cash.
          </p>
        </div>
        <button
          onClick={runBatch}
          className="rounded-lg bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-teal-700"
        >
          Run recovery batch
        </button>
      </header>
      <div className="square-card-grid">
        <div className="metric-card square-card">
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            ₹
            {Math.round(summary?.total_revenue_at_risk || 0).toLocaleString(
              "en-IN",
            )}
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Revenue at Risk
          </div>
        </div>

        <div className="metric-card square-card">
          <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
            ₹
            {Math.round(summary?.total_revenue_recovered || 0).toLocaleString(
              "en-IN",
            )}
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Recovered
          </div>
        </div>

        <div className="metric-card square-card">
          <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
            {(summary?.recovery_rate || 0).toFixed(1)}%
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Recovery Rate
          </div>
        </div>

        <div className="metric-card square-card">
          <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            {summary?.active_cases || 0}
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Active Cases
          </div>
        </div>

        <div className="metric-card square-card">
          <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
            {summary?.escalated_cases || 0}
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Escalated
          </div>
        </div>

        <div className="metric-card square-card">
          <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
            {summary?.recovered_cases || 0}
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Successful
          </div>
        </div>
      </div>
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <section className="panel xl:col-span-2">
          <div className="flex items-center justify-between">
            <div>
              <p className="section-kicker">Leakage taxonomy</p>
              <h2 className="section-title">Why revenue is at risk</h2>
            </div>
            <span className="status-pill">
              {failureReasonItems.length} causes
            </span>
          </div>
          <div className="mt-5 space-y-3">
            {failureReasonItems.map((r: any, index) => (
              <div
                key={r.reason || r.type || index}
                className="flex items-center justify-between border-b border-slate-100 py-3 last:border-0"
              >
                <div className="font-medium">{r.reason || r.type}</div>
                <div className="text-sm font-semibold text-slate-500">
                  {r.count || r.recovered || 0} cases
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="panel">
          <p className="section-kicker">Intervention mix</p>
          <h2 className="section-title">Recovery by channel</h2>
          <div className="mt-5 space-y-3">
            {recoveryItems.map((r: any, index) => (
              <div
                key={r.type || r.reason || index}
                className="flex items-center justify-between border-b border-slate-100 py-3 last:border-0"
              >
                <div className="font-medium">{r.type || r.reason}</div>
                <div className="text-sm font-semibold text-teal-700">
                  ₹{Math.round(r.recovered || 0).toLocaleString("en-IN")}
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <section className="panel">
          <p className="section-kicker">Money recovered</p>
          <h2 className="section-title">Recovery by risk category</h2>
          <div className="chart-panel">
            {chartRecovery.length ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={chartRecovery}
                  margin={{ top: 10, right: 10, left: 0, bottom: 35 }}
                >
                  <XAxis
                    dataKey="label"
                    angle={-18}
                    textAnchor="end"
                    height={55}
                    tick={{ fontSize: 11, fill: "#718096" }}
                  />
                  <YAxis
                    tick={{ fontSize: 11, fill: "#718096" }}
                    tickFormatter={(value) => `₹${Math.round(value / 1000)}k`}
                  />
                  <Tooltip
                    formatter={(value: number) => [
                      `₹${Math.round(value).toLocaleString("en-IN")}`,
                      "Recovered",
                    ]}
                  />
                  <Bar
                    dataKey="recovered"
                    fill="#14b8a6"
                    radius={[5, 5, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="empty-state">
                Recovery data will appear after an agent run.
              </div>
            )}
          </div>
        </section>
        <section className="panel">
          <p className="section-kicker">Portfolio exposure</p>
          <h2 className="section-title">Risk distribution</h2>
          <div className="chart-grid">
            <div className="chart-panel">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartRisk}
                    dataKey="amount"
                    nameKey="name"
                    innerRadius={58}
                    outerRadius={88}
                    paddingAngle={3}
                  >
                    {chartRisk.map((item, index) => (
                      <Cell
                        key={item.name}
                        fill={
                          ["#ef806d", "#f4b860", "#14b8a6", "#93a7bd"][
                            index % 4
                          ]
                        }
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value: number) => [
                      `₹${Math.round(value).toLocaleString("en-IN")}`,
                      "At risk",
                    ]}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="space-y-3">
              {chartRisk.map((item, index) => (
                <div
                  key={item.name}
                  className="flex items-center justify-between gap-4 text-sm"
                >
                  <span>
                    <i
                      className="legend-dot"
                      style={{
                        background: [
                          "#ef806d",
                          "#f4b860",
                          "#14b8a6",
                          "#93a7bd",
                        ][index % 4],
                      }}
                    />
                    {item.name}
                  </span>
                  <b>{item.count}</b>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>

      <section className="panel">
        <p className="section-kicker">Agent workflow</p>
        <h2 className="section-title">Detect to recover</h2>
        <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {funnelItems.map((f: any, index) => (
            <div key={f.stage || index} className="funnel-step">
              <span>{String(index + 1).padStart(2, "0")}</span>
              <b>{f.count}</b>
              <small>{f.stage}</small>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default Dashboard;
