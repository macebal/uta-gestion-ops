from typing import Callable

from nicegui import ui
from sqlalchemy.orm import Session

from src.components import (
    create_invoice_table,
    date_input_with_calendar,
    primary_button,
    searchable_select,
    text_input,
)
from src.models import Account, Supplier, Detail


def create_payment_order_page(session_factory: Callable[[], Session]):
    """Create the payment order form page"""

    # Storage for data
    accounts_data: list[str] = []
    suppliers_data: list[str] = []
    details_data: list[str] = []
    invoice_rows: list[dict] = []

    # UI component references
    op_input = None
    check_input = None

    def load_accounts():
        """Load all accounts from database"""
        nonlocal accounts_data
        session = session_factory()
        try:
            accounts = session.query(Account).order_by(Account.name).all()
            accounts_data.clear()
            accounts_data.extend([account.name for account in accounts])
        finally:
            session.close()

    def load_suppliers():
        """Load all suppliers from database"""
        nonlocal suppliers_data
        session = session_factory()
        try:
            suppliers = session.query(Supplier).order_by(Supplier.name).all()
            suppliers_data.clear()
            suppliers_data.extend([supplier.name for supplier in suppliers])
        finally:
            session.close()

    def load_details():
        """Load all details from database"""
        nonlocal details_data
        session = session_factory()
        try:
            details = session.query(Detail).order_by(Detail.value).all()
            details_data.clear()
            details_data.extend([detail.value for detail in details])
        finally:
            session.close()

    def on_account_change(e):
        """Handle account selection change"""
        nonlocal op_input, check_input
        account_name = e.value
        if not account_name:
            return

        session = session_factory()
        try:
            # Find the account by name
            account = session.query(Account).filter_by(name=account_name).first()
            if account and account.account_sequence:
                # Get next order and check numbers
                next_order = account.account_sequence.last_order_number + 1
                next_check = account.account_sequence.last_check_number + 1

                # Update the input fields
                if op_input:
                    op_input.value = str(next_order)
                if check_input:
                    check_input.value = str(next_check).zfill(8)  # Pad with zeros
            elif account:
                # No sequence yet, start from 1
                if op_input:
                    op_input.value = "1"
                if check_input:
                    check_input.value = str(1).zfill(8)
        finally:
            session.close()

    # Load data from database
    load_accounts()
    load_suppliers()
    load_details()

    with ui.column().classes("w-full p-6"):
        with ui.card().classes("w-full max-w-4xl mx-auto p-6 shadow-lg"):
            ui.label("Nueva Orden de Pago").classes(
                "text-2xl font-normal text-gray-700 mb-6"
            )

            with ui.row().classes("w-full gap-4 mb-4"):
                with ui.column().classes("flex-1"):
                    searchable_select(
                        accounts_data,
                        label="Cuenta",
                        on_change=on_account_change,
                    )

                with ui.column().classes("w-32"):
                    op_input = text_input("OP")

                with ui.column().classes("flex-1"):
                    date_input_with_calendar("Fecha")

            with ui.row().classes("w-full gap-4 mb-4"):
                with ui.column().classes("flex-1"):
                    check_input = text_input("Cheque")

                with ui.column().classes("flex-1"):
                    date_input_with_calendar("Emisión")

                with ui.column().classes("flex-1"):
                    date_input_with_calendar("Vence")

            with ui.column().classes("w-full mb-4"):
                searchable_select(suppliers_data, label="Proveedor")

            with ui.column().classes("w-full mb-6"):
                searchable_select(details_data, label="Detalle")

            with ui.column().classes("w-full items-center"):
                ui.label("Facturas").classes("text-lg font-semibold text-gray-700 mb-2")

                create_invoice_table(invoice_rows, total="$0.00")

            with ui.row().classes("w-full gap-6 mt-6"):
                with ui.column().classes("flex-1"):
                    text_input("Retenciones")

                with ui.card().classes(
                    "flex-1 p-4 bg-gray-50 items-center justify-center"
                ):
                    ui.label("Total OP").classes("text-xs text-gray-500 mb-1")
                    ui.label("$0.00").classes("text-2xl font-bold text-gray-800")

            with ui.row().classes("w-full items-center justify-between mt-6"):
                with ui.row().classes("items-center gap-2"):
                    ui.checkbox("Imprimir orden de pago", value=True).classes(
                        "text-gray-700"
                    )

                primary_button("Agregar OP")
