from collections.abc import Callable
from typing import Any

from nicegui import ui
from sqlalchemy.orm import Session

from src.components import filtered_table, payment_order_form, primary_button
from src.models import PaymentOrder
from src.utils import format_check_number, format_currency, format_date


def manage_payment_orders_page(session_factory: Callable[[], Session]):
    """Create the payment order management page with edit operations"""

    payment_orders_data: list[dict[str, Any]] = []
    table = None
    edit_dialog = None

    def load_payment_orders():
        """Load all payment orders from database"""
        nonlocal payment_orders_data, table
        session = session_factory()
        try:
            payment_orders = session.query(PaymentOrder).order_by(PaymentOrder.order_date.desc()).all()
            payment_orders_data.clear()
            for po in payment_orders:
                payment_orders_data.append(
                    {
                        "id": po.id,
                        "order_number": po.order_number,
                        "check_number": format_check_number(po.check_number),
                        "account": po.account.name,
                        "supplier": po.supplier.name,
                        "order_date": format_date(po.order_date),
                        "issue_date": format_date(po.issue_date),
                        "due_date": format_date(po.due_date),
                        "detail": po.detail.value,
                        "withholding_amount": format_currency(po.withholding_amount),
                        "amount": format_currency(po.amount),
                        "actions": po.id,
                    }
                )
            if table and hasattr(table, "refresh_data"):
                table.refresh_data()
        finally:
            session.close()

    def show_edit_dialog(payment_order_id: int):
        """Show dialog to edit a payment order"""
        nonlocal edit_dialog

        with ui.dialog().props("maximized") as dialog, ui.card().classes("p-6 w-full max-w-6xl"):
            edit_dialog = dialog

            payment_order_form(
                session_factory=session_factory,
                mode="edit",
                payment_order_id=payment_order_id,
                on_save=lambda: (load_payment_orders(), dialog.close()),
                on_cancel=lambda: dialog.close(),
            )

        dialog.open()

    with ui.column().classes("w-full p-6"), ui.card().classes("w-full max-w-full mx-auto p-6 shadow-lg"):
        with ui.row().classes("w-full justify-between items-center mb-4"):
            ui.label("Gestión de Órdenes de Pago").classes("text-2xl font-normal text-gray-700")
            primary_button(
                "Nueva Orden de Pago",
                icon="add_circle",
                on_click=lambda: ui.navigate.to("/payment-orders/create"),
            ).props("color=green")

        ui.separator().classes("mb-6")

        columns = [
            {
                "name": "order_number",
                "label": "OP",
                "field": "order_number",
                "align": "left",
                "sortable": True,
                "type": "number",
            },
            {
                "name": "check_number",
                "label": "Cheque",
                "field": "check_number",
                "align": "left",
                "sortable": True,
                "type": "string",
            },
            {
                "name": "account",
                "label": "Cuenta",
                "field": "account",
                "align": "left",
                "sortable": True,
                "type": "string",
            },
            {
                "name": "supplier",
                "label": "Proveedor",
                "field": "supplier",
                "align": "left",
                "sortable": True,
                "type": "string",
            },
            {
                "name": "order_date",
                "label": "Fecha OP",
                "field": "order_date",
                "align": "left",
                "sortable": True,
                "type": "string",
            },
            {
                "name": "issue_date",
                "label": "Emisión",
                "field": "issue_date",
                "align": "left",
                "sortable": True,
                "type": "string",
            },
            {
                "name": "due_date",
                "label": "Vencimiento",
                "field": "due_date",
                "align": "left",
                "sortable": True,
                "type": "string",
            },
            {
                "name": "detail",
                "label": "Detalle",
                "field": "detail",
                "align": "left",
                "sortable": True,
                "type": "string",
            },
            {
                "name": "withholding_amount",
                "label": "Retenciones",
                "field": "withholding_amount",
                "align": "right",
                "sortable": True,
                "type": "string",
            },
            {
                "name": "amount",
                "label": "Total",
                "field": "amount",
                "align": "right",
                "sortable": True,
                "type": "string",
            },
            {
                "name": "actions",
                "label": "Acciones",
                "field": "actions",
                "align": "center",
            },
        ]

        table = filtered_table(
            columns=columns,
            rows=payment_orders_data,
            row_key="id",
            pagination={
                "rowsPerPage": 10,
                "sortBy": "order_date",
                "descending": True,
            },
        )

        table.props(
            """
                :rows-per-page-options="[10, 20, 50, 0]"
                :rows-per-page-label="'Filas por página:'"
                :pagination-label="(first, last, total) => `${first}-${last} de ${total}`"
            """
        )

        table.classes("horizontal-scroll")
        table.style("overflow-x: auto;")

        table.add_slot(
            "body-cell-actions",
            r"""
                <q-td key="actions" :props="props">
                    <q-btn
                        flat
                        round
                        dense
                        icon="edit"
                        color="blue"
                        @click="() => $parent.$emit('edit_row', props.row)"
                    >
                        <q-tooltip>Editar</q-tooltip>
                    </q-btn>
                </q-td>
                """,
        )

        table.on("edit_row", lambda e: show_edit_dialog(e.args["id"]))

    load_payment_orders()
