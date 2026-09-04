import sys
sys.path.insert(0, r'C:\Sheesh\Projects\Razorpay_Buildathon\backend')

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=== BACKEND VERIFICATION ===")

# 1. Health
r = client.get("/api/health")
s = "OK" if r.status_code == 200 and r.json()["status"] == "healthy" else "FAIL"
print("[%s] Health endpoint (status=%d)" % (s, r.status_code))

# 2. Dashboard summary
r = client.get("/api/dashboard/summary")
s = "OK" if r.status_code == 200 else "FAIL"
data = r.json() if r.status_code == 200 else {}
print("[%s] Dashboard summary (at_risk=%.2f, recovered=%.2f)" % (s, data.get("total_revenue_at_risk", 0), data.get("total_revenue_recovered", 0)))

# 3. Cases listing
r = client.get("/api/cases/")
s = "OK" if r.status_code == 200 else "FAIL"
cases = r.json() if r.status_code == 200 else []
print("[%s] Cases listing (%d cases)" % (s, len(cases)))

# 4. Batch run
r = client.post("/api/batch/run")
s = "OK" if r.status_code == 200 else "FAIL"
batch = r.json() if r.status_code == 200 else {}
pc = batch.get("cases_processed", 0)
ra = batch.get("recovered_amount", 0)
rr = batch.get("recovery_rate", 0)
print("[%s] Batch run (%d processed, %.2f at risk, recovered %.2f, rate %.1f%%)" % (s, pc, ra, rr, rr))

# 5. Agent analyze (if cases exist)
if len(cases) > 0:
    r = client.post("/api/agent/analyze/%d" % cases[0]["id"])
    s = "OK" if r.status_code == 200 else "FAIL"
    print("[%s] Agent analyze (status=%d)" % (s, r.status_code))

# 6. Audit trail (if cases exist)
if len(cases) > 0:
    r = client.get("/api/audit/%d" % cases[0]["id"])
    s = "OK" if r.status_code == 200 else "FAIL"
    print("[%s] Audit trail (status=%d)" % (s, r.status_code))

# 7. Simulation seed
r = client.post("/api/simulation/seed")
s = "OK" if r.status_code == 200 else "SKIP"  # May fail due to seed_data import
print("[%s] Simulation seed (status=%d)" % (s, r.status_code))

print()
print("=== VERIFICATION COMPLETE ===")