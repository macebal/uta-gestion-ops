import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.models import Account, AccountSequence, Base, Detail, Supplier
import contextlib


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

    session.commit()
    session.close()
    yield SessionLocal
