from collections.abc import Callable

from sqlalchemy.orm import Session

from src.models import Account, Detail, Supplier


def load_accounts(session_factory: Callable[[], Session], names_only: bool = True) -> list[str] | list[Account]:
    """
    Load all accounts from database.

    Args:
        session_factory: Function to create database sessions
        names_only: If True, return list of account names. If False, return list of Account objects

    Returns:
        List of account names or Account objects, ordered by name
    """
    session = session_factory()
    try:
        accounts = session.query(Account).order_by(Account.name).all()
        if names_only:
            return [account.name for account in accounts]
        return accounts
    finally:
        session.close()


def load_suppliers(session_factory: Callable[[], Session], names_only: bool = True) -> list[str] | list[Supplier]:
    """
    Load all suppliers from database.

    Args:
        session_factory: Function to create database sessions
        names_only: If True, return list of supplier names. If False, return list of Supplier objects

    Returns:
        List of supplier names or Supplier objects, ordered by name
    """
    session = session_factory()
    try:
        suppliers = session.query(Supplier).order_by(Supplier.name).all()
        if names_only:
            return [supplier.name for supplier in suppliers]
        return suppliers
    finally:
        session.close()


def load_details(session_factory: Callable[[], Session], names_only: bool = True) -> list[str] | list[Detail]:
    """
    Load all details from database.

    Args:
        session_factory: Function to create database sessions
        names_only: If True, return list of detail values. If False, return list of Detail objects

    Returns:
        List of detail values or Detail objects, ordered by value
    """
    session = session_factory()
    try:
        details = session.query(Detail).order_by(Detail.value).all()
        if names_only:
            return [detail.value for detail in details]
        return details
    finally:
        session.close()


def get_account_by_id(session_factory: Callable[[], Session], account_id: int) -> Account | None:
    """
    Get account by ID.

    Args:
        session_factory: Function to create database sessions
        account_id: Account ID

    Returns:
        Account object or None if not found
    """
    if not account_id:
        return None
    session = session_factory()
    try:
        return session.query(Account).filter_by(id=account_id).first()
    finally:
        session.close()


def get_account_by_name(session_factory: Callable[[], Session], account_name: str) -> Account | None:
    """
    Get account by name.

    Args:
        session_factory: Function to create database sessions
        account_name: Account name

    Returns:
        Account object or None if not found
    """
    if not account_name:
        return None
    session = session_factory()
    try:
        return session.query(Account).filter_by(name=account_name).first()
    finally:
        session.close()


def get_account_id_by_name(session_factory: Callable[[], Session], account_name: str) -> int | None:
    """
    Get account ID by name.

    Args:
        session_factory: Function to create database sessions
        account_name: Account name

    Returns:
        Account ID or None if not found
    """
    account = get_account_by_name(session_factory, account_name)
    return account.id if account else None


def get_supplier_by_id(session_factory: Callable[[], Session], supplier_id: int) -> Supplier | None:
    """
    Get supplier by ID.

    Args:
        session_factory: Function to create database sessions
        supplier_id: Supplier ID

    Returns:
        Supplier object or None if not found
    """
    if not supplier_id:
        return None
    session = session_factory()
    try:
        return session.query(Supplier).filter_by(id=supplier_id).first()
    finally:
        session.close()


def get_supplier_by_name(session_factory: Callable[[], Session], supplier_name: str) -> Supplier | None:
    """
    Get supplier by name.

    Args:
        session_factory: Function to create database sessions
        supplier_name: Supplier name

    Returns:
        Supplier object or None if not found
    """
    if not supplier_name:
        return None
    session = session_factory()
    try:
        return session.query(Supplier).filter_by(name=supplier_name).first()
    finally:
        session.close()


def get_supplier_id_by_name(session_factory: Callable[[], Session], supplier_name: str) -> int | None:
    """
    Get supplier ID by name.

    Args:
        session_factory: Function to create database sessions
        supplier_name: Supplier name

    Returns:
        Supplier ID or None if not found
    """
    supplier = get_supplier_by_name(session_factory, supplier_name)
    return supplier.id if supplier else None


def get_detail_by_id(session_factory: Callable[[], Session], detail_id: int) -> Detail | None:
    """
    Get detail by ID.

    Args:
        session_factory: Function to create database sessions
        detail_id: Detail ID

    Returns:
        Detail object or None if not found
    """
    if not detail_id:
        return None
    session = session_factory()
    try:
        return session.query(Detail).filter_by(id=detail_id).first()
    finally:
        session.close()


def get_detail_by_value(session_factory: Callable[[], Session], detail_value: str) -> Detail | None:
    """
    Get detail by value.

    Args:
        session_factory: Function to create database sessions
        detail_value: Detail value

    Returns:
        Detail object or None if not found
    """
    if not detail_value:
        return None
    session = session_factory()
    try:
        return session.query(Detail).filter_by(value=detail_value).first()
    finally:
        session.close()


def get_detail_id_by_value(session_factory: Callable[[], Session], detail_value: str) -> int | None:
    """
    Get detail ID by value.

    Args:
        session_factory: Function to create database sessions
        detail_value: Detail value

    Returns:
        Detail ID or None if not found
    """
    detail = get_detail_by_value(session_factory, detail_value)
    return detail.id if detail else None
