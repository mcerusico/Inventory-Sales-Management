import reflex as rx
from app.components.base_layout import base_layout


def protected_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.div(
                rx.icon("lock", class_name="w-16 h-16 text-red-500 mx-auto mb-6"),
                rx.el.h1(
                    "Access Denied",
                    class_name="text-4xl font-bold text-gray-800 text-center mb-4",
                ),
                rx.el.p(
                    "You do not have the necessary permissions to view this page.",
                    class_name="text-lg text-gray-600 text-center mb-8",
                ),
                rx.el.a(
                    "Go to Dashboard",
                    href="/dashboard",
                    class_name="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 transition",
                ),
                class_name="flex flex-col items-center",
            ),
            class_name="max-w-2xl mx-auto mt-20 p-12 bg-white rounded-xl shadow-lg border",
        )
    )


def protected_page_redirect() -> rx.Component:
    return rx.el.div(on_mount=rx.redirect("/login"))