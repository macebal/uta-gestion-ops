from typing import Callable
from decimal import Decimal
from datetime import datetime

from nicegui import ui
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.components import (
    primary_button,
    searchable_select,
    secondary_button,
    text_input,
)
from src.models import Account, PaymentOrder
from src.services.pdf_generator import create_multiple_payment_orders_pdf


def print_payment_orders_page(session_factory: Callable[[], Session]):
    """Create the print payment orders page"""

    accounts_data: list[str] = []
    filtered_orders: list[dict] = []
    active_filters: list[dict] = []

    account_select = None
    results_table = None
    print_button_container = None
    filters_container = None
    add_filter_dialog = None

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

    def format_currency(amount: float | Decimal | str) -> str:
        """Format a number as currency"""
        if isinstance(amount, str):
            amount = amount.replace("$", "").replace(",", "")
            try:
                amount = float(amount)
            except ValueError:
                amount = 0
        return f"${amount:,.2f}"

    def format_date(date_obj) -> str:
        """Format date as DD/MM/YYYY"""
        if isinstance(date_obj, str):
            return date_obj
        return date_obj.strftime("%d/%m/%Y")

    def render_filters():
        """Render active filters as chips"""
        nonlocal filters_container
        if filters_container:
            filters_container.clear()
            with filters_container:
                if not active_filters:
                    ui.label("No hay filtros activos").classes("text-gray-500 text-sm")
                else:
                    with ui.row().classes("gap-2 flex-wrap"):
                        for filter_item in active_filters:
                            filter_type = filter_item["type"]
                            if filter_type == "order_range":
                                label = (
                                    f"OP: {filter_item['from']} - {filter_item['to']}"
                                )
                            elif filter_type == "check_range":
                                label = f"Cheque: {filter_item['from']} - {filter_item['to']}"

                            with ui.chip(label, removable=True).classes(
                                "bg-blue-100"
                            ) as chip:
                                chip.on(
                                    "remove", lambda f=filter_item: remove_filter(f)
                                )

    def add_filter(filter_type: str, from_value: str, to_value: str):
        """Add a new filter"""
        nonlocal add_filter_dialog

        if not from_value or not to_value:
            ui.notify("Por favor complete ambos campos", type="negative")
            return

        try:
            from_num = int(from_value)
            to_num = int(to_value)

            if from_num > to_num:
                ui.notify(
                    "El valor 'Desde' debe ser menor o igual que 'Hasta'",
                    type="negative",
                )
                return

            for existing_filter in active_filters:
                if existing_filter["type"] == filter_type:
                    ui.notify(
                        "Ya existe un filtro de este tipo. Elimínelo primero.",
                        type="negative",
                    )
                    return

            active_filters.append(
                {
                    "type": filter_type,
                    "from": from_num,
                    "to": to_num,
                }
            )

            render_filters()
            apply_filters()

            if add_filter_dialog:
                add_filter_dialog.close()

            ui.notify("Filtro agregado", type="positive")

        except ValueError:
            ui.notify("Los valores deben ser números enteros", type="negative")

    def remove_filter(filter_item: dict):
        """Remove a filter"""
        active_filters.remove(filter_item)
        render_filters()
        apply_filters()
        ui.notify("Filtro eliminado", type="positive")

    def show_add_filter_dialog():
        """Show dialog to add a new filter"""
        nonlocal add_filter_dialog

        with ui.dialog() as dialog, ui.card().classes("p-6 min-w-96"):
            add_filter_dialog = dialog
            ui.label("Agregar Filtro").classes("text-xl font-semibold mb-4")

            filter_type_select = ui.select(
                options={
                    "order_range": "Rango de Órdenes de Pago",
                    "check_range": "Rango de Cheques",
                },
                label="Tipo de Filtro",
                value="order_range",
            ).classes("w-full mb-4")

            from_input = text_input("Desde")
            to_input = text_input("Hasta")

            with ui.row().classes("w-full gap-4 mt-6 justify-end"):
                secondary_button(
                    "Cancelar",
                    on_click=lambda: dialog.close(),
                )
                primary_button(
                    "Agregar",
                    on_click=lambda: add_filter(
                        filter_type_select.value, from_input.value, to_input.value
                    ),
                )

        dialog.open()

    def apply_filters():
        """Apply all active filters and load payment orders"""
        nonlocal filtered_orders, results_table, print_button_container

        account_name = account_select.value if account_select else ""
        if not account_name:
            if active_filters:
                ui.notify("Por favor seleccione una cuenta", type="negative")
            return

        account_id = get_account_id_by_name(account_name)
        if not account_id:
            ui.notify("Cuenta no encontrada", type="negative")
            return

        session = session_factory()
        try:
            query = session.query(PaymentOrder).filter(
                PaymentOrder.account_id == account_id
            )

            for filter_item in active_filters:
                if filter_item["type"] == "order_range":
                    query = query.filter(
                        and_(
                            PaymentOrder.order_number >= filter_item["from"],
                            PaymentOrder.order_number <= filter_item["to"],
                        )
                    )
                elif filter_item["type"] == "check_range":
                    query = query.filter(
                        and_(
                            PaymentOrder.check_number >= filter_item["from"],
                            PaymentOrder.check_number <= filter_item["to"],
                        )
                    )

            payment_orders = query.order_by(PaymentOrder.order_number).all()

            filtered_orders.clear()
            for po in payment_orders:
                filtered_orders.append(
                    {
                        "id": po.id,
                        "order_number": po.order_number,
                        "check_number": str(po.check_number).zfill(8),
                        "supplier_name": po.supplier.name if po.supplier else "",
                        "detail": po.detail.value if po.detail else "",
                        "amount": format_currency(po.amount),
                        "withholding": format_currency(po.withholding_amount),
                        "total": format_currency(po.amount),
                        "order_date": format_date(po.order_date),
                        "issue_date": format_date(po.issue_date),
                        "due_date": format_date(po.due_date),
                    }
                )

            if results_table:
                results_table.rows = filtered_orders
                results_table.update()

            if print_button_container:
                print_button_container.clear()
                if filtered_orders:
                    with print_button_container:
                        primary_button(
                            "Imprimir PDFs", icon="print", on_click=generate_pdf
                        )

            if active_filters:
                ui.notify(
                    f"Se encontraron {len(filtered_orders)} órdenes de pago",
                    type="positive",
                )

        except Exception as e:
            ui.notify(f"Error al cargar órdenes: {str(e)}", type="negative")
        finally:
            session.close()

    def generate_pdf():
        """Generate PDF with all filtered payment orders"""
        if not filtered_orders:
            ui.notify("No hay órdenes para imprimir", type="negative")
            return

        session = session_factory()
        try:
            payment_orders_data = []

            for order_row in filtered_orders:
                po = session.query(PaymentOrder).filter_by(id=order_row["id"]).first()
                if not po:
                    continue

                account = po.account
                invoices = po.invoices

                invoice_total = sum(invoice.amount for invoice in invoices)
                invoice_numbers = ", ".join(
                    [invoice.invoice_number for invoice in invoices]
                )

                template_data = {
                    "account_name": account.name if account else "",
                    "payment_order_id": str(po.order_number),
                    "payment_order_date": format_date(po.order_date),
                    "supplier_name": po.supplier.name if po.supplier else "",
                    "invoice_amount": format_currency(invoice_total),
                    "detail": po.detail.value if po.detail else "",
                    "witholding_amount": format_currency(po.withholding_amount),
                    "payment_order_total": format_currency(po.amount),
                    "invoice_number": invoice_numbers,
                    "account_number": account.number if account else "",
                    "check_number": str(po.check_number).zfill(8),
                    "issue_date": format_date(po.issue_date),
                    "due_date": format_date(po.due_date),
                }

                payment_orders_data.append(template_data)

            if not payment_orders_data:
                ui.notify(
                    "No se pudieron cargar los datos de las órdenes", type="negative"
                )
                return

            ui.notify(
                f"Generando PDF con {len(payment_orders_data)} órdenes...", type="info"
            )

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"ordenes_pago_{timestamp}.pdf"
            create_multiple_payment_orders_pdf(payment_orders_data, output_path)

            ui.notify(f"PDF generado exitosamente: {output_path}", type="positive")

        except Exception as e:
            ui.notify(f"Error al generar PDF: {str(e)}", type="negative")
        finally:
            session.close()

    load_accounts()

    with ui.column().classes("w-full p-6"):
        with ui.card().classes("w-full max-w-6xl mx-auto p-6 shadow-lg"):
            ui.label("Imprimir Órdenes de Pago").classes(
                "text-2xl font-normal text-gray-700 mb-6"
            )

            with ui.column().classes("w-full gap-4 mb-6"):
                with ui.row().classes("w-full gap-4"):
                    with ui.column().classes("flex-1"):
                        account_select = searchable_select(
                            accounts_data,
                            label="Cuenta",
                            on_change=lambda: apply_filters(),
                        )

                with ui.row().classes("w-full items-center justify-between mt-4"):
                    ui.label("Filtros").classes("text-lg font-semibold text-gray-700")
                    primary_button(
                        "Agregar Filtro", icon="add", on_click=show_add_filter_dialog
                    )

                filters_container = ui.column().classes("w-full min-h-8 py-2")
                render_filters()

            ui.separator().classes("my-6")

            ui.label("Resultados").classes("text-lg font-semibold text-gray-700 mb-4")

            columns = [
                {
                    "name": "order_number",
                    "label": "OP",
                    "field": "order_number",
                    "align": "left",
                    "sortable": True,
                },
                {
                    "name": "check_number",
                    "label": "Cheque",
                    "field": "check_number",
                    "align": "left",
                    "sortable": True,
                },
                {
                    "name": "supplier_name",
                    "label": "Proveedor",
                    "field": "supplier_name",
                    "align": "left",
                    "sortable": True,
                },
                {
                    "name": "detail",
                    "label": "Detalle",
                    "field": "detail",
                    "align": "left",
                    "sortable": True,
                },
                {
                    "name": "amount",
                    "label": "Importe",
                    "field": "amount",
                    "align": "right",
                    "sortable": True,
                },
                {
                    "name": "withholding",
                    "label": "Retenciones",
                    "field": "withholding",
                    "align": "right",
                    "sortable": True,
                },
                {
                    "name": "total",
                    "label": "Total",
                    "field": "total",
                    "align": "right",
                    "sortable": True,
                },
                {
                    "name": "order_date",
                    "label": "Fecha OP",
                    "field": "order_date",
                    "align": "center",
                    "sortable": True,
                },
                {
                    "name": "issue_date",
                    "label": "Emisión",
                    "field": "issue_date",
                    "align": "center",
                    "sortable": True,
                },
                {
                    "name": "due_date",
                    "label": "Vencimiento",
                    "field": "due_date",
                    "align": "center",
                    "sortable": True,
                },
            ]

            results_table = (
                ui.table(
                    columns=columns,
                    rows=filtered_orders,
                    row_key="id",
                    pagination={"rowsPerPage": 10, "sortBy": "order_number"},
                )
                .classes("w-full")
                .props("flat bordered")
            )

            print_button_container = ui.row().classes("w-full justify-end mt-6")
