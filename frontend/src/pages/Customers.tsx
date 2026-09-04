import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { casesAPI } from "../lib/api";

function Customers() {
  const [cases, setCases] = useState<any[]>([]);
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<number | null>(null);
  useEffect(() => {
    casesAPI
      .getAll()
      .then((data) => setCases(Array.isArray(data) ? data : []))
      .catch(console.error);
  }, []);
  const customers = Array.from(
    new Map(cases.map((item) => [item.customer_id, item])).values(),
  );
  const visibleCustomers = customers.filter((item) =>
    `${item.customer_name} ${item.root_cause} ${item.source_type}`
      .toLowerCase()
      .includes(query.toLowerCase()),
  );
  return (
    <div className="space-y-6">
      <header>
        <p className="section-kicker">Portfolio / customer health</p>
        <h1 className="mt-2 text-3xl font-semibold text-slate-950">
          Customers
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Accounts with revenue exposure, recent risk, and an actionable
          recovery path.
        </p>
      </header>
      <section className="panel overflow-hidden p-0">
        <div className="flex flex-col gap-3 border-b border-slate-100 p-5 sm:flex-row sm:items-center sm:justify-between">
          <div className="text-sm font-semibold text-slate-700">
            {visibleCustomers.length} customer accounts with active signals
          </div>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search accounts"
            className="control-input"
          />
        </div>
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>Customer</th>
                <th>Primary signal</th>
                <th>Root cause</th>
                <th>Exposure</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {visibleCustomers.map((item) => (
                <tr
                  className={`customer-row ${selected === item.customer_id ? "customer-row-selected" : ""}`}
                  onClick={() =>
                    setSelected(
                      selected === item.customer_id ? null : item.customer_id,
                    )
                  }
                  key={item.customer_id}
                >
                  <td>
                    <div className="table-person">
                      <div className="avatar avatar-blue">
                        {String(item.customer_name || "CU")
                          .slice(0, 2)
                          .toUpperCase()}
                      </div>
                      <div>
                        <Link
                          to={`/cases/${item.id}`}
                          className="font-semibold text-slate-800 hover:text-teal-700"
                        >
                          {item.customer_name}
                        </Link>
                        <p className="mt-1 text-xs text-slate-500">
                          Primary exposure:{" "}
                          {String(item.source_type || "risk").replaceAll(
                            "_",
                            " ",
                          )}
                        </p>
                      </div>
                    </div>
                  </td>
                  <td>
                    {String(item.source_type || "risk").replaceAll("_", " ")}
                  </td>
                  <td className="muted-cell">
                    {item.root_cause || "Diagnosis pending"}
                  </td>
                  <td className="font-semibold text-slate-800">
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
                      Open →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {selected !== null && (
          <div className="customer-insight">
            <b>Selected account insight</b>
            <span>
              Click a customer row to inspect its recovery signal. Current
              selection:{" "}
              {
                customers.find((item) => item.customer_id === selected)
                  ?.customer_name
              }
            </span>
          </div>
        )}
      </section>
    </div>
  );
}
export default Customers;
