from datetime import datetime
from unittest.mock import patch

from nicegui import ui
from nicegui.testing import User
from sqlalchemy.orm import sessionmaker

from src.models import Account, PaymentOrder
from src.pages.payment_orders.create_payment_order import create_payment_order_page
from tests.conftest import SAMPLE_ACCOUNTS, db_session_ctx


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


async def test_create_payment_order_success(user: User, test_db_session_factory: sessionmaker, tmp_path):
    from src.services import pdf_generator

    open_file_called = []
    original_generate_pdf = pdf_generator.generate_pdf

    def mock_open_file(file_path: str) -> bool:
        open_file_called.append(file_path)
        return True

    def mock_generate_pdf(template_name: str, pages_data: list[dict], output_path: str) -> str:
        full_path = tmp_path / output_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        return original_generate_pdf(template_name, pages_data, output_path, base_dir=tmp_path)

    with (
        patch("src.components.payment_order_form.open_file", side_effect=mock_open_file),
        patch("src.components.payment_order_form.generate_pdf", side_effect=mock_generate_pdf),
    ):

        @ui.page("/test-create-payment-order")
        def test_page():
            create_payment_order_page(test_db_session_factory)

        await user.open("/test-create-payment-order")

        test_account = SAMPLE_ACCOUNTS[0]
        initial_order_number = test_account["last_order_number"]
        initial_check_number = test_account["last_check_number"]

        with db_session_ctx(test_db_session_factory) as session:
            initial_po_count = len(session.query(PaymentOrder).all())
            account = session.query(Account).filter_by(name=test_account["name"]).first()
            assert account.account_sequence.last_order_number == initial_order_number
            assert account.account_sequence.last_check_number == initial_check_number

        account_select = user.find("Cuenta").elements.pop()
        account_select.set_value(test_account["name"])

        await user.should_see("Test Account 1")

        supplier_select = user.find("Proveedor").elements.pop()
        supplier_select.set_value("Test Supplier 1")

        await user.should_see("Test Supplier 1")

        detail_select = user.find("Detalle").elements.pop()
        detail_select.set_value("Test Detail 1")

        user.find("Agregar Factura").click()

        await user.should_see("Agregar Factura")

        invoice_number_input = user.find("Número de Factura").elements.pop()
        invoice_amount_input = user.find("Importe").elements.pop()

        invoice_number_input.set_value("TEST-INV-001")
        invoice_amount_input.set_value("1000.00")

        user.find("add-invoice-submit").click()

        await user.should_see("Factura agregada exitosamente")

        issue_date_inputs = list(user.find(kind=ui.input).elements)
        emission_input = None
        vence_input = None

        for input_elem in issue_date_inputs:
            if hasattr(input_elem, "props") and "Emisión" in str(input_elem):
                emission_input = input_elem
            elif hasattr(input_elem, "props") and "Vence" in str(input_elem):
                vence_input = input_elem

        if emission_input:
            emission_input.set_value("15/03/2024")
        if vence_input:
            vence_input.set_value("15/04/2024")

        export_checkbox = user.find("Generar PDF de orden de pago").elements.pop()
        export_checkbox.set_value(True)

        user.find("submit-payment-order").click()

        await user.should_see("Orden de pago creada exitosamente")

        with db_session_ctx(test_db_session_factory) as session:
            final_po_count = len(session.query(PaymentOrder).all())
            assert final_po_count == initial_po_count + 1

            new_po = session.query(PaymentOrder).order_by(PaymentOrder.id.desc()).first()
            assert new_po is not None
            assert new_po.account.name == test_account["name"]
            assert new_po.supplier.name == "Test Supplier 1"
            assert new_po.detail.value == "Test Detail 1"
            assert len(new_po.invoices) == 1
            assert new_po.invoices[0].invoice_number == "TEST-INV-001"

            account = session.query(Account).filter_by(name=test_account["name"]).first()
            assert account.account_sequence.last_order_number == initial_order_number + 1
            assert account.account_sequence.last_check_number == initial_check_number + 1

    expected_order_number = initial_order_number + 1
    today_str = datetime.now().strftime("%Y%m%d")
    pdf_path = (
        tmp_path
        / "ordenes de pago"
        / test_account["name"].lower()
        / f"orden_de_pago_{expected_order_number}_{today_str}.pdf"
    )
    assert pdf_path.exists(), f"PDF file not found at {pdf_path}"
    assert pdf_path.stat().st_size > 0, "PDF file is empty"
    assert len(open_file_called) == 1, f"open_file should be called once, was called {len(open_file_called)} times"
