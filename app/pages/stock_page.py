import reflex as rx
from app.states.auth_state import AuthState, require_auth
from app.states.product_state import ProductState
from app.components.base_layout import base_layout


def stock_row(stock: rx.Var[dict]) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            stock["product_name"],
            class_name="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900",
        ),
        rx.el.td(
            stock["branch_name"],
            class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-500",
        ),
        rx.el.td(
            rx.el.span(
                stock["quantity"],
                class_name=rx.cond(
                    stock["quantity"] < 10,
                    "px-3 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800",
                    "px-3 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800",
                ),
            ),
            class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-500",
        ),
        class_name="hover:bg-gray-50",
    )


def update_stock_form() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Update Stock Quantity",
            class_name="text-2xl font-semibold text-gray-700 mb-4",
        ),
        rx.el.div(
            rx.el.select(
                rx.el.option("Select Product", value=""),
                rx.foreach(
                    ProductState.products,
                    lambda p: rx.el.option(p["name"], value=p["id"].to_string()),
                ),
                on_change=ProductState.set_selected_product_id,
                class_name="px-4 py-2 border rounded-lg",
            ),
            rx.el.select(
                rx.el.option("Select Branch", value=""),
                rx.foreach(
                    AuthState.all_branches,
                    lambda b: rx.el.option(b["name"], value=b["id"].to_string()),
                ),
                on_change=ProductState.set_selected_branch_id,
                class_name="px-4 py-2 border rounded-lg",
            ),
            rx.el.input(
                placeholder="Quantity",
                type="number",
                on_change=ProductState.set_stock_quantity,
                class_name="px-4 py-2 border rounded-lg",
            ),
            rx.el.button(
                "Update Stock",
                on_click=ProductState.update_stock,
                class_name="px-6 py-2 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700",
            ),
            class_name="grid grid-cols-1 md:grid-cols-4 gap-4 items-center p-6 bg-white rounded-xl shadow",
        ),
    )


def transfer_stock_form() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Transfer Stock Between Branches",
            class_name="text-2xl font-semibold text-gray-700 mb-4 mt-8",
        ),
        rx.el.div(
            rx.el.select(
                rx.el.option("Select Product to Transfer", value=""),
                rx.foreach(
                    ProductState.products,
                    lambda p: rx.el.option(p["name"], value=p["id"].to_string()),
                ),
                on_change=ProductState.set_transfer_product_id,
                class_name="px-4 py-2 border rounded-lg w-full",
            ),
            rx.el.select(
                rx.el.option("From Branch", value=""),
                rx.foreach(
                    AuthState.all_branches,
                    lambda b: rx.el.option(b["name"], value=b["id"].to_string()),
                ),
                on_change=ProductState.set_transfer_from_branch_id,
                class_name="px-4 py-2 border rounded-lg w-full",
            ),
            rx.el.select(
                rx.el.option("To Branch", value=""),
                rx.foreach(
                    AuthState.all_branches,
                    lambda b: rx.el.option(b["name"], value=b["id"].to_string()),
                ),
                on_change=ProductState.set_transfer_to_branch_id,
                class_name="px-4 py-2 border rounded-lg w-full",
            ),
            rx.el.input(
                placeholder="Quantity",
                type="number",
                min=1,
                default_value=1,
                on_change=ProductState.set_transfer_quantity,
                class_name="px-4 py-2 border rounded-lg w-full",
            ),
            rx.el.button(
                "Transfer",
                on_click=ProductState.perform_stock_transfer,
                class_name="w-full px-6 py-2 bg-green-600 text-white font-semibold rounded-lg shadow-md hover:bg-green-700",
            ),
            class_name="grid grid-cols-1 md:grid-cols-5 gap-4 items-center p-6 bg-white rounded-xl shadow",
        ),
    )


@require_auth
def stock_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.h1(
                "Stock Management", class_name="text-4xl font-bold text-gray-800 mb-8"
            ),
            rx.cond(
                AuthState.is_admin,
                rx.fragment(update_stock_form(), transfer_stock_form()),
                None,
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.table(
                        rx.el.thead(
                            rx.el.tr(
                                rx.el.th(
                                    "Product",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Branch",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Quantity",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                            )
                        ),
                        rx.el.tbody(
                            rx.foreach(ProductState.stocks, stock_row),
                            class_name="bg-white divide-y divide-gray-200",
                        ),
                        class_name="min-w-full divide-y divide-gray-200",
                    ),
                    class_name="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg",
                ),
                class_name="overflow-x-auto mt-8",
            ),
            class_name="w-full",
            on_mount=[ProductState.load_products_and_stock, AuthState.load_all_data],
        )
    )