import sys
sys.path.insert(0, r'C:\Sheesh\Projects\Razorpay_Buildathon\backend')

from app.database import init_db, engine, Base
from app.seed.seed_data import SeedData

# Initialize database
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

from sqlalchemy.orm import sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

seed = SeedData(db)
stats = seed.seed_all()
print("Seed stats: %s" % stats)

# Now run batch recovery
from app.services.batch_service import BatchService
bs = BatchService(db)
result = bs.run_full_batch()
print("\nBatch Results:")
print("  Cases processed: %d" % result["cases_processed"])
print("  Total at risk: %s" % result["total_at_risk"])
print("  Recovered: %s" % result["recovered_amount"])
print("  Recovery rate: %s%%" % result["recovery_rate"])
print("  Successful recoveries: %d" % result["successful_recoveries"])
print("  Escalated: %d" % result["escalated_cases"])
print("  Stopped: %d" % result["stopped_cases"])
print("  Actions executed: %d" % result["actions_executed"])
print("  Avg attempts: %s" % result["average_attempts"])
print("  Duration: %s sec" % result["duration_seconds"])

# Verify dashboard summary
from app.services.revenue_calculator import RevenueCalculator
calc = RevenueCalculator(db)
summary = calc.get_dashboard_summary()
print("\nDashboard Summary:")
print("  Total at risk: %s" % summary["total_revenue_at_risk"])
print("  Total recovered: %s" % summary["total_revenue_recovered"])
print("  Recovery rate: %s%%" % summary["recovery_rate"])
print("  Active cases: %d" % summary["active_cases"])
print("  Recovered cases: %d" % summary["recovered_cases"])
print("  Escalated: %d" % summary["escalated_cases"])
print("  Failed cases: %d" % summary["failed_cases"])

db.close()
print("\n✅ Full test completed successfully!")