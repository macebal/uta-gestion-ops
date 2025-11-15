from nicegui import app, ui

from src.utils import get_app_version


def show_about_dialog():
    """Display about dialog with app information"""
    with ui.dialog() as dialog, ui.card().classes("p-6"):
        with ui.column().classes("gap-4 items-center"):
            ui.icon("info", size="3rem").classes("text-blue-600")

            ui.label("UTA - Gestión de Órdenes de Pago").classes("text-2xl font-bold text-gray-800")

            ui.separator().classes("w-full")

            with ui.column().classes("gap-2 w-full"):
                ui.label(f"Versión: {get_app_version()}").classes("text-gray-700")
                ui.label("Creado por Mariano Acebal").classes("text-gray-700")

                with ui.row().classes("gap-2 items-center"):
                    ui.icon("code", size="1.2rem").classes("text-gray-600")
                    ui.link(
                        "https://github.com/macebal/uta-gestion-ops",
                        "https://github.com/macebal/uta-gestion-ops",
                        new_tab=True,
                    ).classes("text-blue-600")

            ui.separator().classes("w-full")

            ui.button("Cerrar", on_click=dialog.close).props("color=primary")

    dialog.open()


def create_menu():
    """Create the top menu bar that is visible across all pages"""
    with ui.header().classes("bg-white shadow-sm"), ui.row().classes("w-full items-center gap-0"):
        # Home button
        ui.button(icon="home").props("flat color=grey-8").on("click", lambda: ui.navigate.to("/")).tooltip("Inicio")

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
                "Órdenes de Pago",
                on_click=lambda: ui.navigate.to("/payment-orders/manage"),
            )
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

        # Export menu
        with ui.button("Exportar a PDF", icon="picture_as_pdf").props("flat color=grey-8"), ui.menu():
            ui.menu_item(
                "Órdenes de Pago",
                on_click=lambda: ui.navigate.to("/payment-orders/export"),
            )
            ui.menu_item(
                "Lista de Cheques",
                on_click=lambda: ui.navigate.to("/checks/export"),
            )

        ui.space()

        ui.button(icon="info").props("flat color=grey-8").on("click", show_about_dialog).tooltip("Acerca de").mark(
            "about_button"
        )
