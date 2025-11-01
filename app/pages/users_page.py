import reflex as rx
from app.states.auth_state import AuthState, require_auth, admin_only
from app.components.base_layout import base_layout


def user_row(user: rx.Var[dict]) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            user["username"],
            class_name="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900",
        ),
        rx.el.td(
            rx.el.span(
                user["role"].to_string().capitalize(),
                class_name=rx.cond(
                    user["role"] == "admin",
                    "px-3 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800",
                    "px-3 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800",
                ),
            ),
            class_name="px-6 py-4 whitespace-nowrap text-sm",
        ),
        rx.el.td(
            rx.cond(user["branch"], user["branch"]["name"], "N/A"),
            class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-500",
        ),
        rx.el.td(
            user["created_at"].to_string().split("T")[0],
            class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-500",
        ),
        rx.el.td(
            rx.el.button(
                rx.icon("trash-2", class_name="w-4 h-4"),
                on_click=lambda: AuthState.delete_user(user["id"]),
                class_name="text-red-600 hover:text-red-900",
                disabled=user["id"] == AuthState.current_user["id"],
            ),
            class_name="px-6 py-4 whitespace-nowrap text-right text-sm font-medium",
        ),
        class_name="hover:bg-gray-50",
    )


def add_user_form() -> rx.Component:
    return rx.el.form(
        rx.el.div(
            rx.el.h2(
                "Create New User",
                class_name="text-2xl font-semibold text-gray-700 mb-4",
            ),
            rx.el.div(
                rx.el.input(
                    name="username",
                    placeholder="Username",
                    class_name="px-4 py-2 border rounded-lg w-full",
                ),
                rx.el.input(
                    name="password",
                    type="password",
                    placeholder="Password",
                    class_name="px-4 py-2 border rounded-lg w-full",
                ),
                rx.el.select(
                    rx.el.option("Seller", value="seller"),
                    rx.el.option("Admin", value="admin"),
                    name="role",
                    class_name="px-4 py-2 border rounded-lg w-full",
                ),
                rx.el.select(
                    rx.el.option("Assign to Branch", value=""),
                    rx.foreach(
                        AuthState.all_branches,
                        lambda b: rx.el.option(b["name"], value=b["id"].to_string()),
                    ),
                    name="branch_id",
                    class_name="px-4 py-2 border rounded-lg w-full",
                ),
                rx.el.button(
                    "Create User",
                    type="submit",
                    class_name="w-full px-6 py-2 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700",
                ),
                class_name="grid md:grid-cols-5 gap-4 items-center",
            ),
            class_name="p-6 bg-white rounded-xl shadow",
        ),
        on_submit=AuthState.admin_create_user,
        reset_on_submit=True,
    )


@require_auth
@admin_only
def users_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.h1(
                "User Management", class_name="text-4xl font-bold text-gray-800 mb-8"
            ),
            add_user_form(),
            rx.el.div(
                rx.el.h2(
                    "All Users",
                    class_name="text-2xl font-semibold text-gray-700 mt-12 mb-4",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.table(
                            rx.el.thead(
                                rx.el.tr(
                                    rx.el.th(
                                        "Username",
                                        class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                    ),
                                    rx.el.th(
                                        "Role",
                                        class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                    ),
                                    rx.el.th(
                                        "Branch",
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
                                rx.foreach(AuthState.all_users, user_row),
                                class_name="bg-white divide-y divide-gray-200",
                            ),
                            class_name="min-w-full divide-y divide-gray-200",
                        ),
                        class_name="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg",
                    ),
                    class_name="overflow-x-auto",
                ),
            ),
            on_mount=AuthState.load_all_data,
        )
    )