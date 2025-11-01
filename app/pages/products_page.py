import reflex as rx
from app.states.auth_state import require_auth, admin_only
from app.states.product_state import ProductState
from app.components.base_layout import base_layout


def product_row(product: rx.Var[dict]) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            product["name"],
            class_name="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900",
        ),
        rx.el.td(
            product["category"],
            class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-500",
        ),
        rx.el.td(
            f"${product['price'].to_string()}",
            class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-500",
        ),
        rx.el.td(
            product["created_at"].to_string().split("T")[0],
            class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-500",
        ),
        rx.el.td(
            rx.el.button(
                rx.icon("trash-2", class_name="w-4 h-4"),
                on_click=lambda: ProductState.delete_product(product["id"]),
                class_name="text-red-600 hover:text-red-900",
            ),
            class_name="px-6 py-4 whitespace-nowrap text-right text-sm font-medium",
        ),
        class_name="hover:bg-gray-50",
    )


def add_product_form() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Add New Product", class_name="text-2xl font-semibold text-gray-700 mb-4"
        ),
        rx.el.div(
            rx.el.input(
                placeholder="Product Name",
                on_change=ProductState.set_new_product_name,
                default_value=ProductState.new_product_name,
                class_name="px-4 py-2 border rounded-lg",
            ),
            rx.el.input(
                placeholder="Category",
                on_change=ProductState.set_new_product_category,
                default_value=ProductState.new_product_category,
                class_name="px-4 py-2 border rounded-lg",
            ),
            rx.el.input(
                placeholder="Price",
                type="number",
                on_change=ProductState.set_new_product_price,
                default_value=ProductState.new_product_price,
                class_name="px-4 py-2 border rounded-lg",
            ),
            rx.el.input(
                placeholder="Description",
                on_change=ProductState.set_new_product_description,
                default_value=ProductState.new_product_description,
                class_name="px-4 py-2 border rounded-lg col-span-3",
            ),
            rx.el.button(
                "Add Product",
                on_click=ProductState.add_product,
                class_name="px-6 py-2 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700",
            ),
            class_name="grid grid-cols-1 md:grid-cols-4 gap-4 items-center p-6 bg-white rounded-xl shadow",
        ),
    )


@require_auth
@admin_only
def products_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.h1(
                "Product Management", class_name="text-4xl font-bold text-gray-800 mb-8"
            ),
            add_product_form(),
            rx.el.div(
                rx.el.div(
                    rx.el.table(
                        rx.el.thead(
                            rx.el.tr(
                                rx.el.th(
                                    "Name",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Category",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Price",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Created At",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(class_name="relative px-6 py-3"),
                            )
                        ),
                        rx.el.tbody(
                            rx.foreach(ProductState.products, product_row),
                            class_name="bg-white divide-y divide-gray-200",
                        ),
                        class_name="min-w-full divide-y divide-gray-200",
                    ),
                    class_name="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg",
                ),
                class_name="overflow-x-auto mt-8",
            ),
            class_name="w-full",
            on_mount=ProductState.load_products_and_stock,
        )
    )