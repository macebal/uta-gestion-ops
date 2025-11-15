from nicegui import ui
from nicegui.testing import User
from sqlalchemy.orm import sessionmaker

from src.models import Supplier
from src.pages.suppliers.manage_suppliers import manage_suppliers_page
from tests.conftest import SAMPLE_SUPPLIERS, db_session_ctx


async def test_page_loads_correctly(user: User, test_db_session_factory: sessionmaker):
    @ui.page("/test-suppliers")
    def test_page():
        manage_suppliers_page(test_db_session_factory)

    await user.open("/test-suppliers")
    await user.should_see("Gestión de Proveedores")
    await user.should_see("Crear Proveedor")


async def test_page_loads_existing_items(user: User, test_db_session_factory: sessionmaker):
    @ui.page("/test-suppliers")
    def test_page():
        manage_suppliers_page(test_db_session_factory)

    await user.open("/test-suppliers")

    table = user.find(ui.table).elements.pop()
    assert len(table.rows) == len(SAMPLE_SUPPLIERS)
    assert {item["name"] for item in table.rows} == {s["name"] for s in SAMPLE_SUPPLIERS}


async def test_create_supplier_success(user: User, test_db_session_factory: sessionmaker):
    @ui.page("/test-suppliers")
    def test_page():
        manage_suppliers_page(test_db_session_factory)

    await user.open("/test-suppliers")

    with db_session_ctx(test_db_session_factory) as session:
        assert len(session.query(Supplier).all()) == len(SAMPLE_SUPPLIERS)

    user.find("Crear Proveedor").click()

    await user.should_see("Nuevo Proveedor")

    supplier_name_input = user.find("Nombre del Proveedor").elements.pop()
    supplier_name_input.set_value("New Supplier")

    await user.should_see("New Supplier")

    user.find("Crear").click()

    await user.should_see("Proveedor creado exitosamente")

    with db_session_ctx(test_db_session_factory) as session:
        assert len(session.query(Supplier).all()) == len(SAMPLE_SUPPLIERS) + 1
        assert session.query(Supplier).filter_by(name="New Supplier").first() is not None

    table = user.find(ui.table).elements.pop()
    assert len(table.rows) == len(SAMPLE_SUPPLIERS) + 1
    assert any(elem["name"] == "New Supplier" for elem in table.rows)
