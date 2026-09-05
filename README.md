# RevenueRecover AI — AI Revenue Recovery Operating System

Autonomous agent that detects revenue at risk, diagnoses root cause, checks deterministic policy, executes bounded recovery, verifies payment, and audits everything. **Money recovered is the headline metric.** All payments/messages are simulated via mock adapters — no real money moves.

## Architecture
`RiskEngine → RootCause → Strategy → PolicyGate → RecoveryEngine → Verify → Stop/Escalate → Audit`. LLM proposes structured JSON (optional, deterministic fallback built in); policy engine approves/rejects; mock providers (`MockPayment/Subscription/Notification/CRM`) implement replaceable interfaces. All metrics are DB-aggregated (`SUM(recovered)`, `COUNT(status)`), never hard-coded.

## Run locally (no Docker, no cloud)

Prerequisites: Python 3.12, Node 20.

Backend (http://localhost:8000, docs at /docs):
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --port 8000
```
First boot auto-creates `revenue_recover.db` (SQLite) and seeds demo data (100 customers, 72 risk cases).

Frontend (http://localhost:5173, proxied to the API):
```bash
cd frontend
npm ci
npm run dev
```

Optional: copy `.env.example` to `.env` to override `DATABASE_URL` (Postgres), `LLM_API_KEY`, `MAX_RETRIES`, `MAX_CONTACTS_PER_WEEK`, `MANUAL_REVIEW_THRESHOLD`.

## Demo (3–5 min)
1. Dashboard → Revenue at Risk / Recovered / Rate. 2. Cases → open failed payment → risk + AI diagnosis. 3. Run recovery → Detect→…→Recover steps, recovered increases. 4. Audit trail per decision. 5. Agent Runs → Run full batch → `RECOVERY COMPLETE` summary. 6. Escalated/MANUAL_REVIEW case → why it stopped → Approve/Reject/Escalate.
7. Reset anytime: `POST /api/simulation/demo/reset`.

## Safety
MAX_RETRIES=3, max 2 contacts/7d, allowed hours 08–20, no retry on permanent failure (expired/invalid/fraud), stop on recovered/opt-out/closed, manual review above threshold. PII masked in APIs.

## Tests
```bash
cd backend
python -m pytest tests/test_engine.py -q
```

## Limitations
Simulated payments/notifications; SQLite default (Postgres via `DATABASE_URL`); LLM optional with deterministic fallback.
