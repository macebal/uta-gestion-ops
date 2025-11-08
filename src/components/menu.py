from nicegui import app, ui


def create_menu():
    """Create the top menu bar that is visible across all pages"""
    with ui.header().classes("bg-white shadow-sm"), ui.row().classes("w-full items-center gap-0"):
        # Home button
        ui.button(icon="home").props("flat color=grey-8").on(
            "click", lambda: ui.navigate.to("/")
        ).tooltip("Inicio")

        # File menu
        with ui.button("Archivo", icon="folder").props("flat color=grey-8"), ui.menu():
            ui.menu_item(
                "Nueva Orden de Pago",
                on_click=lambda: ui.navigate.to("/payment-orders/create"),
            )
            ui.separator()
            ui.menu_item("Salir", on_click=app.shutdown)

        # Manage menu
        with ui.button("Gestionar", icon="settings").props("flat color=grey-8"), ui.menu():
            ui.menu_item(
                "Proveedores",
                on_click=lambda: ui.navigate.to("/suppliers/manage"),
            )
            ui.menu_item(
                "Cuentas",
                on_click=lambda: ui.navigate.to("/accounts/manage"),
            )
            ui.menu_item(
                "Detalles",
                on_click=lambda: ui.navigate.to("/details/manage"),
            )

        # Print menu
        with ui.button("Imprimir", icon="print").props("flat color=grey-8"), ui.menu():
            ui.menu_item(
                "Órdenes de Pago",
                on_click=lambda: ui.navigate.to("/payment-orders/print"),
            )
            ui.menu_item(
                "Lista de Cheques",
                on_click=lambda: ui.navigate.to("/checks/print"),
            )
