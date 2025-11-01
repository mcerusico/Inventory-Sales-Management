import reflex as rx
from app.states.auth_state import AuthState, require_auth
from app.states.customer_state import CustomerState
from app.states.product_state import ProductState
from app.states.sales_state import SalesState
from app.components.base_layout import base_layout


def sale_entry_form() -> rx.Component:
    return rx.el.div(
        rx.el.h2("New Sale", class_name="text-2xl font-semibold text-gray-700 mb-6"),
        rx.el.div(
            rx.el.div(
                rx.el.select(
                    rx.el.option("Select Customer", value=""),
                    rx.foreach(
                        CustomerState.filtered_customers,
                        lambda c: rx.el.option(c["name"], value=c["id"].to_string()),
                    ),
                    on_change=SalesState.set_selected_customer_id,
                    value=SalesState.selected_customer_id,
                    class_name="w-full px-4 py-3 bg-gray-100 rounded-lg border-gray-200",
                ),
                rx.el.select(
                    rx.el.option("Select Product", value=""),
                    rx.foreach(
                        ProductState.products,
                        lambda p: rx.el.option(p["name"], value=p["id"].to_string()),
                    ),
                    on_change=SalesState.set_selected_product_id,
                    value=SalesState.selected_product_id,
                    class_name="w-full px-4 py-3 bg-gray-100 rounded-lg border-gray-200",
                ),
                rx.el.input(
                    type="number",
                    placeholder="Quantity",
                    default_value=SalesState.current_quantity.to_string(),
                    on_change=SalesState.set_current_quantity,
                    min=1,
                    class_name="w-full px-4 py-3 bg-gray-100 rounded-lg border-gray-200",
                ),
                rx.el.button(
                    rx.icon("circle_plus", class_name="mr-2"),
                    "Add to Cart",
                    on_click=SalesState.add_to_cart,
                    class_name="w-full flex items-center justify-center px-6 py-3 bg-blue-500 text-white font-semibold rounded-lg shadow-md hover:bg-blue-600",
                ),
                class_name="grid md:grid-cols-4 gap-4 items-center mb-6",
            ),
            rx.el.div(
                rx.el.h3("Cart", class_name="text-xl font-semibold text-gray-600 mb-4"),
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th("Product", class_name="px-4 py-2 text-left"),
                            rx.el.th("Qty", class_name="px-4 py-2 text-left"),
                            rx.el.th("Price", class_name="px-4 py-2 text-left"),
                            rx.el.th("Subtotal", class_name="px-4 py-2 text-left"),
                            rx.el.th(""),
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(
                            SalesState.cart,
                            lambda item: rx.el.tr(
                                rx.el.td(item["product_name"], class_name="px-4 py-2"),
                                rx.el.td(item["quantity"], class_name="px-4 py-2"),
                                rx.el.td(
                                    f"${item['price'].to_string()}",
                                    class_name="px-4 py-2",
                                ),
                                rx.el.td(
                                    f"${item['subtotal'].to_string()}",
                                    class_name="px-4 py-2",
                                ),
                                rx.el.td(
                                    rx.el.button(
                                        rx.icon("x", class_name="w-4 h-4 text-red-500"),
                                        on_click=lambda: SalesState.remove_from_cart(
                                            item["product_id"]
                                        ),
                                    )
                                ),
                            ),
                        )
                    ),
                ),
                rx.el.p(
                    f"Total: ${SalesState.cart_total.to_string()}",
                    class_name="text-right font-bold text-xl mt-4",
                ),
                class_name="bg-white p-4 rounded-lg shadow-sm border mb-6",
            ),
            rx.el.div(
                rx.el.h3(
                    "Payment", class_name="text-xl font-semibold text-gray-600 mb-4"
                ),
                rx.el.select(
                    rx.el.option("Cash", value="cash"),
                    rx.el.option("Card", value="card"),
                    rx.el.option("Weekly Installments", value="weekly"),
                    rx.el.option("Monthly Installments", value="monthly"),
                    value=SalesState.payment_method,
                    on_change=SalesState.set_payment_method,
                    class_name="w-full px-4 py-3 bg-gray-100 rounded-lg border-gray-200",
                ),
                rx.cond(
                    (SalesState.payment_method == "weekly")
                    | (SalesState.payment_method == "monthly"),
                    rx.el.div(
                        rx.el.input(
                            type="number",
                            placeholder="Number of Installments",
                            default_value=SalesState.num_installments.to_string(),
                            on_change=SalesState.set_num_installments,
                            min=1,
                            class_name="w-full px-4 py-3 bg-gray-100 rounded-lg border-gray-200",
                        ),
                        rx.el.p(
                            f"Installment Amount: ${SalesState.installment_amount.to_string()}",
                            class_name="mt-2 text-gray-600",
                        ),
                        class_name="mt-4",
                    ),
                    None,
                ),
                class_name="mb-6",
            ),
            rx.el.button(
                "Complete Sale",
                on_click=SalesState.create_sale,
                class_name="w-full px-6 py-4 bg-green-600 text-white font-bold rounded-lg shadow-lg hover:bg-green-700 text-lg",
            ),
        ),
        class_name="p-8 bg-white rounded-xl shadow-lg border w-full",
    )


def sales_history_table() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Sales History", class_name="text-2xl font-semibold text-gray-700 my-8"
        ),
        rx.el.div(
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                "Customer",
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Seller",
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Branch",
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Total",
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Payment",
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Status",
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Date",
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(
                            SalesState.sales,
                            lambda sale: rx.el.tr(
                                rx.el.td(
                                    sale["customer_name"],
                                    class_name="px-6 py-4 whitespace-nowrap",
                                ),
                                rx.el.td(
                                    sale["user_username"],
                                    class_name="px-6 py-4 whitespace-nowrap",
                                ),
                                rx.el.td(
                                    sale["branch_name"],
                                    class_name="px-6 py-4 whitespace-nowrap",
                                ),
                                rx.el.td(
                                    f"${sale['total_amount'].to_string()}",
                                    class_name="px-6 py-4 whitespace-nowrap",
                                ),
                                rx.el.td(
                                    sale["payment_method"].to_string().capitalize(),
                                    class_name="px-6 py-4 whitespace-nowrap",
                                ),
                                rx.el.td(
                                    rx.el.span(
                                        sale["status"],
                                        class_name=rx.cond(
                                            sale["status"] == "Paid",
                                            "px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800",
                                            "px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800",
                                        ),
                                    ),
                                    class_name="px-6 py-4 whitespace-nowrap",
                                ),
                                rx.el.td(
                                    sale["created_at"].to_string().split("T")[0],
                                    class_name="px-6 py-4 whitespace-nowrap",
                                ),
                            ),
                        ),
                        class_name="bg-white divide-y divide-gray-200",
                    ),
                    class_name="min-w-full divide-y divide-gray-200",
                ),
                class_name="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg",
            ),
            class_name="overflow-x-auto",
        ),
        class_name="w-full",
    )


@require_auth
def sales_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.h1(
                "Sales Management", class_name="text-4xl font-bold text-gray-800 mb-8"
            ),
            sale_entry_form(),
            sales_history_table(),
            on_mount=[
                SalesState.load_sales,
                CustomerState.load_customers,
                ProductState.load_products_and_stock,
            ],
        )
    )