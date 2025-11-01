import reflex as rx
from app.states.auth_state import AuthState


def login_form() -> rx.Component:
    return rx.el.form(
        rx.el.div(
            rx.el.h2("Login", class_name="text-3xl font-bold text-gray-800 mb-2"),
            rx.el.p("Welcome back to StockFlow.", class_name="text-gray-500 mb-8"),
            rx.el.label(
                "Username", class_name="text-sm font-medium text-gray-700 mb-2 block"
            ),
            rx.el.input(
                name="username",
                placeholder="Enter your username",
                class_name="w-full px-4 py-3 bg-gray-100 rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition",
            ),
            rx.el.label(
                "Password",
                class_name="text-sm font-medium text-gray-700 mb-2 mt-4 block",
            ),
            rx.el.input(
                name="password",
                type="password",
                placeholder="Enter your password",
                class_name="w-full px-4 py-3 bg-gray-100 rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition",
            ),
            rx.cond(
                AuthState.error_message != "",
                rx.el.p(
                    AuthState.error_message, class_name="text-red-500 text-sm mt-4"
                ),
                None,
            ),
            rx.el.button(
                "Sign In",
                type="submit",
                class_name="w-full mt-8 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 transition-all duration-300",
            ),
            class_name="flex flex-col",
        ),
        on_submit=AuthState.login,
        reset_on_submit=True,
    )


def login_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    login_form(),
                    class_name="w-full max-w-md bg-white p-8 md:p-12 rounded-2xl shadow-xl",
                ),
                class_name="w-full lg:w-1/2 flex items-center justify-center p-8",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.h1(
                        "Manage your inventory with ease.",
                        class_name="text-5xl font-extrabold text-white mb-6",
                    ),
                    rx.el.p(
                        "StockFlow gives you the power to track sales, manage stock, and grow your business.",
                        class_name="text-blue-100 text-lg",
                    ),
                ),
                class_name="hidden lg:flex w-1/2 bg-blue-600 items-center justify-center p-12 flex-col text-center",
            ),
            class_name="flex flex-row min-h-screen font-['Montserrat']",
            on_mount=AuthState.load_all_data,
        )
    )