import reflex as rx
from app.components.navbar import navbar


def base_layout(page_content: rx.Component) -> rx.Component:
    return rx.el.div(
        navbar(),
        rx.el.main(
            rx.el.div(page_content, class_name="container mx-auto p-4 md:p-8"),
            class_name="flex-grow w-full",
        ),
        class_name="flex flex-col min-h-screen bg-gray-50 font-['Montserrat']",
    )