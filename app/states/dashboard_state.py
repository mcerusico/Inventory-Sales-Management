import reflex as rx
from sqlmodel import select, func
from app.db_models import Sale, Customer, Installment, User
from typing import TypedDict


class DashboardMetrics(TypedDict):
    total_revenue: float
    total_sales: int
    total_customers: int
    pending_installments: int


class DashboardState(rx.State):
    admin_metrics: DashboardMetrics = {
        "total_revenue": 0,
        "total_sales": 0,
        "total_customers": 0,
        "pending_installments": 0,
    }
    seller_metrics: DashboardMetrics = {
        "total_revenue": 0,
        "total_sales": 0,
        "total_customers": 0,
        "pending_installments": 0,
    }

    @rx.event
    async def load_metrics(self):
        from app.states.auth_state import AuthState

        auth_state = await self.get_state(AuthState)
        if not auth_state.current_user:
            return
        with rx.session() as session:
            if auth_state.is_admin:
                total_revenue = (
                    session.exec(select(func.sum(Sale.total_amount))).one_or_none() or 0
                )
                total_sales = session.exec(select(func.count(Sale.id))).one()
                total_customers = session.exec(select(func.count(Customer.id))).one()
                pending_installments = session.exec(
                    select(func.count(Installment.id)).where(
                        Installment.status == "Pending"
                    )
                ).one()
                self.admin_metrics = {
                    "total_revenue": round(total_revenue, 2),
                    "total_sales": total_sales,
                    "total_customers": total_customers,
                    "pending_installments": pending_installments,
                }
            else:
                user_id = auth_state.current_user["id"]
                branch_id = auth_state.current_user["branch_id"]
                total_revenue = (
                    session.exec(
                        select(func.sum(Sale.total_amount)).where(
                            Sale.user_id == user_id
                        )
                    ).one_or_none()
                    or 0
                )
                total_sales = session.exec(
                    select(func.count(Sale.id)).where(Sale.user_id == user_id)
                ).one()
                total_customers = session.exec(
                    select(func.count(Customer.id)).where(
                        Customer.branch_id == branch_id
                    )
                ).one()
                sales_by_user = select(Sale.id).where(Sale.user_id == user_id)
                pending_installments = session.exec(
                    select(func.count(Installment.id)).where(
                        Installment.sale_id.in_(sales_by_user),
                        Installment.status == "Pending",
                    )
                ).one()
                self.seller_metrics = {
                    "total_revenue": round(total_revenue, 2),
                    "total_sales": total_sales,
                    "total_customers": total_customers,
                    "pending_installments": pending_installments,
                }