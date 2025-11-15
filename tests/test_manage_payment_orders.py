from nicegui import ui
from nicegui.testing import User
from sqlalchemy.orm import sessionmaker

from src.pages.payment_orders.manage_payment_orders import manage_payment_orders_page
from tests.conftest import SAMPLE_PAYMENT_ORDERS


async def test_page_loads_correctly(user: User, test_db_session_factory: sessionmaker):
    @ui.page("/test-manage-payment-orders")
    def test_page():
        manage_payment_orders_page(test_db_session_factory)

    await user.open("/test-manage-payment-orders")
    await user.should_see("Gestión de Órdenes de Pago")
    await user.should_see("Nueva Orden de Pago")


async def test_page_loads_existing_items(user: User, test_db_session_factory: sessionmaker):
    @ui.page("/test-manage-payment-orders")
    def test_page():
        manage_payment_orders_page(test_db_session_factory)

    await user.open("/test-manage-payment-orders")

    table = user.find(ui.table).elements.pop()
    assert len(table.rows) == len(SAMPLE_PAYMENT_ORDERS)
    order_numbers = {row["order_number"] for row in table.rows}
    expected_order_numbers = {po["order_number"] for po in SAMPLE_PAYMENT_ORDERS}
    assert order_numbers == expected_order_numbers


async def test_navigation_to_create_page(user: User, test_db_session_factory: sessionmaker):
    @ui.page("/test-manage-payment-orders")
    def test_page():
        manage_payment_orders_page(test_db_session_factory)

    @ui.page("/payment-orders/create")
    def create_page():
        ui.label("Create Payment Order Page")

    await user.open("/test-manage-payment-orders")

    user.find("Nueva Orden de Pago").click()

    await user.should_see("Create Payment Order Page")
