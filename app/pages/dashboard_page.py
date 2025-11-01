import reflex as rx
from app.states.auth_state import AuthState, require_auth
from app.states.dashboard_state import DashboardState
from app.components.base_layout import base_layout


def metric_card(icon: str, title: str, value: rx.Var[str]) -> rx.Component:
    return rx.el.div(
        rx.el.div(rx.icon(icon, class_name="w-8 h-8 text-blue-600")),
        rx.el.div(
            rx.el.h3(title, class_name="text-sm font-medium text-gray-500"),
            rx.el.p(value, class_name="text-2xl font-bold text-gray-800"),
        ),
        class_name="flex items-center gap-4 p-6 bg-white rounded-xl shadow-sm border border-gray-100",
    )


def admin_dashboard() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Admin Overview", class_name="text-3xl font-bold text-gray-800 mb-6"),
        rx.el.div(
            metric_card(
                "dollar-sign",
                "Total Revenue",
                f"${DashboardState.admin_metrics['total_revenue'].to_string()}",
            ),
            metric_card(
                "shopping-cart",
                "Total Sales",
                DashboardState.admin_metrics["total_sales"].to_string(),
            ),
            metric_card(
                "users",
                "Total Customers",
                DashboardState.admin_metrics["total_customers"].to_string(),
            ),
            metric_card(
                "badge_alert",
                "Pending Installments",
                DashboardState.admin_metrics["pending_installments"].to_string(),
            ),
            class_name="grid md:grid-cols-2 lg:grid-cols-4 gap-6",
        ),
    )


def seller_dashboard() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Your Performance", class_name="text-3xl font-bold text-gray-800 mb-6"
        ),
        rx.el.div(
            metric_card(
                "dollar-sign",
                "Your Revenue",
                f"${DashboardState.seller_metrics['total_revenue'].to_string()}",
            ),
            metric_card(
                "shopping-cart",
                "Your Sales",
                DashboardState.seller_metrics["total_sales"].to_string(),
            ),
            metric_card(
                "users",
                "Your Customers",
                DashboardState.seller_metrics["total_customers"].to_string(),
            ),
            metric_card(
                "badge_alert",
                "Your Pending Installments",
                DashboardState.seller_metrics["pending_installments"].to_string(),
            ),
            class_name="grid md:grid-cols-2 lg:grid-cols-4 gap-6",
        ),
    )


@require_auth
def dashboard_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.h1("Dashboard", class_name="text-4xl font-bold text-gray-800 mb-4"),
            rx.el.p(
                f"Welcome, {AuthState.current_user['username']}!",
                class_name="text-lg text-gray-600 mb-8",
            ),
            rx.cond(AuthState.is_admin, admin_dashboard(), seller_dashboard()),
            on_mount=DashboardState.load_metrics,
        )
    )