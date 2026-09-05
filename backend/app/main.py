from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db, SessionLocal
from app.api import dashboard, cases, agent, batch, audit, simulation
from app.config import settings
from app.models.customer import Customer
from app.models.case import RevenueRiskCase
from app.seed.seed_data import SeedData


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        # Seed-heal: reseed whenever no cases exist (handles half-seeded/wiped DBs).
        if db.query(RevenueRiskCase).count() == 0:
            stats = SeedData(db).seed_all()
            print(f"Seeded demo data: {stats}")
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered revenue recovery operating system",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    # Local dev: Vite (:5173) calls API (:8000) cross-origin.
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173",
                   "http://localhost:3000", "http://127.0.0.1:3000"],
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


@app.get("/api/health")
def health():
    return {"status": "healthy", "app": settings.APP_NAME, "demo_mode": settings.DEMO_MODE}