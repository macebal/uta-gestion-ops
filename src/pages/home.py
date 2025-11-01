from nicegui import ui


def home_page():
    """Create the home page with main action buttons"""

    with ui.column().classes("w-full items-center p-8"):
        # Header section
        with ui.column().classes("w-full max-w-6xl items-center mb-8"):
            ui.label("Sistema de Gestión de Órdenes de Pago").classes(
                "text-4xl font-bold text-gray-800 mb-2"
            )
            ui.label("UTA - Unión Tranviarios Automotor").classes(
                "text-xl text-gray-500"
            )

        # Main action buttons - most frequent
        with ui.column().classes("w-full max-w-6xl gap-6 mb-8"):
            ui.label("Acciones Principales").classes(
                "text-2xl font-semibold text-gray-700 mb-2"
            )

            with ui.row().classes("w-full gap-6"):
                # New Payment Order button - large card
                with (
                    ui.card()
                    .classes(
                        "flex-1 p-8 cursor-pointer hover:shadow-xl transition-shadow bg-gradient-to-br from-blue-500 to-blue-600"
                    )
                    .style("min-height: 280px")
                    .on("click", lambda: ui.navigate.to("/create-payment-order"))
                ):
                    with ui.column().classes(
                        "items-center justify-center gap-4 w-full h-full"
                    ):
                        ui.icon("add_circle", size="4rem").classes("text-white")
                        ui.label("Nueva Orden de Pago").classes(
                            "text-2xl font-bold text-white text-center"
                        )
                        ui.label("Crear una nueva OP para un proveedor").classes(
                            "text-blue-100 text-center"
                        )

                # Print button - large card
                with (
                    ui.card()
                    .classes(
                        "flex-1 p-8 hover:shadow-xl transition-shadow bg-gradient-to-br from-green-500 to-green-600"
                    )
                    .style("min-height: 280px")
                ):
                    with ui.column().classes(
                        "items-center justify-center gap-4 w-full h-full"
                    ):
                        ui.icon("print", size="4rem").classes("text-white")
                        ui.label("Imprimir").classes(
                            "text-2xl font-bold text-white text-center"
                        )
                        ui.label("Imprimir órdenes y resúmenes").classes(
                            "text-green-100 text-center"
                        )
                        with ui.row().classes("gap-2 mt-2 justify-center"):
                            ui.button("Orden de Pago", icon="description").props(
                                "color=white text-color=green-600"
                            ).classes(
                                "text-sm hover:shadow-lg hover:scale-105 transition-all"
                            ).on(
                                "click", lambda: ui.navigate.to("/payment-orders/print")
                            )
                            ui.button("Resumen", icon="summarize").props(
                                "flat color=white text-color=green-600"
                            ).classes("text-sm")

        # Management section - less frequent actions
        with ui.column().classes("w-full max-w-6xl gap-4"):
            ui.label("Gestión").classes("text-2xl font-semibold text-gray-700 mb-2")

            with ui.row().classes("w-full gap-4"):
                # Suppliers management
                with (
                    ui.card()
                    .classes(
                        "flex-1 p-6 cursor-pointer hover:shadow-lg transition-shadow"
                    )
                    .on("click", lambda: ui.navigate.to("/manage-suppliers"))
                ):
                    with ui.row().classes("items-center gap-4"):
                        ui.icon("business", size="2.5rem").classes("text-purple-600")
                        with ui.column().classes("gap-1"):
                            ui.label("Proveedores").classes(
                                "text-xl font-semibold text-gray-800"
                            )
                            ui.label("Administrar proveedores").classes(
                                "text-sm text-gray-500"
                            )

                # Accounts management
                with (
                    ui.card()
                    .classes(
                        "flex-1 p-6 cursor-pointer hover:shadow-lg transition-shadow"
                    )
                    .on("click", lambda: ui.navigate.to("/manage-accounts"))
                ):
                    with ui.row().classes("items-center gap-4"):
                        ui.icon("account_balance", size="2.5rem").classes(
                            "text-orange-600"
                        )
                        with ui.column().classes("gap-1"):
                            ui.label("Cuentas").classes(
                                "text-xl font-semibold text-gray-800"
                            )
                            ui.label("Gestionar cuentas").classes(
                                "text-sm text-gray-500"
                            )

                # Details management
                with (
                    ui.card()
                    .classes(
                        "flex-1 p-6 cursor-pointer hover:shadow-lg transition-shadow"
                    )
                    .on("click", lambda: ui.navigate.to("/manage-details"))
                ):
                    with ui.row().classes("items-center gap-4"):
                        ui.icon("list_alt", size="2.5rem").classes("text-teal-600")
                        with ui.column().classes("gap-1"):
                            ui.label("Detalles").classes(
                                "text-xl font-semibold text-gray-800"
                            )
                            ui.label("Gestionar detalles de pago").classes(
                                "text-sm text-gray-500"
                            )
