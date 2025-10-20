from typing import Callable
from decimal import Decimal

from nicegui import ui
from sqlalchemy.orm import Session

from src.components import (
    date_input_with_calendar,
    primary_button,
    searchable_select,
    secondary_button,
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
    retenciones_input = None
    invoice_table = None
    total_op_label = None
    add_invoice_dialog = None

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

    def format_currency(amount: float | Decimal | str) -> str:
        """Format a number as currency"""
        if isinstance(amount, str):
            # Remove currency symbols and convert to float
            amount = amount.replace("$", "").replace(",", "")
            try:
                amount = float(amount)
            except ValueError:
                amount = 0
        return f"${amount:,.2f}"

    def parse_currency(currency_str: str) -> Decimal:
        """Parse a currency string to Decimal"""
        if not currency_str:
            return Decimal("0.00")
        # Remove currency symbols and commas
        clean_str = currency_str.replace("$", "").replace(",", "").strip()
        try:
            return Decimal(clean_str)
        except (ValueError, Exception):
            return Decimal("0.00")

    def calculate_totals():
        """Calculate and update invoice total and total OP"""
        nonlocal total_op_label, retenciones_input, invoice_table

        # Calculate invoice total
        invoice_total = sum(
            parse_currency(row.get("importe", "0")) for row in invoice_rows
        )

        # Get withholdings
        withholdings = Decimal("0.00")
        if retenciones_input and retenciones_input.value:
            withholdings = parse_currency(retenciones_input.value)

        # Calculate total OP
        total_op = invoice_total - withholdings

        # Update total OP label
        if total_op_label:
            total_op_label.text = format_currency(total_op)

        # Update the invoice table footer via JavaScript
        if invoice_table:
            ui.run_javascript(
                f'document.getElementById("total-facturas").innerText = "{format_currency(invoice_total)}"'
            )

    def add_invoice(invoice_number: str, amount: str):
        """Add an invoice to the list"""
        nonlocal invoice_table, add_invoice_dialog

        if not invoice_number or not amount:
            ui.notify("Por favor complete todos los campos", type="negative")
            return

        try:
            # Validate amount
            parsed_amount = parse_currency(amount)
            if parsed_amount <= 0:
                ui.notify("El importe debe ser mayor a 0", type="negative")
                return

            # Add invoice to rows
            invoice_rows.append(
                {
                    "id": len(invoice_rows),  # Temporary ID
                    "factura": invoice_number,
                    "importe": format_currency(parsed_amount),
                }
            )

            # Update table
            if invoice_table:
                invoice_table.rows = invoice_rows
                invoice_table.update()

            # Recalculate totals
            calculate_totals()

            # Close dialog
            if add_invoice_dialog:
                add_invoice_dialog.close()

            ui.notify("Factura agregada exitosamente", type="positive")

        except Exception as e:
            ui.notify(f"Error al agregar factura: {str(e)}", type="negative")

    def delete_invoice(row_data):
        """Delete an invoice from the list"""
        nonlocal invoice_table

        try:
            # Remove invoice from rows
            invoice_rows[:] = [
                row for row in invoice_rows if row.get("id") != row_data.get("id")
            ]

            # Update table
            if invoice_table:
                invoice_table.rows = invoice_rows
                invoice_table.update()

            # Recalculate totals
            calculate_totals()

            ui.notify("Factura eliminada exitosamente", type="positive")

        except Exception as e:
            ui.notify(f"Error al eliminar factura: {str(e)}", type="negative")

    def show_add_invoice_dialog():
        """Show dialog to add a new invoice"""
        nonlocal add_invoice_dialog

        with ui.dialog() as dialog, ui.card().classes("p-6 min-w-96"):
            add_invoice_dialog = dialog
            ui.label("Agregar Factura").classes("text-xl font-semibold mb-4")

            invoice_number_input = text_input("Número de Factura")
            amount_input = text_input("Importe")

            with ui.row().classes("w-full gap-4 mt-6 justify-end"):
                secondary_button(
                    "Cancelar",
                    on_click=lambda: dialog.close(),
                )
                primary_button(
                    "Agregar",
                    on_click=lambda: add_invoice(
                        invoice_number_input.value, amount_input.value
                    ),
                )

        dialog.open()

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
                with ui.row().classes(
                    "w-full max-w-2xl justify-between items-center mb-2"
                ):
                    ui.label("Facturas").classes("text-lg font-semibold text-gray-700")
                    primary_button(
                        "Agregar Factura", icon="add", on_click=show_add_invoice_dialog
                    )

                # Invoice table columns
                columns = [
                    {
                        "name": "factura",
                        "label": "Factura",
                        "field": "factura",
                        "align": "left",
                    },
                    {
                        "name": "importe",
                        "label": "Importe",
                        "field": "importe",
                        "align": "right",
                    },
                    {
                        "name": "acciones",
                        "label": "Acciones",
                        "field": "acciones",
                        "align": "center",
                    },
                ]

                # Create invoice table
                invoice_table = (
                    ui.table(columns=columns, rows=invoice_rows, row_key="id")
                    .classes("w-full max-w-2xl")
                    .props("flat bordered")
                )

                # Add delete button slot
                invoice_table.add_slot(
                    "body-cell-acciones",
                    r"""
                    <q-td :props="props">
                        <q-btn
                            flat
                            round
                            dense
                            icon="delete"
                            color="red"
                            @click="() => $parent.$emit('delete_invoice', props.row)"
                        >
                            <q-tooltip>Eliminar</q-tooltip>
                        </q-btn>
                    </q-td>
                    """,
                )

                # Add footer row with total
                invoice_table.add_slot(
                    "bottom-row",
                    r"""
                    <q-tr class="bg-gray-50">
                        <q-td class="text-left font-bold">Total</q-td>
                        <q-td class="text-right">
                            <div id="total-facturas" class="text-lg font-semibold text-gray-800">$0.00</div>
                        </q-td>
                        <q-td></q-td>
                    </q-tr>
                    """,
                )

                # Wire up delete event
                invoice_table.on("delete_invoice", lambda e: delete_invoice(e.args))

            with ui.row().classes("w-full gap-6 mt-6"):
                with ui.column().classes("flex-1"):
                    retenciones_input = text_input("Retenciones", value="$0.00")
                    retenciones_input.on(
                        "change", lambda: calculate_totals()
                    )  # Recalculate on change

                with ui.card().classes(
                    "flex-1 p-4 bg-gray-50 items-center justify-center"
                ):
                    ui.label("Total OP").classes("text-xs text-gray-500 mb-1")
                    total_op_label = ui.label("$0.00").classes(
                        "text-2xl font-bold text-gray-800"
                    )

            with ui.row().classes("w-full items-center justify-between mt-6"):
                with ui.row().classes("items-center gap-2"):
                    ui.checkbox("Imprimir orden de pago", value=True).classes(
                        "text-gray-700"
                    )

                primary_button("Agregar OP")
