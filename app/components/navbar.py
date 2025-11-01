import reflex as rx
from app.states.auth_state import AuthState


def nav_item(text: str, href: str, is_active: rx.Var[bool]) -> rx.Component:
    return rx.el.a(
        rx.el.li(
            text,
            class_name=rx.cond(
                is_active,
                "px-4 py-2 rounded-lg bg-blue-100 text-blue-700 font-semibold",
                "px-4 py-2 rounded-lg hover:bg-gray-100 text-gray-600 font-medium",
            ),
        ),
        href=href,
    )


def navbar() -> rx.Component:
    return rx.el.header(
        rx.el.nav(
            rx.el.a(
                rx.el.div(
                    rx.icon("store", class_name="w-8 h-8 text-blue-600"),
                    rx.el.span(
                        "StockFlow",
                        class_name="text-2xl font-bold text-gray-800 tracking-tighter",
                    ),
                    class_name="flex items-center gap-3",
                ),
                href="/dashboard",
            ),
            rx.el.ul(
                nav_item(
                    "Dashboard",
                    "/dashboard",
                    AuthState.router.page.path == "/dashboard",
                ),
                rx.cond(
                    AuthState.is_admin,
                    rx.fragment(
                        nav_item(
                            "Users", "/users", AuthState.router.page.path == "/users"
                        ),
                        nav_item(
                            "Branches",
                            "/branches",
                            AuthState.router.page.path == "/branches",
                        ),
                        nav_item(
                            "Products",
                            "/products",
                            AuthState.router.page.path == "/products",
                        ),
                    ),
                    None,
                ),
                nav_item(
                    "Customers",
                    "/customers",
                    AuthState.router.page.path == "/customers",
                ),
                nav_item("Stock", "/stock", AuthState.router.page.path == "/stock"),
                nav_item("Sales", "/sales", AuthState.router.page.path == "/sales"),
                nav_item(
                    "Financial",
                    "/financial",
                    AuthState.router.page.path == "/financial",
                ),
                nav_item(
                    "Cash Closing",
                    "/cash-closing",
                    AuthState.router.page.path == "/cash-closing",
                ),
                class_name="flex items-center gap-2",
            ),
            rx.el.div(
                rx.cond(
                    AuthState.is_authenticated,
                    rx.el.div(
                        rx.el.div(
                            rx.el.p(
                                AuthState.current_user["username"],
                                class_name="font-semibold text-gray-700",
                            ),
                            rx.el.p(
                                rx.cond(
                                    AuthState.current_user["branch_name"],
                                    AuthState.current_user["branch_name"],
                                    "No Branch",
                                ),
                                class_name="text-sm text-gray-500",
                            ),
                            class_name="text-right",
                        ),
                        rx.el.button(
                            rx.icon("log-out", class_name="w-5 h-5 mr-2"),
                            "Logout",
                            on_click=AuthState.logout,
                            class_name="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium shadow-sm",
                        ),
                        class_name="flex items-center gap-4",
                    ),
                    None,
                ),
                class_name="flex items-center",
            ),
            class_name="container mx-auto flex items-center justify-between p-4",
        ),
        class_name="w-full bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50 font-['Montserrat'] shadow-sm",
    )