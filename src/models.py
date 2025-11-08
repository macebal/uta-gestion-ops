from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all ORM models"""

    pass


class AppState(Base):
    """AppState table - stores application state like last opened date and reminder dismissal"""

    __tablename__ = "app_state"

    id: Mapped[int] = mapped_column(primary_key=True)
    last_opened_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    reminder_dismissed_month: Mapped[str | None] = mapped_column(
        String, nullable=True
    )

    def __repr__(self):
        return (
            f"<AppState(id={self.id}, last_opened={self.last_opened_date}, "
            f"dismissed={self.reminder_dismissed_month})>"
        )


class Account(Base):
    """Accounts table - stores bank account information"""

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    number: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    payment_orders: Mapped[list["PaymentOrder"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )
    account_sequence: Mapped[Optional["AccountSequence"]] = relationship(
        back_populates="account", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Account(id={self.id}, name='{self.name}', number='{self.number}')>"


class AccountSequence(Base):
    """Account_Sequences table - tracks order and check numbers for accounts"""

    __tablename__ = "account_sequences"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("accounts.id"), unique=True, nullable=False
    )
    last_order_number: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_check_number: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)

    # Relationships
    account: Mapped["Account"] = relationship(back_populates="account_sequence")

    def __repr__(self):
        return f"<AccountSequence(id={self.id}, account_id='{self.account_id}', last_order={self.last_order_number})>"


class Supplier(Base):
    """Suppliers table - stores supplier information"""

    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    cuit: Mapped[str | None] = mapped_column(String, nullable=True)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True)

    # Relationships
    payment_orders: Mapped[list["PaymentOrder"]] = relationship(
        back_populates="supplier", cascade="all, delete-orphan"
    )
    invoices: Mapped[list["Invoice"]] = relationship(
        back_populates="supplier", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Supplier(id={self.id}, name='{self.name}')>"


class Detail(Base):
    """Details table - stores detail values"""

    __tablename__ = "details"

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    payment_orders: Mapped[list["PaymentOrder"]] = relationship(
        back_populates="detail", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Detail(id={self.id}, value='{self.value}')>"


class PaymentOrder(Base):
    """Payment_Orders table - stores payment order information"""

    __tablename__ = "payment_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_number: Mapped[int] = mapped_column(Integer, nullable=False)
    check_number: Mapped[int] = mapped_column(Integer, nullable=False)
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("accounts.id"), nullable=False
    )
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("suppliers.id"), nullable=False
    )
    detail_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("details.id"), nullable=False
    )
    withholding_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    created: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    # Relationships
    account: Mapped["Account"] = relationship(back_populates="payment_orders")
    supplier: Mapped["Supplier"] = relationship(back_populates="payment_orders")
    detail: Mapped["Detail"] = relationship(back_populates="payment_orders")
    invoices: Mapped[list["Invoice"]] = relationship(
        back_populates="payment_order", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<PaymentOrder(id={self.id}, order_number={self.order_number}, amount={self.amount})>"


class Invoice(Base):
    """Invoices table - stores invoice information"""

    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True)
    payment_order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("payment_orders.id"), nullable=False
    )
    invoice_number: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("suppliers.id"), nullable=False
    )

    # Relationships
    payment_order: Mapped["PaymentOrder"] = relationship(back_populates="invoices")
    supplier: Mapped["Supplier"] = relationship(back_populates="invoices")

    def __repr__(self):
        return f"<Invoice(id={self.id}, invoice_number='{self.invoice_number}', amount={self.amount})>"
