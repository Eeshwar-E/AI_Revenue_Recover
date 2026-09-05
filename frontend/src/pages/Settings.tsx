function Settings() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-semibold">Settings</h1>
      <p className="text-sm text-slate-500">Guardrails are enforced server-side via environment variables.</p>
      <div className="panel">
        <ul className="space-y-2 text-sm">
          <li><b>MAX_RETRIES</b> = 3 (bounded retries)</li>
          <li><b>MAX_CONTACTS_PER_WEEK</b> = 2 (frequency cap)</li>
          <li><b>MANUAL_REVIEW_THRESHOLD</b> = ₹1,00,000 (human approval above)</li>
          <li><b>Allowed contact hours</b> = 08:00–20:00</li>
          <li><b>DEMO_MODE</b> = true (mock gateway, deterministic seed 42)</li>
        </ul>
        <p className="mt-4 text-sm text-slate-500">Override via <code>.env</code>. See README.</p>
      </div>
    </div>
  );
}
export default Settings;
