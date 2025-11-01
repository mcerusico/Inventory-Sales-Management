import reflex as rx
from typing import Literal, cast, TypedDict
from sqlmodel import select
from app.db_models import User, Branch, UserDict, BranchDict
import bcrypt
import sqlalchemy as sa


class CurrentUser(TypedDict):
    id: int
    username: str
    role: str
    branch_id: int | None
    branch_name: str | None


def require_auth(page):
    def check_auth_and_return_page(*args, **kwargs):
        from app.pages.protected_page import protected_page_redirect

        return rx.cond(
            AuthState.is_authenticated, page(*args, **kwargs), protected_page_redirect()
        )

    return check_auth_and_return_page


def admin_only(page):
    def check_admin_and_return_page(*args, **kwargs):
        from app.pages.protected_page import protected_page

        return rx.cond(AuthState.is_admin, page(*args, **kwargs), protected_page())

    return check_admin_and_return_page


class AuthState(rx.State):
    is_authenticated: bool = False
    current_user: CurrentUser | None = None
    error_message: str = ""
    all_users: list[UserDict] = []
    all_branches: list[BranchDict] = []
    new_branch_name: str = ""
    new_branch_location: str = ""
    editing_branch_id: int | None = None
    editing_branch_name: str = ""
    editing_user_id: int | None = None
    editing_user_role: str = ""
    editing_user_branch: str = ""

    @rx.var
    def is_admin(self) -> bool:
        return self.current_user is not None and self.current_user["role"] == "admin"

    def _hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def _verify_password(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed_password.encode())

    @rx.event
    def check_login(self):
        if not self.is_authenticated and self.router.page.path != "/login":
            return rx.redirect("/login")

    @rx.event(background=True)
    async def login(self, form_data: dict):
        username = form_data["username"]
        password = form_data["password"]
        async with self:
            self.error_message = ""
            with rx.session() as session:
                user = session.exec(
                    select(User).where(User.username == username)
                ).first()
                if user and self._verify_password(password, user.password_hash):
                    branch_name = (
                        session.exec(
                            select(Branch.name).where(Branch.id == user.branch_id)
                        ).first()
                        if user.branch_id
                        else None
                    )
                    self.is_authenticated = True
                    self.current_user = {
                        "id": user.id,
                        "username": user.username,
                        "role": user.role,
                        "branch_id": user.branch_id,
                        "branch_name": branch_name,
                    }
                    return rx.redirect("/dashboard")
                else:
                    self.error_message = "Invalid username or password."
                    return rx.toast.error(self.error_message, duration=3000)

    @rx.event
    def logout(self):
        self.is_authenticated = False
        self.current_user = None
        return rx.redirect("/login")

    @rx.event
    async def load_all_data(self):
        with rx.session() as session:
            branches = session.exec(select(Branch)).all()
            self.all_branches = [b.dict() for b in branches]
        if self.current_user and self.current_user["role"] == "admin":
            users = session.exec(
                select(User).options(sa.orm.selectinload(User.branch))
            ).all()
            self.all_users = []
            for u in users:
                user_dict = u.dict()
                user_dict["branch"] = u.branch.dict() if u.branch else None
                self.all_users.append(user_dict)

    @rx.event(background=True)
    async def add_branch(self):
        async with self:
            with rx.session() as session:
                if not self.new_branch_name:
                    yield rx.toast.error("Branch name cannot be empty.", duration=3000)
                    return
                branch_exists = session.exec(
                    select(Branch).where(Branch.name == self.new_branch_name)
                ).first()
                if branch_exists:
                    yield rx.toast.error(
                        f"Branch '{self.new_branch_name}' already exists.",
                        duration=3000,
                    )
                    return
                new_branch = Branch(
                    name=self.new_branch_name, location=self.new_branch_location
                )
                session.add(new_branch)
                session.commit()
                self.new_branch_name = ""
                self.new_branch_location = ""
        yield AuthState.load_all_data()
        yield rx.toast.success("Branch added successfully.", duration=3000)

    @rx.event(background=True)
    async def delete_branch(self, branch_id: int):
        async with self:
            with rx.session() as session:
                branch_to_delete = session.get(Branch, branch_id)
                if branch_to_delete:
                    if branch_to_delete.users:
                        yield rx.toast.error(
                            "Cannot delete branch with assigned users.", duration=4000
                        )
                        return
                    session.delete(branch_to_delete)
                    session.commit()
        yield AuthState.load_all_data()
        yield rx.toast.success("Branch deleted.", duration=3000)

    @rx.event(background=True)
    async def delete_user(self, user_id: int):
        async with self:
            with rx.session() as session:
                user_to_delete = session.get(User, user_id)
                if user_to_delete and user_to_delete.id != self.current_user["id"]:
                    session.delete(user_to_delete)
                    session.commit()
                else:
                    yield rx.toast.error(
                        "Cannot delete the currently logged in user.", duration=4000
                    )
                    return
        yield AuthState.load_all_data()
        yield rx.toast.success("User deleted.", duration=3000)

    @rx.event(background=True)
    async def admin_create_user(self, form_data: dict):
        username = form_data.get("username")
        password = form_data.get("password")
        role = form_data.get("role")
        branch_id_str = form_data.get("branch_id")
        if not all([username, password, role]):
            yield rx.toast.error("Username, password, and role are required.")
            return
        branch_id = (
            int(branch_id_str) if branch_id_str and branch_id_str.isdigit() else None
        )
        if role == "seller" and (not branch_id):
            yield rx.toast.error("Sellers must be assigned to a branch.")
            return
        async with self:
            with rx.session() as session:
                user_exists = session.exec(
                    select(User).where(User.username == username)
                ).first()
                if user_exists:
                    yield rx.toast.error(f"Username '{username}' already exists.")
                    return
                new_user = User(
                    username=username,
                    password_hash=self._hash_password(password),
                    role=role,
                    branch_id=branch_id,
                )
                session.add(new_user)
                session.commit()
        yield AuthState.load_all_data()
        yield rx.toast.success(f"User '{username}' created successfully.")