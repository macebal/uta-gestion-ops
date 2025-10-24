from nicegui import ui
from nicegui.testing import User
from sqlalchemy.orm import sessionmaker

from src.models import Detail
from src.pages.manage_details import manage_details_page
from tests.conftest import SAMPLE_DETAILS, db_session_ctx


async def test_page_loads_correctly(user: User, test_db_session_factory):
    await user.open("/manage-details")
    await user.should_see("Gestión de Detalles de Pago")
    await user.should_see("Nuevo Detalle")
    await user.should_see("Detalles Existentes")
    await user.should_see("Buscar detalle")
    await user.should_see("Agregar")


async def test_page_loads_existing_items(
    user: User, test_db_session_factory: sessionmaker
):
    @ui.page("/test-details")
    def test_page():
        manage_details_page(test_db_session_factory)

    await user.open("/test-details")

    table = user.find(ui.table).elements.pop()
    assert len(table.rows) == len(SAMPLE_DETAILS)
    assert {item["value"] for item in table.rows} == set(SAMPLE_DETAILS)


async def test_create_detail_success(user: User, test_db_session_factory: sessionmaker):
    @ui.page("/test-details")
    def test_page():
        manage_details_page(test_db_session_factory)

    await user.open("/test-details")

    # Assert initial DB state
    with db_session_ctx(test_db_session_factory) as session:
        assert len(session.query(Detail).all()) == len(SAMPLE_DETAILS)

    user.find("Detalle de Pago").type("New Detail")
    user.find("Agregar").click()

    with db_session_ctx(test_db_session_factory) as session:
        assert len(session.query(Detail).all()) == len(SAMPLE_DETAILS) + 1
        assert session.query(Detail).filter_by(value="New Detail").first() is not None

    table = user.find(ui.table).elements.pop()
    assert len(table.rows) == len(SAMPLE_DETAILS) + 1
    assert any("New Detail" == elem["value"] for elem in table.rows)


async def test_delete_detail(user: User, test_db_session_factory: sessionmaker):
    @ui.page("/test-details")
    def test_page():
        manage_details_page(test_db_session_factory)

    await user.open("/test-details")

    # Assert initial DB state
    with db_session_ctx(test_db_session_factory) as session:
        assert len(session.query(Detail).all()) == len(SAMPLE_DETAILS)

    # TODO: Finish this
