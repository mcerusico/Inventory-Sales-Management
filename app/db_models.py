from datetime import datetime
from typing import TypedDict, Optional
import sqlalchemy as sql
from sqlmodel import Field, Relationship, SQLModel


class Branch(SQLModel, table=True):
    __tablename__ = "branches"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(
        sa_column=sql.Column(sql.String, unique=True, nullable=False, index=True)
    )
    location: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    users: list["User"] = Relationship(back_populates="branch")


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(
        sa_column=sql.Column(sql.String, unique=True, nullable=False, index=True)
    )
    password_hash: str
    role: str = Field(default="seller", nullable=False)
    branch_id: Optional[int] = Field(default=None, foreign_key="branches.id")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    branch: Optional[Branch] = Relationship(back_populates="users")
    financial_payments: list["FinancialPayment"] = Relationship(back_populates="user")


class Customer(SQLModel, table=True):
    __tablename__ = "customers"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    phone: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)
    branch_id: int = Field(foreign_key="branches.id")
    credit_balance: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    branch: Branch = Relationship()


class Product(SQLModel, table=True):
    __tablename__ = "products"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = Field(default=None)
    category: Optional[str] = Field(default=None, index=True)
    price: float = Field(gt=0)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Stock(SQLModel, table=True):
    __tablename__ = "stock"
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id")
    branch_id: int = Field(foreign_key="branches.id")
    quantity: int = Field(default=0)
    product: Product = Relationship()
    branch: Branch = Relationship()


class Sale(SQLModel, table=True):
    __tablename__ = "sales"
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customers.id")
    user_id: int = Field(foreign_key="users.id")
    branch_id: int = Field(foreign_key="branches.id")
    total_amount: float
    payment_method: str
    status: str = Field(default="Paid")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    customer: Customer = Relationship()
    user: User = Relationship()
    branch: Branch = Relationship()
    details: list["SaleDetail"] = Relationship(back_populates="sale")
    installments: list["Installment"] = Relationship(back_populates="sale")


class SaleDetail(SQLModel, table=True):
    __tablename__ = "sale_details"
    id: Optional[int] = Field(default=None, primary_key=True)
    sale_id: int = Field(foreign_key="sales.id")
    product_id: int = Field(foreign_key="products.id")
    quantity: int
    unit_price: float
    subtotal: float = Field(default=0)
    sale: Sale = Relationship(back_populates="details")
    product: Product = Relationship()


class Installment(SQLModel, table=True):
    __tablename__ = "installments"
    id: Optional[int] = Field(default=None, primary_key=True)
    sale_id: int = Field(foreign_key="sales.id")
    due_date: datetime
    amount_due: float
    status: str = Field(default="Pending")
    paid_at: Optional[datetime] = Field(default=None)
    sale: Sale = Relationship(back_populates="installments")


class FinancialPayment(SQLModel, table=True):
    __tablename__ = "financial_payments"
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customers.id")
    user_id: int = Field(foreign_key="users.id")
    branch_id: int = Field(foreign_key="branches.id")
    principal_amount: float
    interest_rate: float
    total_amount: float
    installment_type: str
    num_installments: int
    installment_amount: float
    status: str = Field(default="Active")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    customer: Customer = Relationship()
    user: User = Relationship(back_populates="financial_payments")
    branch: Branch = Relationship()
    installments: list["FinancialInstallment"] = Relationship(back_populates="payment")


class FinancialInstallment(SQLModel, table=True):
    __tablename__ = "financial_installments"
    id: Optional[int] = Field(default=None, primary_key=True)
    payment_id: int = Field(foreign_key="financial_payments.id")
    installment_number: int
    due_date: datetime
    amount_due: float
    amount_paid: float = Field(default=0.0)
    status: str = Field(default="Pending")
    paid_at: Optional[datetime] = Field(default=None)
    payment: FinancialPayment = Relationship(back_populates="installments")


class CashClosing(SQLModel, table=True):
    __tablename__ = "cash_closings"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    branch_id: int = Field(foreign_key="branches.id")
    period_type: str
    start_date: datetime
    end_date: datetime
    total_collected: float
    status: str = Field(default="Closed")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    user: User = Relationship()
    branch: Branch = Relationship()
    details: list["CashClosingDetail"] = Relationship(back_populates="closing")


class CashClosingDetail(SQLModel, table=True):
    __tablename__ = "cash_closing_details"
    id: Optional[int] = Field(default=None, primary_key=True)
    closing_id: int = Field(foreign_key="cash_closings.id")
    payment_type: str
    payment_id: int
    amount: float
    closing: CashClosing = Relationship(back_populates="details")


class BranchDict(TypedDict):
    id: int
    name: str
    location: str | None
    created_at: str


class UserDict(TypedDict):
    id: int
    username: str
    role: str
    branch: BranchDict | None
    created_at: str


class CustomerDict(TypedDict):
    id: int
    name: str
    phone: str | None
    email: str | None
    address: str | None
    branch_id: int
    credit_balance: float
    created_at: str
    branch_name: str


class ProductDict(TypedDict):
    id: int
    name: str
    description: str | None
    category: str | None
    price: float
    created_at: str


class StockDict(TypedDict):
    id: int
    product_id: int
    branch_id: int
    quantity: int
    product_name: str
    branch_name: str


class SaleDict(TypedDict):
    id: int
    customer_name: str
    user_username: str
    branch_name: str
    total_amount: float
    payment_method: str
    status: str
    created_at: str


class FinancialPaymentDict(TypedDict):
    id: int
    customer_name: str
    principal_amount: float
    interest_rate: float
    total_amount: float
    installment_type: str
    num_installments: int
    installment_amount: float
    status: str
    created_at: str
    installments: list["FinancialInstallmentDict"]


class FinancialInstallmentDict(TypedDict):
    id: int
    payment_id: int
    installment_number: int
    due_date: str
    amount_due: float
    amount_paid: float
    status: str
    paid_at: str | None


class CashClosingDict(TypedDict):
    id: int
    user_name: str
    branch_name: str
    period_type: str
    start_date: str
    end_date: str
    total_collected: float
    status: str
    created_at: str


class CollectedPaymentDict(TypedDict):
    customer_name: str
    payment_type: str
    amount: float
    paid_at: str