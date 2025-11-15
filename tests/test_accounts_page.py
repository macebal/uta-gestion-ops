from nicegui import ui
from nicegui.testing import User
from sqlalchemy.orm import sessionmaker

from src.models import Account
from src.pages.accounts.manage_accounts import manage_accounts_page
from tests.conftest import SAMPLE_ACCOUNTS, db_session_ctx


async def test_page_loads_correctly(user: User, test_db_session_factory: sessionmaker):
    @ui.page("/test-accounts")
    def test_page():
        manage_accounts_page(test_db_session_factory)

    await user.open("/test-accounts")
    await user.should_see("Gestión de Cuentas Bancarias")
    await user.should_see("Crear Cuenta")


async def test_page_loads_existing_items(user: User, test_db_session_factory: sessionmaker):
    @ui.page("/test-accounts")
    def test_page():
        manage_accounts_page(test_db_session_factory)

    await user.open("/test-accounts")

    table = user.find(ui.table).elements.pop()
    assert len(table.rows) == len(SAMPLE_ACCOUNTS)
    assert {item["name"] for item in table.rows} == {a["name"] for a in SAMPLE_ACCOUNTS}


async def test_create_account_success(user: User, test_db_session_factory: sessionmaker):
    @ui.page("/test-accounts")
    def test_page():
        manage_accounts_page(test_db_session_factory)

    await user.open("/test-accounts")

    with db_session_ctx(test_db_session_factory) as session:
        assert len(session.query(Account).all()) == len(SAMPLE_ACCOUNTS)

    user.find("Crear Cuenta").click()

    await user.should_see("Nueva Cuenta")

    account_name_input = user.find("Nombre de la Cuenta").elements.pop()
    account_number_input = user.find("Número de Cuenta").elements.pop()

    account_name_input.set_value("New Account")
    account_number_input.set_value("9999999999")

    await user.should_see("New Account")

    order_number_input = user.find("Último Número de OP").elements.pop()
    check_number_input = user.find("Último Número de Cheque").elements.pop()

    order_number_input.set_value(10)
    check_number_input.set_value(20)

    user.find("Crear").click()

    await user.should_see("Cuenta creada exitosamente")

    with db_session_ctx(test_db_session_factory) as session:
        assert len(session.query(Account).all()) == len(SAMPLE_ACCOUNTS) + 1
        new_account = session.query(Account).filter_by(name="New Account").first()
        assert new_account is not None
        assert new_account.number == "9999999999"
        assert new_account.account_sequence.last_order_number == 10
        assert new_account.account_sequence.last_check_number == 20

    table = user.find(ui.table).elements.pop()
    assert len(table.rows) == len(SAMPLE_ACCOUNTS) + 1
    assert any(elem["name"] == "New Account" for elem in table.rows)
