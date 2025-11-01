import reflex as rx
from app.states.auth_state import AuthState, require_auth, admin_only
from app.components.base_layout import base_layout


def branch_row(branch: rx.Var[dict]) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            branch["name"],
            class_name="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900",
        ),
        rx.el.td(
            branch["location"],
            class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-500",
        ),
        rx.el.td(
            branch["created_at"].to_string().split("T")[0],
            class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-500",
        ),
        rx.el.td(
            rx.el.button(
                rx.icon("trash-2", class_name="w-4 h-4"),
                on_click=lambda: AuthState.delete_branch(branch["id"]),
                class_name="text-red-600 hover:text-red-900",
            ),
            class_name="px-6 py-4 whitespace-nowrap text-right text-sm font-medium",
        ),
        class_name="hover:bg-gray-50",
    )


@require_auth
@admin_only
def branches_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.h1(
                "Branch Management", class_name="text-4xl font-bold text-gray-800 mb-8"
            ),
            rx.el.div(
                rx.el.h2(
                    "Add New Branch",
                    class_name="text-2xl font-semibold text-gray-700 mb-4",
                ),
                rx.el.div(
                    rx.el.input(
                        placeholder="Branch Name",
                        on_change=AuthState.set_new_branch_name,
                        class_name="px-4 py-2 border rounded-lg focus:ring-blue-500 focus:border-blue-500",
                        default_value=AuthState.new_branch_name,
                    ),
                    rx.el.input(
                        placeholder="Location (Optional)",
                        on_change=AuthState.set_new_branch_location,
                        class_name="px-4 py-2 border rounded-lg focus:ring-blue-500 focus:border-blue-500",
                        default_value=AuthState.new_branch_location,
                    ),
                    rx.el.button(
                        "Add Branch",
                        on_click=AuthState.add_branch,
                        class_name="px-6 py-2 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700",
                    ),
                    class_name="flex items-center gap-4 p-6 bg-white rounded-xl shadow",
                ),
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
                                    "Location",
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
                            rx.foreach(AuthState.all_branches, branch_row),
                            class_name="bg-white divide-y divide-gray-200",
                        ),
                        class_name="min-w-full divide-y divide-gray-200",
                    ),
                    class_name="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg",
                ),
                class_name="overflow-x-auto",
            ),
            class_name="mt-8",
            on_mount=AuthState.load_all_data,
        )
    )