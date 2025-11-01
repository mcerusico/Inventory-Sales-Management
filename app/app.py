import reflex as rx
from app.states.auth_state import AuthState
from app.pages.login_page import login_page
from app.pages.dashboard_page import dashboard_page
from app.pages.users_page import users_page
from app.pages.branches_page import branches_page
from app.pages.protected_page import protected_page
from app.pages.customers_page import customers_page
from app.pages.products_page import products_page
from app.pages.stock_page import stock_page
from app.pages.sales_page import sales_page
from app.pages.financial_page import financial_page
from app.pages.cash_closing_page import cash_closing_page
from sqlmodel import SQLModel
from app import db_models


def index() -> rx.Component:
    return rx.cond(AuthState.is_authenticated, dashboard_page(), login_page())


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, on_load=AuthState.check_login)
app.add_page(login_page, route="/login")
app.add_page(dashboard_page, route="/dashboard", on_load=AuthState.check_login)
app.add_page(users_page, route="/users", on_load=AuthState.check_login)
app.add_page(branches_page, route="/branches", on_load=AuthState.check_login)
app.add_page(customers_page, route="/customers", on_load=AuthState.check_login)
app.add_page(products_page, route="/products", on_load=AuthState.check_login)
app.add_page(stock_page, route="/stock", on_load=AuthState.check_login)
app.add_page(sales_page, route="/sales", on_load=AuthState.check_login)
app.add_page(financial_page, route="/financial", on_load=AuthState.check_login)
app.add_page(cash_closing_page, route="/cash-closing", on_load=AuthState.check_login)
app.add_page(protected_page, route="/protected", on_load=AuthState.check_login)


def create_db_and_tables():
    SQLModel.metadata.create_all(rx.Model.get_db_engine())


create_db_and_tables()