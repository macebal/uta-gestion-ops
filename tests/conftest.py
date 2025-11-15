import contextlib
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.models import Account, AccountSequence, Base, Detail, Invoice, PaymentOrder, Supplier


SAMPLE_DETAILS = [
    "Test Detail 1",
    "Test Detail 2",
    "Test Detail 3",
]

SAMPLE_ACCOUNTS = [
    {
        "name": "Test Account 1",
        "number": "1234567890",
        "last_order_number": 1,
        "last_check_number": 2,
    },
    {
        "name": "Test Account 2",
        "number": "0987654321",
        "last_order_number": 3,
        "last_check_number": 4,
    },
    {
        "name": "Test Account 3",
        "number": "1111111111",
        "last_order_number": 5,
        "last_check_number": 6,
    },
]

SAMPLE_SUPPLIERS = [
    {"name": "Test Supplier 1"},
    {"name": "Test Supplier 2"},
    {"name": "Test Supplier 3"},
]

SAMPLE_PAYMENT_ORDERS = [
    {
        "order_number": 1,
        "check_number": 1001,
        "account_index": 0,
        "supplier_index": 0,
        "detail_index": 0,
        "withholding_amount": Decimal("100.00"),
        "amount": Decimal("900.00"),
        "order_date": date(2024, 1, 15),
        "issue_date": date(2024, 1, 20),
        "due_date": date(2024, 2, 20),
        "invoices": [
            {"invoice_number": "INV-001", "amount": Decimal("500.00")},
            {"invoice_number": "INV-002", "amount": Decimal("500.00")},
        ],
    },
    {
        "order_number": 2,
        "check_number": 1002,
        "account_index": 0,
        "supplier_index": 1,
        "detail_index": 1,
        "withholding_amount": Decimal("0.00"),
        "amount": Decimal("1500.00"),
        "order_date": date(2024, 2, 10),
        "issue_date": date(2024, 2, 15),
        "due_date": date(2024, 3, 15),
        "invoices": [
            {"invoice_number": "INV-003", "amount": Decimal("1500.00")},
        ],
    },
]


@contextlib.contextmanager
def db_session_ctx(session_factory):
    """Context manager to yield and close a fresh session from a sessionmaker."""
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_db_session_factory():
    engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    for value in SAMPLE_DETAILS:
        detail = Detail(value=value)
        session.add(detail)
    session.flush()

    for account in SAMPLE_ACCOUNTS:
        new_account = Account(name=account["name"], number=account["number"])
        session.add(new_account)
        session.flush()
        account_sequence = AccountSequence(
            account_id=new_account.id,
            last_order_number=account["last_order_number"],
            last_check_number=account["last_check_number"],
        )
        session.add(account_sequence)
    session.flush()

    for supplier in SAMPLE_SUPPLIERS:
        supplier = Supplier(name=supplier["name"])
        session.add(supplier)
    session.flush()

    accounts = session.query(Account).all()
    suppliers = session.query(Supplier).all()
    details = session.query(Detail).all()

    for po_data in SAMPLE_PAYMENT_ORDERS:
        payment_order = PaymentOrder(
            order_number=po_data["order_number"],
            check_number=po_data["check_number"],
            account_id=accounts[po_data["account_index"]].id,
            supplier_id=suppliers[po_data["supplier_index"]].id,
            detail_id=details[po_data["detail_index"]].id,
            withholding_amount=po_data["withholding_amount"],
            amount=po_data["amount"],
            order_date=po_data["order_date"],
            issue_date=po_data["issue_date"],
            due_date=po_data["due_date"],
        )
        session.add(payment_order)
        session.flush()

        for invoice_data in po_data["invoices"]:
            invoice = Invoice(
                payment_order_id=payment_order.id,
                invoice_number=invoice_data["invoice_number"],
                amount=invoice_data["amount"],
                supplier_id=suppliers[po_data["supplier_index"]].id,
            )
            session.add(invoice)

    session.commit()
    session.close()
    yield SessionLocal
