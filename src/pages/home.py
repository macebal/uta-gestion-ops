from typing import Callable
from datetime import date

from nicegui import ui
from sqlalchemy.orm import Session

from src.models import AppState


def home_page(session_factory: Callable[[], Session]):
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
                    .on("click", lambda: ui.navigate.to("/payment-orders/create"))
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

                # Print Payment Orders button - large card
                with (
                    ui.card()
                    .classes(
                        "flex-1 p-8 cursor-pointer hover:shadow-xl transition-shadow bg-gradient-to-br from-green-500 to-green-600"
                    )
                    .style("min-height: 280px")
                    .on("click", lambda: ui.navigate.to("/payment-orders/print"))
                ):
                    with ui.column().classes(
                        "items-center justify-center gap-4 w-full h-full"
                    ):
                        ui.icon("description", size="4rem").classes("text-white")
                        ui.label("Imprimir Órdenes de Pago").classes(
                            "text-2xl font-bold text-white text-center"
                        )
                        ui.label("Imprimir órdenes de pago individuales").classes(
                            "text-green-100 text-center"
                        )

                # Print Check List button - large card
                with (
                    ui.card()
                    .classes(
                        "flex-1 p-8 cursor-pointer hover:shadow-xl transition-shadow bg-gradient-to-br from-teal-500 to-teal-600"
                    )
                    .style("min-height: 280px")
                    .on("click", lambda: ui.navigate.to("/checks/print"))
                ):
                    with ui.column().classes(
                        "items-center justify-center gap-4 w-full h-full"
                    ):
                        ui.icon("list", size="4rem").classes("text-white")
                        ui.label("Imprimir Lista de Cheques").classes(
                            "text-2xl font-bold text-white text-center"
                        )
                        ui.label("Generar lista de cheques por cuenta y mes").classes(
                            "text-teal-100 text-center"
                        )

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
                    .on("click", lambda: ui.navigate.to("/suppliers/manage"))
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
                    .on("click", lambda: ui.navigate.to("/accounts/manage"))
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
                    .on("click", lambda: ui.navigate.to("/details/manage"))
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

        def check_and_show_reminder():
            """Check if reminder should be shown and return visibility state
            
            If the reminder has been dismissed for the current month, it will not be shown.
            If the reminder has not been dismissed for the current month, it will be shown.
            """
            session = session_factory()
            try:
                app_state = session.query(AppState).first()
                today = date.today()
                current_month_str = today.strftime("%Y-%m")

                if not app_state:
                    app_state = AppState(
                        last_opened_date=today, reminder_dismissed_month=None
                    )
                    session.add(app_state)
                    session.commit()
                    return True

                should_show = app_state.reminder_dismissed_month != current_month_str

                app_state.last_opened_date = today
                session.commit()

                return should_show
            finally:
                session.close()

        def dismiss_reminder_for_month():
            """Mark reminder as dismissed for current month and navigate to accounts"""
            session = session_factory()
            try:
                app_state = session.query(AppState).first()
                if app_state:
                    today = date.today()
                    app_state.reminder_dismissed_month = today.strftime("%Y-%m")
                    session.commit()
            finally:
                session.close()
            ui.navigate.to("/accounts/manage")

    show_reminder = check_and_show_reminder()

    reminder_container = ui.column().classes("fixed bottom-0 left-0 right-0 z-50 px-4 pb-4")
    reminder_container.visible = show_reminder
    
    with reminder_container:
        with ui.card().classes(
            "w-full max-w-6xl mx-auto p-6 bg-gradient-to-r from-amber-50 to-orange-50 border-l-4 border-orange-400 shadow-2xl"
        ):
            with ui.row().classes("items-center gap-4 w-full"):
                ui.icon("account_balance", size="2.5rem").classes("text-orange-600")
                with ui.column().classes("flex-1 gap-2"):
                    ui.label("Recordatorio Mensual").classes(
                        "text-lg font-semibold text-gray-800"
                    )
                    ui.label(
                        "Revise y actualice los números de cheque y orden de pago de las cuentas"
                    ).classes("text-gray-700")
                with ui.row().classes("gap-3"):
                    # clicking on the button will hide the reminder container and it will be 
                    # shown again next time the user opens the app if the reminder has not been dismissed for the current month
                    ui.button("Posponer", on_click=lambda: reminder_container.set_visibility(False)).props(
                        "outline color=orange-7"
                    ).classes("px-4")
                    ui.button("Ir a Cuentas", on_click=dismiss_reminder_for_month).props(
                        "color=orange"
                    ).classes("px-4")
