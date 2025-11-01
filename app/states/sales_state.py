import reflex as rx
from typing import TypedDict, Any
from sqlmodel import select, and_
from app.db_models import (
    Sale,
    SaleDetail,
    Product,
    Stock,
    Customer,
    User,
    Branch,
    SaleDict,
    Installment,
)
from datetime import datetime, timedelta
import sqlalchemy as sa
import logging


class CartItem(TypedDict):
    product_id: int
    product_name: str
    quantity: int
    price: float
    subtotal: float


class SalesState(rx.State):
    sales: list[SaleDict] = []
    cart: list[CartItem] = []
    selected_customer_id: str = ""
    selected_product_id: str = ""
    current_quantity: int = 1
    payment_method: str = "cash"
    installment_type: str = "weekly"
    num_installments: int = 4
    error_message: str = ""

    @rx.var
    def cart_total(self) -> float:
        return sum((item["subtotal"] for item in self.cart))

    @rx.var
    def installment_amount(self) -> float:
        if self.payment_method in ["weekly", "monthly"] and self.num_installments > 0:
            return self.cart_total / self.num_installments
        return 0.0

    @rx.event
    async def load_sales(self):
        from app.states.auth_state import AuthState

        auth_state = await self.get_state(AuthState)
        if not auth_state.current_user:
            return
        with rx.session() as session:
            query = select(Sale).options(
                sa.orm.selectinload(Sale.customer),
                sa.orm.selectinload(Sale.user),
                sa.orm.selectinload(Sale.branch),
            )
            if not auth_state.is_admin:
                query = query.where(Sale.user_id == auth_state.current_user["id"])
            all_sales = session.exec(query.order_by(Sale.created_at.desc())).all()
            self.sales = [
                {
                    "id": s.id,
                    "customer_name": s.customer.name if s.customer else "N/A",
                    "user_username": s.user.username if s.user else "N/A",
                    "branch_name": s.branch.name if s.branch else "N/A",
                    "total_amount": s.total_amount,
                    "payment_method": s.payment_method,
                    "status": s.status,
                    "created_at": s.created_at.isoformat(),
                }
                for s in all_sales
            ]

    @rx.event
    def add_to_cart(self):
        if not self.selected_product_id:
            return rx.toast.error("Please select a product.")
        product_id = int(self.selected_product_id)
        for item in self.cart:
            if item["product_id"] == product_id:
                item["quantity"] += self.current_quantity
                item["subtotal"] = item["quantity"] * item["price"]
                self.current_quantity = 1
                return
        with rx.session() as session:
            product = session.get(Product, product_id)
            if product:
                self.cart.append(
                    {
                        "product_id": product.id,
                        "product_name": product.name,
                        "quantity": self.current_quantity,
                        "price": product.price,
                        "subtotal": self.current_quantity * product.price,
                    }
                )
                self.current_quantity = 1

    @rx.event
    def remove_from_cart(self, product_id: int):
        self.cart = [item for item in self.cart if item["product_id"] != product_id]

    @rx.event(background=True)
    async def create_sale(self):
        async with self:
            from app.states.auth_state import AuthState

            auth_state = await self.get_state(AuthState)
            if (
                not self.cart
                or not self.selected_customer_id
                or (not auth_state.current_user)
            ):
                yield rx.toast.error("Cart, customer, and user must be set.")
                return
            branch_id = auth_state.current_user.get("branch_id")
            if not branch_id:
                yield rx.toast.error("User is not associated with a branch.")
                return
            with rx.session() as session:
                for item in self.cart:
                    stock = session.exec(
                        select(Stock).where(
                            and_(
                                Stock.product_id == item["product_id"],
                                Stock.branch_id == branch_id,
                            )
                        )
                    ).first()
                    if not stock or stock.quantity < item["quantity"]:
                        yield rx.toast.error(
                            f"Not enough stock for {item['product_name']}."
                        )
                        return
                sale_status = (
                    "Paid" if self.payment_method in ["cash", "card"] else "Pending"
                )
                new_sale = Sale(
                    customer_id=int(self.selected_customer_id),
                    user_id=auth_state.current_user["id"],
                    branch_id=branch_id,
                    total_amount=self.cart_total,
                    payment_method=self.payment_method,
                    status=sale_status,
                )
                session.add(new_sale)
                session.flush()
                for item in self.cart:
                    sale_detail = SaleDetail(
                        sale_id=new_sale.id,
                        product_id=item["product_id"],
                        quantity=item["quantity"],
                        unit_price=item["price"],
                        subtotal=item["subtotal"],
                    )
                    session.add(sale_detail)
                    stock = session.exec(
                        select(Stock).where(
                            and_(
                                Stock.product_id == item["product_id"],
                                Stock.branch_id == branch_id,
                            )
                        )
                    ).first()
                    stock.quantity -= item["quantity"]
                    session.add(stock)
                if self.payment_method in ["weekly", "monthly"]:
                    today = datetime.utcnow()
                    for i in range(self.num_installments):
                        if self.payment_method == "weekly":
                            due_date = today + timedelta(weeks=i + 1)
                        else:
                            due_date = today + timedelta(days=30 * (i + 1))
                        installment = Installment(
                            sale_id=new_sale.id,
                            due_date=due_date,
                            amount_due=self.installment_amount,
                            status="Pending",
                        )
                        session.add(installment)
                session.commit()
            self.cart = []
            self.selected_customer_id = ""
            self.payment_method = "cash"
        yield SalesState.load_sales
        yield rx.toast.success("Sale created successfully!")