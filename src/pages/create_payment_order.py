from nicegui import ui


def create_payment_order_page():
    """Create the payment order form page"""

    with ui.card().classes("w-full max-w-4xl mx-auto p-6 shadow-lg"):
        ui.label("Nueva Orden de Pago").classes(
            "text-2xl font-normal text-gray-700 mb-6"
        )

        with ui.row().classes("w-full gap-4 mb-4"):
            with ui.column().classes("flex-1"):
                ui.select(
                    ["Sindical", "Otra Cuenta"], value="Sindical", label="Cuenta"
                ).classes("w-full")

            with ui.column().classes("w-32"):
                ui.input(label="OP", value="123").classes("w-full").props("outlined")

            with ui.column().classes("flex-1"):
                ui.input(label="Fecha", value="01/01/2025").classes("w-full").props(
                    "outlined"
                )

        with ui.row().classes("w-full gap-4 mb-4"):
            with ui.column().classes("flex-1"):
                ui.input(label="Cheque", value="00123456").classes("w-full").props(
                    "outlined"
                )

            with ui.column().classes("flex-1"):
                ui.input(label="Emisión", value="01/01/2025").classes("w-full").props(
                    "outlined"
                )

            with ui.column().classes("flex-1"):
                ui.input(label="Vence", value="01/01/2025").classes("w-full").props(
                    "outlined"
                )

        with ui.column().classes("w-full mb-4"):
            with ui.row().classes("w-full gap-2 items-center"):
                ui.select(
                    ["Juan Pérez S.A.", "Otro Proveedor"],
                    value="Juan Pérez S.A.",
                    label="Proveedor",
                ).classes("flex-1")
                ui.icon("edit").classes("text-yellow-500 cursor-pointer text-xl")

        with ui.column().classes("w-full mb-6"):
            with ui.row().classes("w-full gap-2 items-center"):
                ui.select(
                    ["Pago por XXXXXXXXXX", "Otro Detalle"],
                    value="Pago por XXXXXXXXXX",
                    label="Detalle",
                ).classes("flex-1")
                ui.icon("edit").classes("text-yellow-500 cursor-pointer text-xl")

        with ui.column().classes("w-full items-center"):
            ui.label("Facturas").classes("text-lg font-semibold text-gray-700 mb-2")

            table = (
                ui.table(
                    columns=[
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
                    ],
                    rows=[
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
                    ],
                )
                .classes("w-full max-w-2xl")
                .props("virtual-scroll")
                .style("height: 250px")
            )

            table.add_slot(
                "body-cell-acciones",
                """
                <q-td :props="props">
                    <q-icon name="close" class="text-red-500 cursor-pointer" size="sm" />
                </q-td>
            """,
            )

            with ui.row().classes("w-full max-w-2xl items-center justify-between mt-4"):
                ui.label("$22,000.00").classes("text-lg font-semibold text-gray-800")
                ui.button("Agregar").classes("bg-blue-500 text-white px-4 py-1 rounded")

        with ui.row().classes("w-full gap-6 mt-6"):
            ui.input(label="Retenciones", value="$2,500.00").classes("flex-1").props(
                "outlined"
            )

            with ui.card().classes("flex-1 p-4 bg-gray-50 items-center justify-center"):
                ui.label("Total OP").classes("text-xs text-gray-500 mb-1")
                ui.label("$19,500.00").classes("text-2xl font-bold text-gray-800")

        with ui.row().classes("w-full items-center justify-between mt-6"):
            with ui.row().classes("items-center gap-2"):
                ui.checkbox("Imprimir orden de pago", value=True).classes(
                    "text-gray-700"
                )

            ui.button("Agregar OP").classes(
                "bg-blue-500 text-white px-6 py-2 rounded-lg text-base"
            )
