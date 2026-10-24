from decimal import Decimal

from nicegui import ui
from nicegui.testing import User
from sqlalchemy.orm import sessionmaker

from src.components.payment_order_form import payment_order_form
from src.models import PaymentOrder
from tests.conftest import db_session_ctx


async def test_edit_payment_order_saves_and_reloads_more_than_five_invoices(
    user: User, test_db_session_factory: sessionmaker
):
    with db_session_ctx(test_db_session_factory) as session:
        order_id = session.query(PaymentOrder).filter_by(order_number=1).one().id

    @ui.page("/test-edit-payment-order")
    def test_page():
        payment_order_form(test_db_session_factory, mode="edit", payment_order_id=order_id)

    await user.open("/test-edit-payment-order")

    for index in range(3, 8):
        user.find("Agregar Factura").click()
        invoice_number_input = max(user.find("Número de Factura").elements, key=lambda element: element.id)
        invoice_amount_input = max(user.find("Importe").elements, key=lambda element: element.id)
        invoice_number_input.set_value(f"INV-{index:03}")
        invoice_amount_input.set_value("100.01")
        user.find("add-invoice-submit").click()
        await user.should_see("Factura agregada exitosamente")

    invoice_table = user.find(ui.table).elements.pop()
    assert len(invoice_table.rows) == 7
    user.find("Retenciones").elements.pop().set_value("25.75")
    await user.should_see("$ 1,474.30")
    user.find("save-payment-order").click()
    await user.should_see("Orden de pago actualizada exitosamente")

    with db_session_ctx(test_db_session_factory) as session:
        order = session.get(PaymentOrder, order_id)
        assert len(order.invoices) == 7
        assert {invoice.invoice_number for invoice in order.invoices} == {f"INV-{index:03}" for index in range(1, 8)}
        assert order.amount == Decimal("1474.30")
        assert order.withholding_amount == Decimal("25.75")

    await user.open("/test-edit-payment-order")
    invoice_table = user.find(ui.table).elements.pop()
    assert len(invoice_table.rows) == 7
    await user.should_see("$ 1,474.30")
