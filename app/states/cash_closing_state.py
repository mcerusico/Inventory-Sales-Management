import reflex as rx
from typing import TypedDict
from sqlmodel import select, and_, or_, func
from app.db_models import (
    CashClosing,
    CashClosingDetail,
    Sale,
    FinancialPayment,
    FinancialInstallment,
    Customer,
    User,
    Branch,
    CashClosingDict,
    CollectedPaymentDict,
)
from datetime import datetime, timedelta
import sqlalchemy as sa


class CashClosingState(rx.State):
    period_type: str = "weekly"
    start_date: str = ""
    end_date: str = ""
    collected_payments: list[CollectedPaymentDict] = []
    total_collected: float = 0.0
    closings_history: list[CashClosingDict] = []

    @rx.event
    async def on_page_load(self):
        self._set_default_dates()
        yield CashClosingState.fetch_collected_payments
        yield CashClosingState.load_closings_history

    def _set_default_dates(self):
        today = datetime.now()
        if self.period_type == "weekly":
            start_of_week = today - timedelta(days=today.weekday())
            self.start_date = start_of_week.strftime("%Y-%m-%d")
            self.end_date = (start_of_week + timedelta(days=6)).strftime("%Y-%m-%d")
        elif self.period_type == "monthly":
            self.start_date = today.replace(day=1).strftime("%Y-%m-%d")
            self.end_date = today.strftime("%Y-%m-%d")

    @rx.event
    def set_period_type_and_fetch(self, period_type: str):
        self.period_type = period_type
        self._set_default_dates()
        return CashClosingState.fetch_collected_payments

    @rx.event
    async def fetch_collected_payments(self):
        from app.states.auth_state import AuthState

        auth_state = await self.get_state(AuthState)
        if not auth_state.current_user or not self.start_date or (not self.end_date):
            return
        start = datetime.strptime(self.start_date, "%Y-%m-%d")
        end = datetime.strptime(self.end_date, "%Y-%m-%d") + timedelta(days=1)
        with rx.session() as session:
            payments_query = (
                select(FinancialInstallment)
                .options(
                    sa.orm.selectinload(FinancialInstallment.payment).selectinload(
                        FinancialPayment.customer
                    )
                )
                .where(
                    FinancialInstallment.paid_at >= start,
                    FinancialInstallment.paid_at < end,
                    FinancialInstallment.status == "Paid",
                )
            )
            sales_query = (
                select(Sale)
                .options(sa.orm.selectinload(Sale.customer))
                .where(
                    Sale.created_at >= start,
                    Sale.created_at < end,
                    or_(Sale.payment_method == "cash", Sale.payment_method == "card"),
                )
            )
            if not auth_state.is_admin:
                payments_query = payments_query.join(FinancialPayment).where(
                    FinancialPayment.user_id == auth_state.current_user["id"]
                )
                sales_query = sales_query.where(
                    Sale.user_id == auth_state.current_user["id"]
                )
            financial_payments = session.exec(payments_query).all()
            cash_sales = session.exec(sales_query).all()
            self.collected_payments = []
            for fp in financial_payments:
                self.collected_payments.append(
                    {
                        "customer_name": fp.payment.customer.name
                        if fp.payment.customer
                        else "N/A",
                        "payment_type": "Credit Payment",
                        "amount": fp.amount_paid,
                        "paid_at": fp.paid_at.isoformat(),
                    }
                )
            for sale in cash_sales:
                self.collected_payments.append(
                    {
                        "customer_name": sale.customer.name if sale.customer else "N/A",
                        "payment_type": f"Direct Sale ({sale.payment_method.capitalize()})",
                        "amount": sale.total_amount,
                        "paid_at": sale.created_at.isoformat(),
                    }
                )
            self.total_collected = sum((p["amount"] for p in self.collected_payments))

    @rx.event(background=True)
    async def perform_cash_closing(self):
        async with self:
            from app.states.auth_state import AuthState

            auth_state = await self.get_state(AuthState)
            if not auth_state.current_user or not self.collected_payments:
                yield rx.toast.error("No payments to close.")
                return
            start = datetime.strptime(self.start_date, "%Y-%m-%d")
            end = datetime.strptime(self.end_date, "%Y-%m-%d")
            with rx.session() as session:
                new_closing = CashClosing(
                    user_id=auth_state.current_user["id"],
                    branch_id=auth_state.current_user["branch_id"],
                    period_type=self.period_type,
                    start_date=start,
                    end_date=end,
                    total_collected=self.total_collected,
                    status="Closed",
                )
                session.add(new_closing)
                session.flush()
                session.commit()
                self.collected_payments = []
                self.total_collected = 0.0
        yield CashClosingState.load_closings_history
        yield rx.toast.success(
            f"{self.period_type.capitalize()} cash closing completed!"
        )

    @rx.event
    async def load_closings_history(self):
        from app.states.auth_state import AuthState

        auth_state = await self.get_state(AuthState)
        if not auth_state.current_user:
            return
        with rx.session() as session:
            query = select(CashClosing).options(
                sa.orm.selectinload(CashClosing.user),
                sa.orm.selectinload(CashClosing.branch),
            )
            if not auth_state.is_admin:
                query = query.where(
                    CashClosing.user_id == auth_state.current_user["id"]
                )
            closings = session.exec(query.order_by(CashClosing.created_at.desc())).all()
            self.closings_history = []
            for c in closings:
                self.closings_history.append(
                    {
                        "id": c.id,
                        "user_name": c.user.username if c.user else "N/A",
                        "branch_name": c.branch.name if c.branch else "N/A",
                        "period_type": c.period_type,
                        "start_date": c.start_date.isoformat(),
                        "end_date": c.end_date.isoformat(),
                        "total_collected": c.total_collected,
                        "status": c.status,
                        "created_at": c.created_at.isoformat(),
                    }
                )