from nicegui import ui

from src.components import (
    create_invoice_table,
    date_input,
    primary_button,
    select_field,
    select_with_edit,
    text_input,
)


def create_payment_order_page():
    """Create the payment order form page"""

    with ui.column().classes("w-full p-6"):
        with ui.card().classes("w-full max-w-4xl mx-auto p-6 shadow-lg"):
            ui.label("Nueva Orden de Pago").classes(
                "text-2xl font-normal text-gray-700 mb-6"
            )

            with ui.row().classes("w-full gap-4 mb-4"):
                with ui.column().classes("flex-1"):
                    select_field(
                        ["Sindical", "Otra Cuenta"], label="Cuenta", value="Sindical"
                    )

                with ui.column().classes("w-32"):
                    text_input("OP", value="123")

                with ui.column().classes("flex-1"):
                    date_input("Fecha", value="01/01/2025")

            with ui.row().classes("w-full gap-4 mb-4"):
                with ui.column().classes("flex-1"):
                    text_input("Cheque", value="00123456")

                with ui.column().classes("flex-1"):
                    date_input("Emisión", value="01/01/2025")

                with ui.column().classes("flex-1"):
                    date_input("Vence", value="01/01/2025")

            with ui.column().classes("w-full mb-4"):
                select_with_edit(
                    ["Juan Pérez S.A.", "Otro Proveedor"],
                    label="Proveedor",
                    value="Juan Pérez S.A.",
                )

            with ui.column().classes("w-full mb-6"):
                select_with_edit(
                    ["Pago por XXXXXXXXXX", "Otro Detalle"],
                    label="Detalle",
                    value="Pago por XXXXXXXXXX",
                )

            with ui.column().classes("w-full items-center"):
                ui.label("Facturas").classes("text-lg font-semibold text-gray-700 mb-2")

                # Invoice rows data
                invoice_rows = [
                    {
                        "factura": "01-123",
                        "importe": "$10,000.00",
                        "acciones": "delete",
                    },
                    {
                        "factura": "04-567",
                        "importe": "$12,000.00",
                        "acciones": "delete",
                    },
                ]

                create_invoice_table(invoice_rows, total="$22,000.00")

            with ui.row().classes("w-full gap-6 mt-6"):
                with ui.column().classes("flex-1"):
                    text_input("Retenciones", value="$2,500.00")

                with ui.card().classes(
                    "flex-1 p-4 bg-gray-50 items-center justify-center"
                ):
                    ui.label("Total OP").classes("text-xs text-gray-500 mb-1")
                    ui.label("$19,500.00").classes("text-2xl font-bold text-gray-800")

            with ui.row().classes("w-full items-center justify-between mt-6"):
                with ui.row().classes("items-center gap-2"):
                    ui.checkbox("Imprimir orden de pago", value=True).classes(
                        "text-gray-700"
                    )

                primary_button("Agregar OP")
