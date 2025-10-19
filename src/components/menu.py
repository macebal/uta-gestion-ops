from nicegui import app, ui


def create_menu():
    """Create the top menu bar that is visible across all pages"""
    with ui.header().classes("bg-white shadow-sm"):
        with ui.row().classes("w-full items-center gap-0"):
            # File menu
            with ui.button("Archivo", icon="folder").props("flat color=grey-8"):
                with ui.menu():
                    ui.menu_item(
                        "Nueva Orden de Pago",
                        on_click=lambda: ui.navigate.to("/create-payment-order"),
                    )
                    ui.menu_item("Abrir")
                    ui.separator()
                    ui.menu_item("Salir", on_click=app.shutdown)

            # Manage menu
            with ui.button("Gestionar", icon="settings").props("flat color=grey-8"):
                with ui.menu():
                    ui.menu_item(
                        "Proveedores",
                        on_click=lambda: ui.navigate.to("/manage-suppliers"),
                    )
                    ui.menu_item(
                        "Cuentas",
                        on_click=lambda: ui.navigate.to("/manage-accounts"),
                    )
                    ui.menu_item(
                        "Detalles",
                        on_click=lambda: ui.navigate.to("/manage-details"),
                    )
                    ui.menu_item("Configuración")

            # Print menu
            with ui.button("Imprimir", icon="print").props("flat color=grey-8"):
                with ui.menu():
                    ui.menu_item("Orden de Pago")
                    ui.menu_item("Reporte de Órdenes")
                    ui.menu_item("Resumen")
