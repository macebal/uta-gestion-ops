from typing import Callable
from decimal import Decimal
from pathlib import Path

from nicegui import ui
from sqlalchemy.orm import Session

from src.components import (
    date_input_with_calendar,
    primary_button,
    searchable_select,
    secondary_button,
    text_input,
)
from src.models import Account, PaymentOrder, Supplier, Detail
from src.services.pdf_generator import generate_pdf


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
    account_select = None
    supplier_select = None
    detail_select = None
    order_date_input = None
    issue_date_input = None
    due_date_input = None
    print_checkbox = None

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

    def get_account_id_by_name(account_name: str) -> int | None:
        """Get account ID by name"""
        if not account_name:
            return None
        session = session_factory()
        try:
            account = session.query(Account).filter_by(name=account_name).first()
            return account.id if account else None
        finally:
            session.close()

    def get_supplier_id_by_name(supplier_name: str) -> int | None:
        """Get supplier ID by name"""
        if not supplier_name:
            return None
        session = session_factory()
        try:
            supplier = session.query(Supplier).filter_by(name=supplier_name).first()
            return supplier.id if supplier else None
        finally:
            session.close()

    def get_detail_id_by_value(detail_value: str) -> int | None:
        """Get detail ID by value"""
        if not detail_value:
            return None
        session = session_factory()
        try:
            detail = session.query(Detail).filter_by(value=detail_value).first()
            return detail.id if detail else None
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
            account = session.query(Account).filter_by(name=account_name).first()
            if account and account.account_sequence:
                next_order = account.account_sequence.last_order_number + 1
                next_check = account.account_sequence.last_check_number + 1

                if op_input:
                    op_input.value = str(next_order)
                if check_input:
                    check_input.value = str(next_check).zfill(8)
            elif account:
                if op_input:
                    op_input.value = "1"
                if check_input:
                    check_input.value = str(1).zfill(8)
        finally:
            session.close()

    def format_currency(amount: float | Decimal | str) -> str:
        """Format a number as currency"""
        if isinstance(amount, str):
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
        clean_str = currency_str.replace("$", "").replace(",", "").strip()
        try:
            return Decimal(clean_str)
        except (ValueError, Exception):
            return Decimal("0.00")

    def calculate_totals():
        """Calculate and update invoice total and total OP"""
        nonlocal total_op_label, retenciones_input, invoice_table

        invoice_total = sum(
            parse_currency(row.get("importe", "0")) for row in invoice_rows
        )

        withholdings = Decimal("0.00")
        if retenciones_input and retenciones_input.value:
            withholdings = parse_currency(retenciones_input.value)

        total_op = invoice_total - withholdings

        if total_op_label:
            total_op_label.text = format_currency(total_op)

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
            parsed_amount = parse_currency(amount)
            if parsed_amount <= 0:
                ui.notify("El importe debe ser mayor a 0", type="negative")
                return

            invoice_rows.append(
                {
                    "id": len(invoice_rows),
                    "factura": invoice_number,
                    "importe": format_currency(parsed_amount),
                }
            )

            if invoice_table:
                invoice_table.rows = invoice_rows
                invoice_table.update()

            calculate_totals()

            if add_invoice_dialog:
                add_invoice_dialog.close()

            ui.notify("Factura agregada exitosamente", type="positive")

        except Exception as e:
            ui.notify(f"Error al agregar factura: {str(e)}", type="negative")

    def delete_invoice(row_data):
        """Delete an invoice from the list"""
        nonlocal invoice_table

        try:
            invoice_rows[:] = [
                row for row in invoice_rows if row.get("id") != row_data.get("id")
            ]

            if invoice_table:
                invoice_table.rows = invoice_rows
                invoice_table.update()

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

    def update_account_sequence(account_id: int, order_number: int, check_number: int):
        """Update account sequence numbers after creating payment order"""
        session = session_factory()
        try:
            account = session.query(Account).filter_by(id=account_id).first()
            if account:
                if account.account_sequence:
                    account.account_sequence.last_order_number = order_number
                    account.account_sequence.last_check_number = check_number
                else:
                    from src.models import AccountSequence

                    account_seq = AccountSequence(
                        account_id=account.id,
                        last_order_number=order_number,
                        last_check_number=check_number,
                    )
                    session.add(account_seq)
                session.commit()
        except Exception as e:
            session.rollback()
            ui.notify(
                f"Error al actualizar secuencia de cuenta: {str(e)}", type="negative"
            )
        finally:
            session.close()

    def create_payment_order():
        """Create a new payment order"""
        account_name = account_select.value if account_select else ""
        supplier_name = supplier_select.value if supplier_select else ""
        detail_value = detail_select.value if detail_select else ""
        op = op_input.value if op_input else ""
        check = check_input.value if check_input else ""
        retenciones = retenciones_input.value if retenciones_input else "$0.00"
        order_date_str = order_date_input.value if order_date_input else ""
        issue_date_str = issue_date_input.value if issue_date_input else ""
        due_date_str = due_date_input.value if due_date_input else ""

        if not all(
            [
                account_name,
                supplier_name,
                detail_value,
                op,
                check,
                order_date_str,
                issue_date_str,
                due_date_str,
            ]
        ):
            ui.notify(
                "Por favor complete todos los campos obligatorios", type="negative"
            )
            return

        if not invoice_rows:
            ui.notify("Debe agregar al menos una factura", type="negative")
            return

        account_id = get_account_id_by_name(account_name)
        supplier_id = get_supplier_id_by_name(supplier_name)
        detail_id = get_detail_id_by_value(detail_value)

        if not all([account_id, supplier_id, detail_id]):
            ui.notify("Error al obtener datos de la base de datos", type="negative")
            return

        try:
            from datetime import datetime

            order_date = datetime.strptime(order_date_str, "%d/%m/%Y").date()
            issue_date = datetime.strptime(issue_date_str, "%d/%m/%Y").date()
            due_date = datetime.strptime(due_date_str, "%d/%m/%Y").date()
        except ValueError:
            ui.notify("Formato de fecha inválido. Use DD/MM/YYYY", type="negative")
            return

        withholding_amount = parse_currency(retenciones)
        total_amount = parse_currency(
            total_op_label.text if total_op_label else "$0.00"
        )

        session = session_factory()
        try:
            payment_order = PaymentOrder(
                order_number=int(op),
                check_number=int(check),
                account_id=account_id,
                supplier_id=supplier_id,
                detail_id=detail_id,
                withholding_amount=withholding_amount,
                amount=total_amount,
                order_date=order_date,
                issue_date=issue_date,
                due_date=due_date,
            )
            session.add(payment_order)
            session.flush()

            from src.models import Invoice

            for invoice_row in invoice_rows:
                invoice = Invoice(
                    payment_order_id=payment_order.id,
                    invoice_number=invoice_row["factura"],
                    amount=parse_currency(invoice_row["importe"]),
                    supplier_id=supplier_id,
                )
                session.add(invoice)

            session.commit()

            update_account_sequence(account_id, int(op), int(check))

            ui.notify("Orden de pago creada exitosamente", type="positive")

            # Generate PDF if checkbox is checked
            if print_checkbox and print_checkbox.value:
                try:
                    account = session.query(Account).filter_by(id=account_id).first()

                    invoice_total = sum(
                        parse_currency(row.get("importe", "0")) for row in invoice_rows
                    )

                    # Format invoice numbers (concatenate if multiple)
                    invoice_numbers = ", ".join(
                        [row["factura"] for row in invoice_rows]
                    )

                    template_data = {
                        "account_name": account_name,
                        "payment_order_id": str(op),
                        "payment_order_date": order_date_str,
                        "supplier_name": supplier_name,
                        "invoice_amount": format_currency(invoice_total),
                        "detail": detail_value,
                        "witholding_amount": format_currency(withholding_amount),
                        "payment_order_total": format_currency(total_amount),
                        "invoice_number": invoice_numbers,
                        "account_number": account.number if account else "",
                        "check_number": str(check).zfill(8),
                        "issue_date": issue_date_str,
                        "due_date": due_date_str,
                    }

                    output_path = f"orden_pago_{op}.pdf"
                    pdf_path = generate_pdf(
                        "payment_order", [template_data], output_path
                    )
                    ui.notify(f"PDF generado: {Path(pdf_path).name}", type="positive")
                except Exception as e:
                    ui.notify(f"Error al generar PDF: {str(e)}", type="warning")

            if account_select:
                account_select.value = ""
            if supplier_select:
                supplier_select.value = ""
            if detail_select:
                detail_select.value = ""
            if op_input:
                op_input.value = ""
            if check_input:
                check_input.value = ""
            if retenciones_input:
                retenciones_input.value = "$0.00"
            if order_date_input:
                order_date_input.value = ""
            if issue_date_input:
                issue_date_input.value = ""
            if due_date_input:
                due_date_input.value = ""

            invoice_rows.clear()
            if invoice_table:
                invoice_table.rows = invoice_rows
                invoice_table.update()

            if total_op_label:
                total_op_label.text = "$0.00"

        except Exception as e:
            session.rollback()
            ui.notify(f"Error al crear la orden de pago: {str(e)}", type="negative")
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
                    account_select = searchable_select(
                        accounts_data,
                        label="Cuenta",
                        on_change=on_account_change,
                    )

                with ui.column().classes("w-32"):
                    op_input = text_input("OP")

                with ui.column().classes("flex-1"):
                    order_date_input = date_input_with_calendar("Fecha")

            with ui.row().classes("w-full gap-4 mb-4"):
                with ui.column().classes("flex-1"):
                    check_input = text_input("Cheque")

                with ui.column().classes("flex-1"):
                    issue_date_input = date_input_with_calendar("Emisión")

                with ui.column().classes("flex-1"):
                    due_date_input = date_input_with_calendar("Vence")

            with ui.column().classes("w-full mb-4"):
                supplier_select = searchable_select(suppliers_data, label="Proveedor")

            with ui.column().classes("w-full mb-6"):
                detail_select = searchable_select(details_data, label="Detalle")

            with ui.column().classes("w-full items-center"):
                with ui.row().classes(
                    "w-full max-w-2xl justify-between items-center mb-2"
                ):
                    ui.label("Facturas").classes("text-lg font-semibold text-gray-700")
                    primary_button(
                        "Agregar Factura", icon="add", on_click=show_add_invoice_dialog
                    )

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

                invoice_table = (
                    ui.table(columns=columns, rows=invoice_rows, row_key="id")
                    .classes("w-full max-w-2xl")
                    .props("flat bordered")
                )

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

                invoice_table.on("delete_invoice", lambda e: delete_invoice(e.args))

            with ui.row().classes("w-full gap-6 mt-6"):
                with ui.column().classes("flex-1"):
                    retenciones_input = text_input(
                        "Retenciones", value="$0.00", on_change=calculate_totals
                    )

                with ui.card().classes(
                    "flex-1 p-4 bg-gray-50 items-center justify-center"
                ):
                    ui.label("Total OP").classes("text-xs text-gray-500 mb-1")
                    total_op_label = ui.label("$0.00").classes(
                        "text-2xl font-bold text-gray-800"
                    )

            with ui.row().classes("w-full items-center justify-between mt-6"):
                with ui.row().classes("items-center gap-2"):
                    print_checkbox = ui.checkbox(
                        "Imprimir orden de pago", value=True
                    ).classes("text-gray-700")

                primary_button("Agregar OP", on_click=create_payment_order)
