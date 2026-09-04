from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db, SessionLocal
from app.api import dashboard, cases, agent, batch, audit, simulation
from app.config import settings
from app.models.customer import Customer
from app.models.case import RevenueRiskCase
from app.seed.seed_data import SeedData

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered revenue recovery operating system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(cases.router)
app.include_router(agent.router)
app.include_router(batch.router)
app.include_router(audit.router)
app.include_router(simulation.router)


@app.on_event("startup")
def startup():
    init_db()
    db = SessionLocal()
    try:
        customer_count = db.query(Customer).count()
        case_count = db.query(RevenueRiskCase).count()
        if customer_count == 0 and case_count == 0:
            SeedData(db).seed_all()
    finally:
        db.close()


@app.get("/api/health")
def health():
    return {"status": "healthy", "app": settings.APP_NAME, "demo_mode": settings.DEMO_MODE}