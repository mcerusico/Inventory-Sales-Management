import reflex as rx
from sqlmodel import select
from app.db_models import Customer, CustomerDict
import sqlalchemy as sa


class CustomerState(rx.State):
    customers: list[CustomerDict] = []
    search_query: str = ""
    new_customer_name: str = ""
    new_customer_phone: str = ""
    new_customer_email: str = ""
    new_customer_address: str = ""

    @rx.var
    def filtered_customers(self) -> list[CustomerDict]:
        if not self.search_query:
            return self.customers
        return [
            c
            for c in self.customers
            if self.search_query.lower() in c["name"].lower()
            or (c["email"] and self.search_query.lower() in c["email"].lower())
            or (c["phone"] and self.search_query.lower() in c["phone"].lower())
        ]

    @rx.event
    async def load_customers(self):
        from app.states.auth_state import AuthState

        auth_state = await self.get_state(AuthState)
        if not auth_state or not auth_state.current_user:
            return
        with rx.session() as session:
            query = select(Customer).options(sa.orm.selectinload(Customer.branch))
            if auth_state.current_user["role"] != "admin":
                query = query.where(
                    Customer.branch_id == auth_state.current_user["branch_id"]
                )
            all_customers = session.exec(query).all()
            self.customers = [
                {**c.dict(), "branch_name": c.branch.name if c.branch else "N/A"}
                for c in all_customers
            ]

    @rx.event(background=True)
    async def add_customer(self, form_data: dict):
        async with self:
            from app.states.auth_state import AuthState

            auth_state = await self.get_state(AuthState)
            if not form_data.get("name"):
                yield rx.toast.error("Customer name is required.")
                return
            branch_id_to_assign = auth_state.current_user["branch_id"]
            if auth_state.is_admin and form_data.get("branch_id"):
                branch_id_to_assign = int(form_data["branch_id"])
            if not branch_id_to_assign:
                yield rx.toast.error("Cannot add customer without a branch assignment.")
                return
            with rx.session() as session:
                new_customer = Customer(
                    name=form_data["name"],
                    phone=form_data.get("phone"),
                    email=form_data.get("email"),
                    address=form_data.get("address"),
                    branch_id=branch_id_to_assign,
                )
                session.add(new_customer)
                session.commit()
                self.new_customer_name = ""
                self.new_customer_phone = ""
                self.new_customer_email = ""
                self.new_customer_address = ""
        yield CustomerState.load_customers
        yield rx.toast.success("Customer added successfully!")

    @rx.event(background=True)
    async def delete_customer(self, customer_id: int):
        async with self:
            with rx.session() as session:
                customer = session.get(Customer, customer_id)
                if customer:
                    session.delete(customer)
                    session.commit()
        yield CustomerState.load_customers
        yield rx.toast.info(f"Customer deleted.")