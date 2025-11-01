import reflex as rx
from app.states.auth_state import require_auth
from app.states.cash_closing_state import CashClosingState
from app.components.base_layout import base_layout


def cash_closing_form() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Cash Closing", class_name="text-3xl font-bold text-gray-800 mb-6"),
        rx.el.div(
            rx.el.div(
                rx.el.label("Period Type", class_name="font-medium text-gray-600"),
                rx.el.div(
                    rx.el.button(
                        "Weekly",
                        on_click=lambda: CashClosingState.set_period_type_and_fetch(
                            "weekly"
                        ),
                        class_name=rx.cond(
                            CashClosingState.period_type == "weekly",
                            "px-4 py-2 bg-blue-600 text-white rounded-l-lg",
                            "px-4 py-2 bg-gray-200 text-gray-700 rounded-l-lg",
                        ),
                    ),
                    rx.el.button(
                        "Monthly",
                        on_click=lambda: CashClosingState.set_period_type_and_fetch(
                            "monthly"
                        ),
                        class_name=rx.cond(
                            CashClosingState.period_type == "monthly",
                            "px-4 py-2 bg-blue-600 text-white rounded-r-lg",
                            "px-4 py-2 bg-gray-200 text-gray-700 rounded-r-lg",
                        ),
                    ),
                    class_name="flex mt-2",
                ),
            ),
            rx.el.div(
                rx.el.label("Start Date", class_name="font-medium text-gray-600"),
                rx.el.input(
                    type="date",
                    default_value=CashClosingState.start_date,
                    on_change=CashClosingState.set_start_date,
                    class_name="w-full px-4 py-2 bg-gray-100 rounded-lg border-gray-200 mt-2",
                ),
            ),
            rx.el.div(
                rx.el.label("End Date", class_name="font-medium text-gray-600"),
                rx.el.input(
                    type="date",
                    default_value=CashClosingState.end_date,
                    on_change=CashClosingState.set_end_date,
                    class_name="w-full px-4 py-2 bg-gray-100 rounded-lg border-gray-200 mt-2",
                ),
            ),
            rx.el.button(
                "Fetch Payments",
                on_click=CashClosingState.fetch_collected_payments,
                class_name="self-end px-6 py-2 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700",
            ),
            class_name="grid md:grid-cols-4 gap-6 items-center mb-8",
        ),
        rx.el.div(
            rx.el.h3(
                "Collected Payments",
                class_name="text-2xl font-semibold text-gray-700 mb-4",
            ),
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th("Customer"),
                            rx.el.th("Payment Type"),
                            rx.el.th("Amount"),
                            rx.el.th("Paid At"),
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(
                            CashClosingState.collected_payments,
                            lambda payment: rx.el.tr(
                                rx.el.td(payment["customer_name"]),
                                rx.el.td(payment["payment_type"]),
                                rx.el.td(f"${payment['amount'].to_string()}"),
                                rx.el.td(payment["paid_at"].to_string().split("T")[0]),
                                class_name="text-sm",
                            ),
                        )
                    ),
                    class_name="min-w-full divide-y divide-gray-200 text-left",
                ),
                class_name="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg mb-6",
            ),
            rx.el.div(
                rx.el.p(
                    f"Total Collected: ${CashClosingState.total_collected.to_string()}",
                    class_name="text-xl font-bold text-green-600",
                ),
                rx.el.button(
                    "Perform Cash Closing",
                    on_click=CashClosingState.perform_cash_closing,
                    class_name="px-8 py-3 bg-green-600 text-white font-bold rounded-lg shadow-lg hover:bg-green-700 text-lg",
                    disabled=CashClosingState.collected_payments.length() == 0,
                ),
                class_name="flex justify-between items-center mt-6",
            ),
        ),
        class_name="p-8 bg-white rounded-xl shadow-lg border w-full mb-12",
    )


def closings_history_table() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Cash Closing History",
            class_name="text-2xl font-semibold text-gray-700 my-8",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th("Collector"),
                            rx.el.th("Branch"),
                            rx.el.th("Period"),
                            rx.el.th("Date Range"),
                            rx.el.th("Total Collected"),
                            rx.el.th("Status"),
                            rx.el.th("Closed At"),
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(
                            CashClosingState.closings_history,
                            lambda item: rx.el.tr(
                                rx.el.td(item["user_name"]),
                                rx.el.td(item["branch_name"]),
                                rx.el.td(item["period_type"].to_string().capitalize()),
                                rx.el.td(
                                    f"{item['start_date'].to_string().split('T')[0]} - {item['end_date'].to_string().split('T')[0]}"
                                ),
                                rx.el.td(f"${item['total_collected'].to_string()}"),
                                rx.el.td(
                                    rx.el.span(
                                        item["status"],
                                        class_name="px-3 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800",
                                    )
                                ),
                                rx.el.td(item["created_at"].to_string().split("T")[0]),
                                class_name="hover:bg-gray-50 text-sm",
                            ),
                        )
                    ),
                    class_name="min-w-full divide-y divide-gray-200 text-left",
                ),
                class_name="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg",
            ),
            class_name="overflow-x-auto",
        ),
    )


@require_auth
def cash_closing_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.h1(
                "Cash Closing Management",
                class_name="text-4xl font-bold text-gray-800 mb-8",
            ),
            cash_closing_form(),
            closings_history_table(),
            on_mount=CashClosingState.on_page_load,
        )
    )