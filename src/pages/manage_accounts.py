from typing import Callable, Dict, Any

from nicegui import ui
from sqlalchemy.orm import Session

from src.components import primary_button, secondary_button, text_input
from src.models import Account, AccountSequence


def manage_accounts_page(session_factory: Callable[[], Session]):
    """Create the account management page with CRUD operations"""

    # State variables
    accounts_data: list[Dict[str, Any]] = []
    table = None
    edit_dialog = None
    delete_dialog = None
    selected_account = None

    def load_accounts():
        """Load all accounts from database"""
        nonlocal accounts_data, table
        session = session_factory()
        try:
            accounts = session.query(Account).all()
            accounts_data.clear()
            for account in accounts:
                accounts_data.append(
                    {
                        "id": account.id,
                        "name": account.name,
                        "number": account.number,
                        "actions": account.id,
                    }
                )
            if table:
                table.rows = accounts_data
                table.update()
        finally:
            session.close()

    def create_account(name: str, number: str):
        """Create a new account"""
        if not name or not number:
            ui.notify("Por favor complete todos los campos", type="negative")
            return

        session = session_factory()
        try:
            # Check if account with same number already exists
            existing = session.query(Account).filter_by(number=number).first()
            if existing:
                ui.notify("Ya existe una cuenta con este número", type="negative")
                return

            new_account = Account(name=name, number=number)
            session.add(new_account)
            session.flush()

            # Create account sequence for the new account
            account_seq = AccountSequence(
                account_id=new_account.id,
                last_order_number=0,
                last_check_number=0,
            )
            session.add(account_seq)
            session.commit()

            ui.notify("Cuenta creada exitosamente", type="positive")
            load_accounts()

            # Clear input fields
            name_input.value = ""
            number_input.value = ""
        except Exception as e:
            session.rollback()
            ui.notify(f"Error al crear cuenta: {str(e)}", type="negative")
        finally:
            session.close()

    def update_account(account_id: int, name: str, number: str):
        """Update an existing account"""
        if not name or not number:
            ui.notify("Por favor complete todos los campos", type="negative")
            return

        session = session_factory()
        try:
            # Check if another account has the same number
            existing = (
                session.query(Account)
                .filter(Account.number == number, Account.id != account_id)
                .first()
            )
            if existing:
                ui.notify("Ya existe otra cuenta con este número", type="negative")
                return

            account = session.query(Account).filter_by(id=account_id).first()
            if account:
                account.name = name
                account.number = number
                session.commit()
                ui.notify("Cuenta actualizada exitosamente", type="positive")
                load_accounts()
                edit_dialog.close()
            else:
                ui.notify("Cuenta no encontrada", type="negative")
        except Exception as e:
            session.rollback()
            ui.notify(f"Error al actualizar cuenta: {str(e)}", type="negative")
        finally:
            session.close()

    def delete_account(account_id: int):
        """Delete an account"""
        session = session_factory()
        try:
            account = session.query(Account).filter_by(id=account_id).first()
            if account:
                # Check if account has payment orders
                if account.payment_orders:
                    ui.notify(
                        "No se puede eliminar: la cuenta tiene órdenes de pago asociadas",
                        type="negative",
                    )
                    delete_dialog.close()
                    return

                # Delete the account
                session.delete(account)
                session.commit()
                ui.notify("Cuenta eliminada exitosamente", type="positive")
                load_accounts()
                delete_dialog.close()
            else:
                ui.notify("Cuenta no encontrada", type="negative")
        except Exception as e:
            session.rollback()
            ui.notify(f"Error al eliminar cuenta: {str(e)}", type="negative")
        finally:
            session.close()

    def show_edit_dialog(account_id: int):
        """Show dialog to edit an account"""
        nonlocal edit_dialog, selected_account

        # Find the account in the data
        account_data = next((a for a in accounts_data if a["id"] == account_id), None)
        if not account_data:
            ui.notify("Cuenta no encontrada", type="negative")
            return

        selected_account = account_data

        with ui.dialog() as dialog, ui.card().classes("p-6 min-w-96"):
            edit_dialog = dialog
            ui.label("Editar Cuenta").classes("text-xl font-semibold mb-4")

            edit_name_input = text_input(
                "Nombre de la Cuenta", value=account_data["name"]
            )
            edit_number_input = text_input(
                "Número de Cuenta", value=account_data["number"]
            )

            with ui.row().classes("w-full gap-4 mt-6 justify-end"):
                secondary_button(
                    "Cancelar",
                    on_click=lambda: dialog.close(),
                )
                primary_button(
                    "Guardar",
                    on_click=lambda: update_account(
                        account_id, edit_name_input.value, edit_number_input.value
                    ),
                )

        dialog.open()

    def show_delete_dialog(account_id: int):
        """Show confirmation dialog to delete an account"""
        nonlocal delete_dialog

        # Find the account in the data
        account_data = next((a for a in accounts_data if a["id"] == account_id), None)
        if not account_data:
            ui.notify("Cuenta no encontrada", type="negative")
            return

        with ui.dialog() as dialog, ui.card().classes("p-6 min-w-96"):
            delete_dialog = dialog
            ui.label("Confirmar Eliminación").classes("text-xl font-semibold mb-4")
            ui.label(
                f"¿Está seguro que desea eliminar la cuenta '{account_data['name']}'?"
            ).classes("mb-4")

            with ui.row().classes("w-full gap-4 mt-6 justify-end"):
                secondary_button(
                    "Cancelar",
                    on_click=lambda: dialog.close(),
                )
                primary_button(
                    "Eliminar",
                    on_click=lambda: delete_account(account_id),
                    classes="bg-red-500 text-white px-6 py-2 rounded-lg text-base",
                )

        dialog.open()

    # Load initial data FIRST
    load_accounts()

    # Main page layout
    with ui.column().classes("w-full p-6"):
        with ui.card().classes("w-full max-w-6xl mx-auto p-6 shadow-lg"):
            ui.label("Gestión de Cuentas Bancarias").classes(
                "text-2xl font-normal text-gray-700 mb-6"
            )

            # Create new account section
            with ui.card().classes("w-full p-4 bg-gray-50 mb-6"):
                ui.label("Nueva Cuenta").classes(
                    "text-lg font-semibold text-gray-700 mb-4"
                )

                with ui.row().classes("w-full gap-4 items-end"):
                    with ui.column().classes("flex-1"):
                        name_input = text_input("Nombre de la Cuenta")

                    with ui.column().classes("flex-1"):
                        number_input = text_input("Número de Cuenta")

                    primary_button(
                        "Agregar",
                        icon="add",
                        on_click=lambda: create_account(
                            name_input.value, number_input.value
                        ),
                    )

            # Accounts table
            ui.label("Cuentas Existentes").classes(
                "text-lg font-semibold text-gray-700 mb-4"
            )

            columns = [
                {
                    "name": "name",
                    "label": "Nombre de la Cuenta",
                    "field": "name",
                    "align": "left",
                    "sortable": True,
                },
                {
                    "name": "number",
                    "label": "Número de Cuenta",
                    "field": "number",
                    "align": "left",
                    "sortable": True,
                },
                {
                    "name": "actions",
                    "label": "Acciones",
                    "field": "actions",
                    "align": "center",
                },
            ]

            table = ui.table(
                columns=columns,
                rows=accounts_data,
                row_key="id",
            ).classes("w-full")

            # Custom slot for action buttons
            table.add_slot(
                "body-cell-actions",
                r"""
                <q-td :props="props">
                    <q-btn
                        flat
                        round
                        dense
                        icon="edit"
                        color="blue"
                        @click="$parent.$emit('edit', props.row)"
                    />
                    <q-btn
                        flat
                        round
                        dense
                        icon="delete"
                        color="red"
                        @click="$parent.$emit('delete', props.row)"
                    />
                </q-td>
                """,
            )

            # Event handlers for table actions
            table.on("edit", lambda e: show_edit_dialog(e.args["id"]))
            table.on("delete", lambda e: show_delete_dialog(e.args["id"]))
