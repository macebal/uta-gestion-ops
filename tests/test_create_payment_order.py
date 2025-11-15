from nicegui import ui
from nicegui.testing import User
from sqlalchemy.orm import sessionmaker

from src.pages.payment_orders.create_payment_order import create_payment_order_page


async def test_page_loads_correctly(user: User, test_db_session_factory: sessionmaker):
    @ui.page("/test-create-payment-order")
    def test_page():
        create_payment_order_page(test_db_session_factory)

    await user.open("/test-create-payment-order")
    await user.should_see("Nueva Orden de Pago")


async def test_form_elements_present(user: User, test_db_session_factory: sessionmaker):
    @ui.page("/test-create-payment-order")
    def test_page():
        create_payment_order_page(test_db_session_factory)

    await user.open("/test-create-payment-order")

    await user.should_see("Cuenta")
    await user.should_see("OP")
    await user.should_see("Cheque")
    await user.should_see("Proveedor")
    await user.should_see("Detalle")
    await user.should_see("Fecha")
    await user.should_see("Emisión")
    await user.should_see("Vence")
    await user.should_see("Facturas")
    await user.should_see("Agregar Factura")
    await user.should_see("Retenciones")
    await user.should_see("Total OP")
    await user.should_see("Agregar OP")
