from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.models.transaction import Transaction
from app.models.case import RevenueRiskCase
from app.models.subscription import Subscription
from app.models.invoice import Invoice
from app.models.promise import PromiseToPay
from app.models.recovery import RecoveryAction
from app.models.audit import AuditEvent
from datetime import datetime, timedelta
import random

random.seed(42)


class SeedData:
    def __init__(self, db: Session):
        self.db = db

    def seed_all(self):
        customers = self._seed_customers()
        transactions = self._seed_transactions(customers)
        subscriptions = self._seed_subscriptions(customers)
        invoices = self._seed_invoices(customers)
        promises = self._seed_promises(invoices)
        cases = self._seed_cases(customers, transactions, subscriptions, invoices)

        stats = {
            "customers": len(customers),
            "transactions": len(transactions),
            "subscriptions": len(subscriptions),
            "invoices": len(invoices),
            "promises": len(promises),
            "cases": len(cases),
        }
        return stats

    def _seed_customers(self):
        customers = []
        for i in range(100):
            first = ["Rahul", "Priya", "Amit", "Sneha", "Vikram"][i % 5]
            last = ["Sharma", "Patel", "Kumar", "Singh", "Reddy"][i % 5]
            name = "%s %s" % (first, last)
            email = "contact@company%d.com" % i
            phone = "+9198765%d%d" % (i // 10, i % 10)
            segment = ["VIP", "HIGH_VALUE", "REGULAR", "LOW_VALUE"][i % 4]
            ltv = {"VIP": 300000, "HIGH_VALUE": 80000, "REGULAR": 15000, "LOW_VALUE": 2000}[segment]
            hist_rate = 0.85 + (i % 7) * 0.015
            recent_rate = hist_rate * random.uniform(0.4, 1.0)
            recent_rate = min(max(recent_rate, 0.2), 1.0)

            c = Customer(
                name=name, email=email, phone=phone, segment=segment,
                lifetime_value=ltv, risk_score=random.uniform(10, 95),
                historical_success_rate=round(hist_rate, 3),
                recent_success_rate=round(recent_rate, 3),
                is_active=1, has_opted_out=random.random() < 0.03,
            )
            self.db.add(c)
            customers.append(c)
        self.db.commit()
        return customers

    def _seed_transactions(self, customers):
        txns = []
        methods = ["upi", "card", "netbanking", "wallet"]
        for c in customers:
            for j in range(random.randint(2, 5)):
                amt = random.uniform(500, 50000)
                is_fail = random.random() < 0.25
                status = "FAILED" if is_fail else "SUCCESS"
                reason = random.choice(["insufficient_funds", "bank_decline", "network_error", "expired_card"]) if is_fail else None
                txn = Transaction(
                    customer_id=c.id, amount=round(amt, 2), currency="INR",
                    status=status, payment_method=random.choice(methods),
                    failure_reason=reason,
                    gateway_reference="GW%06d" % random.randint(100000, 999999),
                    created_at=datetime.now() - timedelta(days=random.randint(1, 45)),
                )
                self.db.add(txn)
                txns.append(txn)
        self.db.commit()
        return txns

    def _seed_subscriptions(self, customers):
        subs = []
        plans = [("Basic", 499), ("Standard", 999), ("Premium", 1999), ("Enterprise", 4999)]
        sub_cust = random.sample(customers, min(20, len(customers)))
        for c in sub_cust:
            plan, amt = random.choice(plans)
            is_fail = random.random() < 0.6
            sub = Subscription(
                customer_id=c.id, plan_name=plan, amount=amt,
                currency="INR", status="PAST_DUE" if is_fail else "ACTIVE",
                payment_method=random.choice(["card", "upi"]),
                mandate_id="MAND%05d" % random.randint(1000, 9999) if is_fail else None,
                failed_payment_count=random.randint(1, 4) if is_fail else 0,
                last_payment_date=datetime.now() - timedelta(days=random.randint(1, 30)),
                next_payment_date=datetime.now() + timedelta(days=random.randint(1, 30)),
                created_at=datetime.now() - timedelta(days=random.randint(30, 180)),
            )
            self.db.add(sub)
            subs.append(sub)
        self.db.commit()
        return subs

    def _seed_invoices(self, customers):
        invoices = []
        inv_cust = random.sample(customers, min(20, len(customers)))
        for i, c in enumerate(inv_cust):
            amt = random.uniform(5000, 150000)
            days = random.randint(5, 45)
            is_paid = random.random() < 0.3
            inv = Invoice(
                customer_id=c.id, invoice_number="INV-2024-%04d" % i,
                amount=round(amt, 2), currency="INR",
                status="PAID" if is_paid else "OVERDUE",
                due_date=datetime.now() - timedelta(days=days),
                paid_amount=amt if is_paid else 0,
                paid_date=datetime.now() - timedelta(days=max(1, days - 5)) if is_paid else None,
                days_overdue=0 if is_paid else days,
                account_owner="%s %s" % (random.choice(["Rahul", "Priya", "Amit"]), random.choice(["Sharma", "Patel", "Kumar"])),
                customer_segment=c.segment,
                created_at=datetime.now() - timedelta(days=days + 30),
            )
            self.db.add(inv)
            invoices.append(inv)
        self.db.commit()
        return invoices

    def _seed_promises(self, invoices):
        promises = []
        overdue = [i for i in invoices if i.status == "OVERDUE"]
        for inv in overdue[:8]:
            is_fulfilled = random.random() < 0.3
            ptp = PromiseToPay(
                invoice_id=inv.id, promised_amount=round(inv.amount * random.uniform(0.5, 1.0), 2),
                promise_date=datetime.now() - timedelta(days=random.randint(1, 14)),
                status="FULFILLED" if is_fulfilled else "MISSED",
                fulfilled_amount=round(inv.amount, 2) if is_fulfilled else 0,
                fulfilled_at=datetime.now() - timedelta(days=random.randint(0, 5)) if is_fulfilled else None,
                reminder_count=random.randint(1, 3),
                missed_count=random.randint(0, 3) if not is_fulfilled else 0,
            )
            self.db.add(ptp)
            promises.append(ptp)
        self.db.commit()
        return promises

    def _seed_cases(self, customers, transactions, subscriptions, invoices):
        cases = []
        case_num = 1001

        # Showcase: overdue invoice ₹1,20,000
        acme_c = customers[0]
        acme_inv = invoices[0] if invoices else None
        if acme_inv:
            case = RevenueRiskCase(
                case_number="CASE-%04d" % case_num, customer_id=acme_c.id,
                source_type="RECEIVABLE", invoice_id=acme_inv.id,
                amount_at_risk=120000, recovered_amount=0,
                status="DETECTED", risk_level="HIGH", risk_score=75,
                root_cause="invoice_overdue", current_retry_count=0, max_retries=3,
            )
            self.db.add(case)
            cases.append(case)
            case_num += 1

        # Showcase: failed subscription ₹4,999
        sub_c = customers[1] if len(customers) > 1 else customers[0]
        sub = subscriptions[0] if subscriptions else None
        if sub:
            txn = Transaction(customer_id=sub_c.id, amount=4999, currency="INR",
                              status="FAILED", payment_method="card",
                              failure_reason="insufficient_funds",
                              gateway_reference="GW-SHOWCASE",
                              created_at=datetime.now() - timedelta(days=2))
            self.db.add(txn)
            self.db.flush()
            case = RevenueRiskCase(
                case_number="CASE-%04d" % case_num, customer_id=sub_c.id,
                source_type="SUBSCRIPTION", transaction_id=txn.id,
                subscription_id=sub.id, amount_at_risk=4999, recovered_amount=0,
                status="DETECTED", risk_level="MEDIUM", risk_score=55,
                root_cause="insufficient_funds", current_retry_count=0, max_retries=3,
            )
            self.db.add(case)
            cases.append(case)
            case_num += 1

        # Payment failure cases
        failed_txns = [t for t in transactions if t.status == "FAILED"]
        for txn in failed_txns[:20]:
            c = next((c for c in customers if c.id == txn.customer_id), customers[0])
            amount = round(txn.amount * random.uniform(1, 3), 2)
            case = RevenueRiskCase(
                case_number="CASE-%04d" % case_num, customer_id=txn.customer_id,
                source_type="PAYMENT_FAILURE", transaction_id=txn.id,
                amount_at_risk=amount, recovered_amount=0,
                status="DETECTED", risk_level=random.choice(["LOW", "MEDIUM", "HIGH"]),
                risk_score=round(random.uniform(30, 85), 1),
                root_cause=txn.failure_reason or "unknown", current_retry_count=0, max_retries=3,
            )
            self.db.add(case)
            cases.append(case)
            case_num += 1

        # Checkout abandonment cases
        for i in range(15):
            c = random.choice(customers)
            amount = round(random.uniform(1000, 25000), 2)
            case = RevenueRiskCase(
                case_number="CASE-%04d" % case_num, customer_id=c.id,
                source_type="CHECKOUT", amount_at_risk=amount, recovered_amount=0,
                status="DETECTED", risk_level=random.choice(["LOW", "MEDIUM"]),
                risk_score=round(random.uniform(25, 65), 1),
                root_cause=random.choice(["user_abandoned", "payment_method_failure", "timeout"]),
                current_retry_count=0, max_retries=2,
            )
            self.db.add(case)
            cases.append(case)
            case_num += 1

        # Subscription failure cases
        failed_subs = [s for s in subscriptions if s.status == "PAST_DUE"]
        for sub in failed_subs[:8]:
            c = next((c for c in customers if c.id == sub.customer_id), customers[0])
            amount = round(sub.amount * random.uniform(1, 2), 2)
            case = RevenueRiskCase(
                case_number="CASE-%04d" % case_num, customer_id=sub.customer_id,
                source_type="SUBSCRIPTION", amount_at_risk=amount, recovered_amount=0,
                status="DETECTED", risk_level=random.choice(["MEDIUM", "HIGH"]),
                risk_score=round(random.uniform(40, 80), 1),
                root_cause=random.choice(["mandate_failure", "insufficient_funds", "expired_card"]),
                current_retry_count=0, max_retries=3,
            )
            self.db.add(case)
            cases.append(case)
            case_num += 1

        # Receivable cases
        overdue_Invs = [i for i in invoices if i.status == "OVERDUE"]
        for inv in overdue_Invs[:6]:
            c = next((c for c in customers if c.id == inv.customer_id), customers[0])
            amount = round(inv.amount * random.uniform(0.8, 1.2), 2)
            days = inv.days_overdue
            case = RevenueRiskCase(
                case_number="CASE-%04d" % case_num, customer_id=c.id,
                source_type="RECEIVABLE", invoice_id=inv.id,
                amount_at_risk=amount, recovered_amount=0,
                status="DETECTED",
                risk_level=("CRITICAL" if days > 30 else "HIGH" if days > 14 else "MEDIUM"),
                risk_score=min(95, round(30 + days * 1.2, 1)),
                root_cause="invoice_overdue", current_retry_count=0, max_retries=3,
            )
            self.db.add(case)
            cases.append(case)
            case_num += 1

        # Mandate failure cases
        for i in range(5):
            c = random.choice(customers)
            amount = round(random.uniform(1000, 10000), 2)
            case = RevenueRiskCase(
                case_number="CASE-%04d" % case_num, customer_id=c.id,
                source_type="MANDATE", amount_at_risk=amount, recovered_amount=0,
                status="DETECTED", risk_level=random.choice(["MEDIUM", "HIGH"]),
                risk_score=round(random.uniform(45, 75), 1),
                root_cause="mandate_failure", current_retry_count=0, max_retries=3,
            )
            self.db.add(case)
            cases.append(case)
            case_num += 1

        # Promise-to-pay cases
        for i in range(6):
            c = random.choice(customers)
            amount = round(random.uniform(5000, 50000), 2)
            case = RevenueRiskCase(
                case_number="CASE-%04d" % case_num, customer_id=c.id,
                source_type="PROMISE", amount_at_risk=amount, recovered_amount=0,
                status="DETECTED", risk_level=random.choice(["LOW", "MEDIUM"]),
                risk_score=round(random.uniform(30, 60), 1),
                root_cause="missed_promise", current_retry_count=0, max_retries=2,
            )
            self.db.add(case)
            cases.append(case)
            case_num += 1

        self.db.commit()
        return cases