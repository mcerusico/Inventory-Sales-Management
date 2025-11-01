import reflex as rx
from app.states.auth_state import AuthState, require_auth
from app.states.customer_state import CustomerState
from app.components.base_layout import base_layout


def customer_row(customer: rx.Var[dict]) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            customer["name"],
            class_name="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900",
        ),
        rx.el.td(
            customer["email"],
            class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-500",
        ),
        rx.el.td(
            customer["phone"],
            class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-500",
        ),
        rx.el.td(
            customer["branch_name"],
            class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-500",
        ),
        rx.el.td(
            f"${customer['credit_balance'].to_string()}",
            class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-500",
        ),
        rx.el.td(
            rx.el.button(
                rx.icon("trash-2", class_name="w-4 h-4"),
                on_click=lambda: CustomerState.delete_customer(customer["id"]),
                class_name="text-red-600 hover:text-red-900",
            ),
            class_name="px-6 py-4 whitespace-nowrap text-right text-sm font-medium",
        ),
        class_name="hover:bg-gray-50",
    )


def add_customer_form() -> rx.Component:
    return rx.el.form(
        rx.el.div(
            rx.el.h2(
                "Add New Customer",
                class_name="text-2xl font-semibold text-gray-700 mb-4",
            ),
            rx.el.div(
                rx.el.input(
                    name="name",
                    placeholder="Full Name",
                    class_name="px-4 py-2 border rounded-lg w-full",
                ),
                rx.el.input(
                    name="email",
                    placeholder="Email Address",
                    type="email",
                    class_name="px-4 py-2 border rounded-lg w-full",
                ),
                rx.el.input(
                    name="phone",
                    placeholder="Phone Number",
                    class_name="px-4 py-2 border rounded-lg w-full",
                ),
                rx.el.input(
                    name="address",
                    placeholder="Address",
                    class_name="px-4 py-2 border rounded-lg w-full",
                ),
                rx.cond(
                    AuthState.is_admin,
                    rx.el.select(
                        rx.el.option("Assign to Branch", value=""),
                        rx.foreach(
                            AuthState.all_branches,
                            lambda b: rx.el.option(
                                b["name"], value=b["id"].to_string()
                            ),
                        ),
                        name="branch_id",
                        class_name="px-4 py-2 border rounded-lg w-full",
                    ),
                    None,
                ),
                class_name="grid md:grid-cols-2 gap-4 mb-4",
            ),
            rx.el.button(
                "Add Customer",
                type="submit",
                class_name="px-6 py-2 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700",
            ),
            class_name="p-6 bg-white rounded-xl shadow",
        ),
        on_submit=CustomerState.add_customer,
        reset_on_submit=True,
    )


@require_auth
def customers_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.h1(
                "Customer Management",
                class_name="text-4xl font-bold text-gray-800 mb-8",
            ),
            add_customer_form(),
            rx.el.div(
                rx.el.input(
                    placeholder="Search customers...",
                    on_change=CustomerState.set_search_query,
                    class_name="px-4 py-2 border rounded-lg w-full md:w-1/3",
                ),
                class_name="my-8",
            ),
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
                                    "Email",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Phone",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Branch",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Credit Balance",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(class_name="relative px-6 py-3"),
                            )
                        ),
                        rx.el.tbody(
                            rx.foreach(CustomerState.filtered_customers, customer_row),
                            class_name="bg-white divide-y divide-gray-200",
                        ),
                        class_name="min-w-full divide-y divide-gray-200",
                    ),
                    class_name="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg",
                ),
                class_name="overflow-x-auto mt-8",
            ),
            class_name="w-full",
            on_mount=[CustomerState.load_customers, AuthState.load_all_data],
        )
    )