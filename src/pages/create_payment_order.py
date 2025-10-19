from typing import Callable

from nicegui import ui
from sqlalchemy.orm import Session

from src.components import (
    create_invoice_table,
    date_input,
    primary_button,
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
                    ui.select(
                        accounts_data,
                        label="Cuenta",
                        with_input=True,
                    ).classes(
                        "w-full"
                    ).props("outlined use-input")

                with ui.column().classes("w-32"):
                    text_input("OP")

                with ui.column().classes("flex-1"):
                    date_input("Fecha")

            with ui.row().classes("w-full gap-4 mb-4"):
                with ui.column().classes("flex-1"):
                    text_input("Cheque")

                with ui.column().classes("flex-1"):
                    date_input("Emisión")

                with ui.column().classes("flex-1"):
                    date_input("Vence")

            with ui.column().classes("w-full mb-4"):
                with ui.row().classes("w-full gap-2 items-center"):
                    ui.select(
                        suppliers_data,
                        label="Proveedor",
                        with_input=True,
                    ).classes("flex-1").props("outlined use-input")
                    ui.icon("edit").classes(
                        "text-yellow-500 cursor-pointer text-xl"
                    ).on("click", lambda: ui.navigate.to("/manage-suppliers"))

            with ui.column().classes("w-full mb-6"):
                with ui.row().classes("w-full gap-2 items-center"):
                    ui.select(
                        details_data,
                        label="Detalle",
                        with_input=True,
                    ).classes(
                        "flex-1"
                    ).props("outlined use-input")
                    ui.icon("edit").classes(
                        "text-yellow-500 cursor-pointer text-xl"
                    ).on("click", lambda: ui.navigate.to("/manage-details"))

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
