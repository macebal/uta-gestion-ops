from nicegui import ui
from nicegui.testing import User
from sqlalchemy.orm import sessionmaker

from src.models import Detail
from src.pages.details.manage_details import manage_details_page
from tests.conftest import SAMPLE_DETAILS, db_session_ctx


async def test_page_loads_correctly(user: User, test_db_session_factory: sessionmaker):
    @ui.page("/test-details")
    def test_page():
        manage_details_page(test_db_session_factory)

    await user.open("/test-details")
    await user.should_see("Gestión de Detalles de Pago")
    await user.should_see("Crear Detalle")


async def test_page_loads_existing_items(user: User, test_db_session_factory: sessionmaker):
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

    with db_session_ctx(test_db_session_factory) as session:
        assert len(session.query(Detail).all()) == len(SAMPLE_DETAILS)

    user.find("Crear Detalle").click()

    await user.should_see("Nuevo Detalle")

    detail_input = list(user.find(kind=ui.input).elements)[0]
    detail_input.set_value("New Detail")

    user.find("Crear").click()

    with db_session_ctx(test_db_session_factory) as session:
        assert len(session.query(Detail).all()) == len(SAMPLE_DETAILS) + 1
        assert session.query(Detail).filter_by(value="New Detail").first() is not None

    table = user.find(ui.table).elements.pop()
    assert len(table.rows) == len(SAMPLE_DETAILS) + 1
    assert any(elem["value"] == "New Detail" for elem in table.rows)
