import reflex as rx
from typing import TypedDict
from sqlmodel import select, and_
from app.db_models import (
    FinancialPayment,
    FinancialInstallment,
    Customer,
    FinancialPaymentDict,
    FinancialInstallmentDict,
)
from datetime import datetime, timedelta
import sqlalchemy as sa


class FinancialState(rx.State):
    financial_payments: list[FinancialPaymentDict] = []
    selected_payment_installments: list[FinancialInstallmentDict] = []
    selected_customer_id: str = ""
    principal_amount: float = 0.0
    interest_rate: float = 0.0
    installment_type: str = "monthly"
    num_installments: int = 12
    show_installments_for_payment_id: int | None = None

    @rx.var
    def total_amount(self) -> float:
        interest = self.principal_amount * (self.interest_rate / 100)
        return self.principal_amount + interest

    @rx.var
    def installment_amount(self) -> float:
        if self.num_installments > 0:
            return self.total_amount / self.num_installments
        return 0.0

    @rx.event
    async def load_financial_payments(self):
        from app.states.auth_state import AuthState

        auth_state = await self.get_state(AuthState)
        if not auth_state.current_user:
            return
        with rx.session() as session:
            query = select(FinancialPayment).options(
                sa.orm.selectinload(FinancialPayment.customer),
                sa.orm.selectinload(FinancialPayment.installments),
            )
            if not auth_state.is_admin:
                query = query.where(
                    FinancialPayment.user_id == auth_state.current_user["id"]
                )
            payments = session.exec(
                query.order_by(FinancialPayment.created_at.desc())
            ).all()
            self.financial_payments = []
            for p in payments:
                installments_dict = []
                for i in p.installments:
                    installments_dict.append(
                        {
                            "id": i.id,
                            "payment_id": i.payment_id,
                            "installment_number": i.installment_number,
                            "due_date": i.due_date.isoformat(),
                            "amount_due": i.amount_due,
                            "amount_paid": i.amount_paid,
                            "status": i.status,
                            "paid_at": i.paid_at.isoformat() if i.paid_at else None,
                        }
                    )
                self.financial_payments.append(
                    {
                        "id": p.id,
                        "customer_name": p.customer.name if p.customer else "N/A",
                        "principal_amount": p.principal_amount,
                        "interest_rate": p.interest_rate,
                        "total_amount": p.total_amount,
                        "installment_type": p.installment_type,
                        "num_installments": p.num_installments,
                        "installment_amount": p.installment_amount,
                        "status": p.status,
                        "created_at": p.created_at.isoformat(),
                        "installments": installments_dict,
                    }
                )

    @rx.event(background=True)
    async def create_financial_payment(self):
        async with self:
            from app.states.auth_state import AuthState

            auth_state = await self.get_state(AuthState)
            if (
                not self.selected_customer_id
                or self.principal_amount <= 0
                or self.num_installments <= 0
                or (not auth_state.current_user)
            ):
                yield rx.toast.error("Please fill all fields correctly.")
                return
            branch_id = auth_state.current_user.get("branch_id")
            if not branch_id:
                yield rx.toast.error("User is not associated with a branch.")
                return
            with rx.session() as session:
                new_payment = FinancialPayment(
                    customer_id=int(self.selected_customer_id),
                    user_id=auth_state.current_user["id"],
                    branch_id=branch_id,
                    principal_amount=self.principal_amount,
                    interest_rate=self.interest_rate,
                    total_amount=self.total_amount,
                    installment_type=self.installment_type,
                    num_installments=self.num_installments,
                    installment_amount=self.installment_amount,
                    status="Active",
                )
                session.add(new_payment)
                session.flush()
                today = datetime.utcnow()
                for i in range(self.num_installments):
                    if self.installment_type == "weekly":
                        due_date = today + timedelta(weeks=i + 1)
                    else:
                        due_date = today + timedelta(days=30 * (i + 1))
                    installment = FinancialInstallment(
                        payment_id=new_payment.id,
                        installment_number=i + 1,
                        due_date=due_date,
                        amount_due=self.installment_amount,
                    )
                    session.add(installment)
                session.commit()
                self.selected_customer_id = ""
                self.principal_amount = 0.0
                self.interest_rate = 0.0
                self.num_installments = 12
        yield FinancialState.load_financial_payments
        yield rx.toast.success("Financial payment plan created!")

    @rx.event
    def toggle_installments_view(self, payment_id: int):
        if self.show_installments_for_payment_id == payment_id:
            self.show_installments_for_payment_id = None
            self.selected_payment_installments = []
        else:
            self.show_installments_for_payment_id = payment_id
            for payment in self.financial_payments:
                if payment["id"] == payment_id:
                    self.selected_payment_installments = payment["installments"]
                    break

    @rx.event(background=True)
    async def mark_installment_paid(self, installment_id: int):
        async with self:
            with rx.session() as session:
                installment = session.get(FinancialInstallment, installment_id)
                if installment:
                    installment.status = "Paid"
                    installment.amount_paid = installment.amount_due
                    installment.paid_at = datetime.utcnow()
                    session.add(installment)
                    payment = session.get(FinancialPayment, installment.payment_id)
                    if payment:
                        all_paid = all(
                            (inst.status == "Paid" for inst in payment.installments)
                        )
                        if all_paid:
                            payment.status = "Completed"
                            session.add(payment)
                    session.commit()
        yield FinancialState.load_financial_payments
        yield FinancialState.toggle_installments_view(installment.payment_id)
        yield rx.toast.success("Installment marked as paid.")