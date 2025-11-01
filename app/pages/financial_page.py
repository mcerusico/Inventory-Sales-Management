import reflex as rx
from app.states.auth_state import AuthState, require_auth
from app.states.customer_state import CustomerState
from app.states.financial_state import FinancialState
from app.components.base_layout import base_layout


def new_financial_payment_form() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "New Financial Payment",
            class_name="text-2xl font-semibold text-gray-700 mb-6",
        ),
        rx.el.div(
            rx.el.select(
                rx.el.option("Select Customer", value=""),
                rx.foreach(
                    CustomerState.filtered_customers,
                    lambda c: rx.el.option(c["name"], value=c["id"].to_string()),
                ),
                on_change=FinancialState.set_selected_customer_id,
                value=FinancialState.selected_customer_id,
                class_name="w-full px-4 py-3 bg-gray-100 rounded-lg border-gray-200",
            ),
            rx.el.input(
                placeholder="Principal Amount",
                type="number",
                on_change=FinancialState.set_principal_amount,
                default_value=FinancialState.principal_amount.to_string(),
                class_name="w-full px-4 py-3 bg-gray-100 rounded-lg border-gray-200",
            ),
            rx.el.input(
                placeholder="Interest Rate (%)",
                type="number",
                on_change=FinancialState.set_interest_rate,
                default_value=FinancialState.interest_rate.to_string(),
                class_name="w-full px-4 py-3 bg-gray-100 rounded-lg border-gray-200",
            ),
            class_name="grid md:grid-cols-3 gap-4 mb-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.label("Installment Type", class_name="font-medium text-gray-600"),
                rx.el.div(
                    rx.el.label(
                        rx.el.input(
                            type="radio",
                            name="installment_type",
                            value="weekly",
                            on_change=FinancialState.set_installment_type,
                            checked=FinancialState.installment_type == "weekly",
                        ),
                        " Weekly",
                        class_name="mr-4",
                    ),
                    rx.el.label(
                        rx.el.input(
                            type="radio",
                            name="installment_type",
                            value="monthly",
                            on_change=FinancialState.set_installment_type,
                            checked=FinancialState.installment_type == "monthly",
                        ),
                        " Monthly",
                    ),
                    class_name="flex items-center mt-2",
                ),
            ),
            rx.el.div(
                rx.el.label(
                    "Number of Installments", class_name="font-medium text-gray-600"
                ),
                rx.el.input(
                    type="number",
                    min=1,
                    on_change=FinancialState.set_num_installments,
                    default_value=FinancialState.num_installments.to_string(),
                    class_name="w-full px-4 py-3 bg-gray-100 rounded-lg border-gray-200 mt-2",
                ),
            ),
            class_name="grid md:grid-cols-2 gap-4 mb-6 items-center",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p("Total Amount (with interest):", class_name="font-semibold"),
                rx.el.p(
                    f"${FinancialState.total_amount.to_string()}",
                    class_name="text-xl font-bold text-blue-600",
                ),
                class_name="p-4 bg-blue-50 rounded-lg text-center",
            ),
            rx.el.div(
                rx.el.p("Installment Amount:", class_name="font-semibold"),
                rx.el.p(
                    f"${FinancialState.installment_amount.to_string()}",
                    class_name="text-xl font-bold text-green-600",
                ),
                class_name="p-4 bg-green-50 rounded-lg text-center",
            ),
            class_name="grid md:grid-cols-2 gap-4 mb-6",
        ),
        rx.el.button(
            "Create Payment Plan",
            on_click=FinancialState.create_financial_payment,
            class_name="w-full px-6 py-4 bg-blue-600 text-white font-bold rounded-lg shadow-lg hover:bg-blue-700 text-lg",
        ),
        class_name="p-8 bg-white rounded-xl shadow-lg border w-full mb-12",
    )


def status_badge(status: rx.Var[str]) -> rx.Component:
    return rx.el.span(
        status,
        class_name=rx.match(
            status,
            (
                "Active",
                "px-3 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800",
            ),
            (
                "Completed",
                "px-3 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800",
            ),
            (
                "Overdue",
                "px-3 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800",
            ),
            (
                "Paid",
                "px-3 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800",
            ),
            (
                "Pending",
                "px-3 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800",
            ),
            "px-3 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800",
        ),
    )


def installment_details_view() -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            rx.el.div(
                rx.el.h3(
                    "Installment Schedule", class_name="text-lg font-semibold mb-4"
                ),
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th("#"),
                            rx.el.th("Due Date"),
                            rx.el.th("Amount Due"),
                            rx.el.th("Status"),
                            rx.el.th("Action"),
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(
                            FinancialState.selected_payment_installments,
                            lambda inst: rx.el.tr(
                                rx.el.td(inst["installment_number"]),
                                rx.el.td(inst["due_date"].to_string().split("T")[0]),
                                rx.el.td(f"${inst['amount_due'].to_string()}"),
                                rx.el.td(status_badge(inst["status"])),
                                rx.el.td(
                                    rx.cond(
                                        inst["status"] == "Pending",
                                        rx.el.button(
                                            "Mark as Paid",
                                            on_click=lambda: FinancialState.mark_installment_paid(
                                                inst["id"]
                                            ),
                                            class_name="px-3 py-1 bg-green-500 text-white text-xs rounded-md hover:bg-green-600",
                                        ),
                                        None,
                                    )
                                ),
                                class_name="text-sm",
                            ),
                        )
                    ),
                    class_name="min-w-full divide-y divide-gray-200",
                ),
                class_name="p-6 bg-gray-50 rounded-lg",
            ),
            col_span=8,
            class_name="p-0",
        )
    )


def financial_history_table() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Financial Payments History",
            class_name="text-2xl font-semibold text-gray-700 my-8",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th("Customer"),
                            rx.el.th("Principal"),
                            rx.el.th("Interest"),
                            rx.el.th("Total"),
                            rx.el.th("Plan"),
                            rx.el.th("Status"),
                            rx.el.th("Date"),
                            rx.el.th(""),
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(
                            FinancialState.financial_payments,
                            lambda payment: rx.fragment(
                                rx.el.tr(
                                    rx.el.td(payment["customer_name"]),
                                    rx.el.td(
                                        f"${payment['principal_amount'].to_string()}"
                                    ),
                                    rx.el.td(
                                        f"{payment['interest_rate'].to_string()}%"
                                    ),
                                    rx.el.td(f"${payment['total_amount'].to_string()}"),
                                    rx.el.td(
                                        f"{payment['num_installments']} {payment['installment_type']}"
                                    ),
                                    rx.el.td(status_badge(payment["status"])),
                                    rx.el.td(
                                        payment["created_at"].to_string().split("T")[0]
                                    ),
                                    rx.el.td(
                                        rx.el.button(
                                            rx.icon("chevron-down"),
                                            on_click=lambda: FinancialState.toggle_installments_view(
                                                payment["id"]
                                            ),
                                        )
                                    ),
                                    class_name="hover:bg-gray-50 cursor-pointer text-sm",
                                    on_click=lambda: FinancialState.toggle_installments_view(
                                        payment["id"]
                                    ),
                                ),
                                rx.cond(
                                    FinancialState.show_installments_for_payment_id
                                    == payment["id"],
                                    installment_details_view(),
                                    None,
                                ),
                            ),
                        ),
                        class_name="bg-white divide-y divide-gray-200",
                    ),
                    class_name="min-w-full divide-y divide-gray-200 text-left",
                ),
                class_name="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg",
            ),
            class_name="overflow-x-auto",
        ),
        class_name="w-full",
    )


@require_auth
def financial_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.h1(
                "Financial Management",
                class_name="text-4xl font-bold text-gray-800 mb-8",
            ),
            new_financial_payment_form(),
            financial_history_table(),
            on_mount=[
                FinancialState.load_financial_payments,
                CustomerState.load_customers,
            ],
        )
    )