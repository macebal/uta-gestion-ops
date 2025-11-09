from collections.abc import Callable
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from nicegui import ui
from sqlalchemy.orm import Session

from src.components.buttons import primary_button, secondary_button
from src.components.inputs import date_input_with_calendar, searchable_select, text_input
from src.models import Account, Detail, Invoice, PaymentOrder, Supplier
from src.services.pdf_generator import generate_pdf
from src.utils import format_check_number, format_currency, format_date, open_file, parse_currency


def payment_order_form(
    session_factory: Callable[[], Session],
    mode: str = "create",
    payment_order_id: int | None = None,
    on_save: Callable | None = None,
    on_cancel: Callable | None = None,
):
    """
    Create a payment order form that works in both create and edit modes.

    Args:
        session_factory: Function to create database sessions
        mode: "create" or "edit"
        payment_order_id: ID of payment order to edit (only for edit mode)
        on_save: Callback function after successful save
        on_cancel: Callback function when cancel is clicked
    """
    is_edit_mode = mode == "edit"

    accounts_data: list[str] = []
    suppliers_data: list[str] = []
    details_data: list[str] = []
    invoice_rows: list[dict] = []

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
    export_checkbox = None
    invoice_counter_label = None
    add_invoice_button = None
    supplier_add_button = None
    detail_add_button = None

    payment_order_data = None

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

    def show_create_supplier_dialog():
        """Show dialog to create a new supplier"""
        with ui.dialog() as dialog, ui.card().classes("p-6 min-w-96"):
            ui.label("Nuevo Proveedor").classes("text-xl font-semibold mb-4")

            name_input = text_input("Nombre del Proveedor")
            cuit_input = text_input("CUIT")
            phone_input = text_input("Teléfono")
            email_input = text_input("Email")

            def create_supplier():
                name = name_input.value
                cuit = cuit_input.value
                phone = phone_input.value
                email = email_input.value

                if not name:
                    ui.notify("Por favor ingrese el nombre del proveedor", type="negative")
                    return

                session = session_factory()
                try:
                    existing = session.query(Supplier).filter_by(name=name).first()
                    if existing:
                        ui.notify("Ya existe un proveedor con este nombre", type="negative")
                        return

                    new_supplier = Supplier(
                        name=name,
                        cuit=cuit if cuit else None,
                        phone=phone if phone else None,
                        email=email if email else None,
                    )
                    session.add(new_supplier)
                    session.commit()

                    ui.notify("Proveedor creado exitosamente", type="positive")
                    load_suppliers()

                    if supplier_select:
                        supplier_select.set_options(suppliers_data)
                        supplier_select.value = name
                        if add_invoice_button:
                            add_invoice_button.enabled = True

                    dialog.close()
                except Exception as e:
                    session.rollback()
                    ui.notify(f"Error al crear proveedor: {str(e)}", type="negative")
                finally:
                    session.close()

            with ui.row().classes("w-full gap-4 mt-6 justify-end"):
                secondary_button("Cancelar", on_click=lambda: dialog.close())
                primary_button("Crear", on_click=create_supplier)

        dialog.open()

    def show_create_detail_dialog():
        """Show dialog to create a new detail"""
        with ui.dialog() as dialog, ui.card().classes("p-6 min-w-96"):
            ui.label("Nuevo Detalle").classes("text-xl font-semibold mb-4")

            value_input = text_input("Detalle")

            def create_detail():
                value = value_input.value

                if not value:
                    ui.notify("Por favor ingrese el detalle", type="negative")
                    return

                session = session_factory()
                try:
                    existing = session.query(Detail).filter_by(value=value).first()
                    if existing:
                        ui.notify("Ya existe un detalle con este texto", type="negative")
                        return

                    new_detail = Detail(value=value)
                    session.add(new_detail)
                    session.commit()

                    ui.notify("Detalle creado exitosamente", type="positive")
                    load_details()

                    if detail_select:
                        detail_select.set_options(details_data)
                        detail_select.value = value

                    dialog.close()
                except Exception as e:
                    session.rollback()
                    ui.notify(f"Error al crear detalle: {str(e)}", type="negative")
                finally:
                    session.close()

            with ui.row().classes("w-full gap-4 mt-6 justify-end"):
                secondary_button("Cancelar", on_click=lambda: dialog.close())
                primary_button("Crear", on_click=create_detail)

        dialog.open()

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
        if is_edit_mode:
            return

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
                    check_input.value = format_check_number(next_check)
            elif account:
                if op_input:
                    op_input.value = "1"
                if check_input:
                    check_input.value = format_check_number(1)
        finally:
            session.close()

    def on_supplier_change(e):
        """Handle supplier selection change"""
        nonlocal add_invoice_button
        if add_invoice_button:
            add_invoice_button.enabled = bool(e.value)

    def compute_invoice_total():
        """Compute total from current invoice rows"""
        return format_currency(sum(parse_currency(row.get("importe", "0")) for row in invoice_rows))

    def update_invoice_total_display():
        """Update the invoice total display"""
        element_id = "edit-total-facturas" if is_edit_mode else "total-facturas"
        total = compute_invoice_total()
        ui.run_javascript(f'const el = document.getElementById("{element_id}"); if (el) el.innerText = "{total}";')

    def calculate_total_op():
        """Calculate and update total OP based on invoices and withholdings"""
        nonlocal total_op_label, retenciones_input

        invoice_total = sum(parse_currency(row.get("importe", "0")) for row in invoice_rows)

        withholdings = Decimal("0.00")
        if retenciones_input and retenciones_input.value:
            withholdings = parse_currency(retenciones_input.value)

        total_op = invoice_total - withholdings

        if total_op_label:
            total_op_label.text = format_currency(total_op)

    def add_invoice(invoice_number: str, amount: str):
        """Add an invoice to the list"""
        nonlocal invoice_table, add_invoice_dialog, invoice_counter_label

        if len(invoice_rows) >= 5:
            ui.notify("No se pueden agregar más de 5 facturas", type="negative")
            return

        if not invoice_number or not amount:
            ui.notify("Por favor complete todos los campos", type="negative")
            return

        if any(row.get("factura") == invoice_number for row in invoice_rows):
            ui.notify(
                f"La factura {invoice_number} ya fue agregada a esta orden de pago",
                type="negative",
            )
            return

        if is_edit_mode and payment_order_data:
            supplier_name = payment_order_data["supplier"]
        else:
            supplier_name = supplier_select.value if supplier_select else ""
            if not supplier_name:
                ui.notify("Por favor seleccione un proveedor primero", type="negative")
                return

        supplier_id = get_supplier_id_by_name(supplier_name)
        if not supplier_id:
            ui.notify("Error al obtener datos del proveedor", type="negative")
            return

        session = session_factory()
        try:
            query = session.query(Invoice).filter_by(invoice_number=invoice_number, supplier_id=supplier_id)

            if is_edit_mode and payment_order_id:
                query = query.filter(Invoice.payment_order_id != payment_order_id)

            existing_invoice = query.first()

            if existing_invoice:
                payment_order = existing_invoice.payment_order
                error_msg = (
                    f"La factura {invoice_number} ya fue procesada en la "
                    f"orden de pago #{payment_order.order_number}, "
                    f"cuenta {payment_order.account.name}, "
                    f"cheque {format_check_number(payment_order.check_number)}, "
                    f"fecha {format_date(payment_order.order_date)}"
                )
                ui.notify(error_msg, type="negative")
                return

            parsed_amount = parse_currency(amount)
            if parsed_amount <= 0:
                ui.notify("El importe debe ser mayor a 0", type="negative")
                return

            next_id = max([row.get("id", 0) for row in invoice_rows], default=0) + 1
            invoice_rows.append(
                {
                    "id": next_id,
                    "factura": invoice_number,
                    "importe": format_currency(parsed_amount),
                    "is_new": is_edit_mode,
                    "is_modified": False,
                }
            )

            if invoice_table:
                invoice_table.rows = invoice_rows
                invoice_table.update()

            update_invoice_total_display()
            calculate_total_op()

            if invoice_counter_label:
                invoice_counter_label.text = f"{len(invoice_rows)}/5"

            if add_invoice_dialog:
                add_invoice_dialog.close()

            ui.notify("Factura agregada exitosamente", type="positive")

        except Exception as e:
            ui.notify(f"Error al agregar factura: {str(e)}", type="negative")
        finally:
            session.close()

    def edit_invoice_amount(row_data, new_amount: str):
        """Edit an invoice amount"""
        nonlocal invoice_table

        try:
            parsed_amount = parse_currency(new_amount)
            if parsed_amount <= 0:
                ui.notify("El importe debe ser mayor a 0", type="negative")
                return

            for row in invoice_rows:
                if row.get("id") == row_data.get("id"):
                    row["importe"] = format_currency(parsed_amount)
                    if is_edit_mode:
                        row["is_modified"] = True
                    break

            if invoice_table:
                invoice_table.rows = invoice_rows
                invoice_table.update()

            update_invoice_total_display()
            calculate_total_op()

            ui.notify("Importe actualizado exitosamente", type="positive")

        except Exception as e:
            ui.notify(f"Error al actualizar importe: {str(e)}", type="negative")

    def delete_invoice(row_data):
        """Delete an invoice from the list"""
        nonlocal invoice_table, invoice_counter_label

        try:
            invoice_rows[:] = [row for row in invoice_rows if row.get("id") != row_data.get("id")]

            if invoice_table:
                invoice_table.rows = invoice_rows
                invoice_table.update()

            update_invoice_total_display()
            calculate_total_op()

            if invoice_counter_label:
                invoice_counter_label.text = f"{len(invoice_rows)}/5"

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
                    on_click=lambda: add_invoice(invoice_number_input.value, amount_input.value),
                )

        dialog.open()

    def show_edit_invoice_dialog(row_data):
        """Show dialog to edit an invoice amount"""
        with ui.dialog() as dialog, ui.card().classes("p-6 min-w-96"):
            ui.label("Editar Importe de Factura").classes("text-xl font-semibold mb-4")

            ui.label(f"Factura: {row_data.get('factura', '')}").classes("text-gray-600 mb-4")
            amount_input = text_input("Importe", value=row_data.get("importe", "$0.00"))

            with ui.row().classes("w-full gap-4 mt-6 justify-end"):
                secondary_button(
                    "Cancelar",
                    on_click=lambda: dialog.close(),
                )
                primary_button(
                    "Guardar",
                    on_click=lambda: (edit_invoice_amount(row_data, amount_input.value), dialog.close()),
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
            ui.notify(f"Error al actualizar secuencia de cuenta: {str(e)}", type="negative")
        finally:
            session.close()

    def save_payment_order():
        """Save payment order (create or update based on mode)"""
        if is_edit_mode:
            save_edit()
        else:
            save_create()

    def save_create():
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
            ui.notify("Por favor complete todos los campos obligatorios", type="negative")
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
        total_amount = parse_currency(total_op_label.text if total_op_label else "$0.00")

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

            if export_checkbox and export_checkbox.value:
                try:
                    account = session.query(Account).filter_by(id=account_id).first()

                    invoice_numbers = ", ".join([row["factura"] for row in invoice_rows])
                    invoices_list = [{"amount": parse_currency(row.get("importe", "0"))} for row in invoice_rows]

                    template_data = {
                        "account_name": account_name,
                        "payment_order_id": str(op),
                        "payment_order_date": order_date,
                        "supplier_name": supplier_name,
                        "invoices": invoices_list,
                        "detail": detail_value,
                        "withholding_amount": withholding_amount,
                        "payment_order_total": total_amount,
                        "invoice_number": invoice_numbers,
                        "account_number": account.number if account else "",
                        "check_number": int(check),
                        "issue_date": issue_date,
                        "due_date": due_date,
                    }

                    base_dir = Path("ordenes de pago") / account_name.lower()
                    base_dir.mkdir(parents=True, exist_ok=True)

                    date_str = order_date.strftime("%Y%m%d")
                    filename = f"orden_de_pago_{op}_{date_str}.pdf"
                    output_path = base_dir / filename

                    pdf_path = generate_pdf("payment_order", [template_data], str(output_path))
                    ui.notify(f"PDF generado: {Path(pdf_path).name}", type="positive")

                    open_file(pdf_path)
                except Exception as e:
                    ui.notify(f"Error al generar PDF: {str(e)}", type="warning")

            reset_form()

            if on_save:
                on_save()

        except Exception as e:
            session.rollback()
            ui.notify(f"Error al crear la orden de pago: {str(e)}", type="negative")
        finally:
            session.close()

    def save_edit():
        """Update an existing payment order"""
        detail_value = detail_select.value if detail_select else ""
        withholding = retenciones_input.value if retenciones_input else "$0.00"
        generate_pdf_flag = export_checkbox.value if export_checkbox else False

        if not detail_value:
            ui.notify("Por favor seleccione un detalle", type="negative")
            return

        if not invoice_rows:
            ui.notify("Debe tener al menos una factura", type="negative")
            return

        session = session_factory()
        try:
            payment_order = session.query(PaymentOrder).filter_by(id=payment_order_id).first()
            if not payment_order:
                ui.notify("Orden de pago no encontrada", type="negative")
                return

            detail = session.query(Detail).filter_by(value=detail_value).first()
            if not detail:
                ui.notify("Detalle no encontrado", type="negative")
                return

            withholding_amount = parse_currency(withholding)
            invoice_total = sum(parse_currency(row.get("importe", "0")) for row in invoice_rows)
            total_amount = invoice_total - withholding_amount

            payment_order.detail_id = detail.id
            payment_order.withholding_amount = withholding_amount
            payment_order.amount = total_amount

            existing_invoice_ids = set()
            for row in invoice_rows:
                if row.get("is_new"):
                    invoice = Invoice(
                        payment_order_id=payment_order.id,
                        invoice_number=row["factura"],
                        amount=parse_currency(row["importe"]),
                        supplier_id=payment_order.supplier_id,
                    )
                    session.add(invoice)
                else:
                    existing_invoice_ids.add(row.get("invoice_id"))
                    invoice = session.query(Invoice).filter_by(id=row.get("invoice_id")).first()
                    if invoice and row.get("is_modified"):
                        invoice.amount = parse_currency(row["importe"])

            for invoice in payment_order.invoices:
                if invoice.id not in existing_invoice_ids:
                    session.delete(invoice)

            session.commit()

            ui.notify("Orden de pago actualizada exitosamente", type="positive")

            if generate_pdf_flag:
                try:
                    session.refresh(payment_order)
                    account = session.query(Account).filter_by(id=payment_order.account_id).first()

                    invoice_numbers = ", ".join([row["factura"] for row in invoice_rows])
                    invoices_list = [{"amount": parse_currency(row.get("importe", "0"))} for row in invoice_rows]

                    template_data = {
                        "account_name": payment_order.account.name,
                        "payment_order_id": str(payment_order.order_number),
                        "payment_order_date": payment_order.order_date,
                        "supplier_name": payment_order.supplier.name,
                        "invoices": invoices_list,
                        "detail": detail_value,
                        "withholding_amount": withholding_amount,
                        "payment_order_total": total_amount,
                        "invoice_number": invoice_numbers,
                        "account_number": account.number if account else "",
                        "check_number": payment_order.check_number,
                        "issue_date": payment_order.issue_date,
                        "due_date": payment_order.due_date,
                    }

                    base_dir = Path("ordenes de pago") / payment_order.account.name.lower()
                    base_dir.mkdir(parents=True, exist_ok=True)

                    date_str = payment_order.order_date.strftime("%Y%m%d")
                    filename = f"orden_de_pago_{payment_order.order_number}_{date_str}.pdf"
                    output_path = base_dir / filename

                    pdf_path = generate_pdf("payment_order", [template_data], str(output_path))
                    ui.notify(f"PDF generado: {Path(pdf_path).name}", type="positive")

                    open_file(pdf_path)
                except Exception as e:
                    ui.notify(f"Error al generar PDF: {str(e)}", type="warning")

            if on_save:
                on_save()

        except Exception as e:
            session.rollback()
            ui.notify(f"Error al actualizar orden de pago: {str(e)}", type="negative")
        finally:
            session.close()

    def reset_form():
        """Reset form to initial state (for create mode)"""
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

        if invoice_counter_label:
            invoice_counter_label.text = "0/5"

        if add_invoice_button:
            add_invoice_button.enabled = False

    def load_payment_order_data():
        """Load payment order data for edit mode"""
        nonlocal payment_order_data

        if not is_edit_mode or not payment_order_id:
            return

        session = session_factory()
        try:
            payment_order = session.query(PaymentOrder).filter_by(id=payment_order_id).first()
            if not payment_order:
                ui.notify("Orden de pago no encontrada", type="negative")
                return

            payment_order_data = {
                "id": payment_order.id,
                "order_number": payment_order.order_number,
                "check_number": payment_order.check_number,
                "account": payment_order.account.name,
                "supplier": payment_order.supplier.name,
                "order_date": payment_order.order_date,
                "issue_date": payment_order.issue_date,
                "due_date": payment_order.due_date,
                "detail": payment_order.detail.value,
                "withholding_amount": payment_order.withholding_amount,
                "amount": payment_order.amount,
            }

            invoice_rows.clear()
            for idx, invoice in enumerate(payment_order.invoices):
                invoice_rows.append(
                    {
                        "id": idx + 1,
                        "invoice_id": invoice.id,
                        "factura": invoice.invoice_number,
                        "importe": format_currency(invoice.amount),
                        "is_new": False,
                        "is_modified": False,
                    }
                )

        finally:
            session.close()

    load_accounts()
    load_suppliers()
    load_details()

    if is_edit_mode:
        load_payment_order_data()

    title = "Nueva Orden de Pago" if not is_edit_mode else "Editar Orden de Pago"
    ui.label(title).classes("text-2xl font-normal text-gray-700 mb-6")

    if is_edit_mode and payment_order_data:
        with ui.row().classes("w-full gap-4 mb-4"):
            with ui.column().classes("flex-1"):
                ui.label("Cuenta").classes("text-sm text-gray-600")
                ui.label(payment_order_data["account"]).classes("text-base font-semibold")

            with ui.column().classes("w-32"):
                ui.label("OP").classes("text-sm text-gray-600")
                ui.label(str(payment_order_data["order_number"])).classes("text-base font-semibold")

            with ui.column().classes("flex-1"):
                ui.label("Fecha").classes("text-sm text-gray-600")
                ui.label(format_date(payment_order_data["order_date"])).classes("text-base font-semibold")

        with ui.row().classes("w-full gap-4 mb-4"):
            with ui.column().classes("flex-1"):
                ui.label("Cheque").classes("text-sm text-gray-600")
                ui.label(format_check_number(payment_order_data["check_number"])).classes("text-base font-semibold")

            with ui.column().classes("flex-1"):
                ui.label("Emisión").classes("text-sm text-gray-600")
                ui.label(format_date(payment_order_data["issue_date"])).classes("text-base font-semibold")

            with ui.column().classes("flex-1"):
                ui.label("Vence").classes("text-sm text-gray-600")
                ui.label(format_date(payment_order_data["due_date"])).classes("text-base font-semibold")

        with ui.column().classes("w-full mb-4"):
            ui.label("Proveedor").classes("text-sm text-gray-600")
            ui.label(payment_order_data["supplier"]).classes("text-base font-semibold")
    else:
        with ui.row().classes("w-full gap-4 mb-4"):
            with ui.column().classes("flex-1"):
                account_select = searchable_select(
                    accounts_data,
                    label="Cuenta",
                    on_change=on_account_change,
                )

            with ui.column().classes("w-32"):
                op_input = text_input("OP", readonly=True)

            with ui.column().classes("flex-1"):
                today = datetime.now().strftime("%d/%m/%Y")
                order_date_input = date_input_with_calendar("Fecha", value=today)

        with ui.row().classes("w-full gap-4 mb-4"):
            with ui.column().classes("flex-1"):
                check_input = text_input("Cheque", readonly=True)

            with ui.column().classes("flex-1"):
                issue_date_input = date_input_with_calendar("Emisión")

            with ui.column().classes("flex-1"):
                due_date_input = date_input_with_calendar("Vence")

        with ui.row().classes("w-full mb-4 gap-2 items-end"):
            with ui.column().classes("flex-1"):
                supplier_select = searchable_select(suppliers_data, label="Proveedor", on_change=on_supplier_change)

            supplier_add_button = ui.button(icon="add").props("round flat color=primary").classes("mb-1")
            supplier_add_button.on("click", show_create_supplier_dialog)
            supplier_add_button.tooltip("Crear nuevo proveedor")
            if is_edit_mode:
                supplier_add_button.disable()

    with ui.row().classes("w-full mb-6 gap-2 items-end"):
        with ui.column().classes("flex-1"):
            detail_select = searchable_select(details_data, label="Detalle")
            if is_edit_mode and payment_order_data:
                detail_select.value = payment_order_data["detail"]

        detail_add_button = ui.button(icon="add").props("round flat color=primary").classes("mb-1")
        detail_add_button.on("click", show_create_detail_dialog)
        detail_add_button.tooltip("Crear nuevo detalle")

    with ui.column().classes("w-full items-center"):
        max_width_class = "max-w-4xl" if is_edit_mode else "max-w-2xl"
        with ui.row().classes(f"w-full {max_width_class} justify-between items-center mb-2"):
            with ui.row().classes("items-center gap-2"):
                ui.label("Facturas").classes("text-lg font-semibold text-gray-700")
                initial_count = len(invoice_rows) if is_edit_mode else 0
                invoice_counter_label = ui.label(f"{initial_count}/5").classes("text-sm text-gray-500")
            add_invoice_button = primary_button("Agregar Factura", icon="add", on_click=show_add_invoice_dialog)
            if not is_edit_mode:
                add_invoice_button.enabled = False

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
            .classes(f"w-full {max_width_class}")
            .props("flat bordered no-data-label='No hay datos disponibles'")
        )

        invoice_table.add_slot(
            "body-cell-acciones",
            r"""
                <q-td :props="props">
                    <q-btn
                        flat
                        round
                        dense
                        icon="edit"
                        color="blue"
                        @click="() => $parent.$emit('edit_invoice', props.row)"
                    >
                        <q-tooltip>Editar Importe</q-tooltip>
                    </q-btn>
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

        initial_invoice_total = compute_invoice_total()
        element_id = "edit-total-facturas" if is_edit_mode else "total-facturas"

        invoice_table.add_slot(
            "bottom-row",
            f"""
                <q-tr class="bg-gray-50">
                    <q-td class="text-left font-bold">Total</q-td>
                    <q-td class="text-right">
                        <div id="{element_id}" class="text-lg font-semibold text-gray-800">{initial_invoice_total}</div>
                    </q-td>
                    <q-td></q-td>
                </q-tr>
                """,
        )

        invoice_table.on("edit_invoice", lambda e: show_edit_invoice_dialog(e.args))
        invoice_table.on("delete_invoice", lambda e: delete_invoice(e.args))

    with ui.row().classes("w-full gap-6 mt-6"):
        with ui.column().classes("flex-1"):
            initial_withholding = "$0.00"
            if is_edit_mode and payment_order_data:
                initial_withholding = format_currency(payment_order_data["withholding_amount"])
            retenciones_input = text_input("Retenciones", value=initial_withholding, on_change=calculate_total_op)

        with ui.card().classes("flex-1 p-4 bg-gray-50 items-center justify-center"):
            ui.label("Total OP").classes("text-xs text-gray-500 mb-1")
            initial_total = "$0.00"
            if is_edit_mode and payment_order_data:
                initial_total = format_currency(payment_order_data["amount"])
            total_op_label = ui.label(initial_total).classes("text-2xl font-bold text-gray-800")

    with ui.row().classes("w-full items-center justify-between mt-6"):
        with ui.row().classes("items-center gap-2"):
            initial_checkbox_value = not is_edit_mode
            export_checkbox = ui.checkbox("Generar PDF de orden de pago", value=initial_checkbox_value).classes(
                "text-gray-700"
            )

        with ui.row().classes("gap-4"):
            if on_cancel:
                secondary_button("Cancelar", on_click=on_cancel)

            button_text = "Agregar OP" if not is_edit_mode else "Guardar Cambios"
            primary_button(button_text, on_click=save_payment_order)

    if is_edit_mode:
        ui.timer(0.3, lambda: (update_invoice_total_display(), calculate_total_op()), once=True)
