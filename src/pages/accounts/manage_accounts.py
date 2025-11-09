from collections.abc import Callable
from typing import Any

from nicegui import ui
from sqlalchemy.orm import Session

from src.components import filtered_table, primary_button, secondary_button, text_input
from src.models import Account, AccountSequence


def manage_accounts_page(session_factory: Callable[[], Session]):
    """Create the account management page with CRUD operations"""

    accounts_data: list[dict[str, Any]] = []
    table = None
    edit_dialog = None
    delete_dialog = None
    selected_account = None

    def load_accounts():
        """Load all accounts from database"""
        nonlocal accounts_data, table
        session = session_factory()
        try:
            accounts = session.query(Account).order_by(Account.name).all()
            accounts_data.clear()
            for account in accounts:
                # Get the sequence data for this account
                last_order = 0
                last_check = 0
                if account.account_sequence:
                    last_order = account.account_sequence.last_order_number
                    last_check = account.account_sequence.last_check_number

                accounts_data.append(
                    {
                        "id": account.id,
                        "name": account.name,
                        "number": account.number,
                        "last_order_number": last_order,
                        "last_check_number": last_check,
                        "actions": account.id,
                    }
                )
            if table and hasattr(table, "refresh_data"):
                table.refresh_data()
        finally:
            session.close()

    def create_account(name: str, number: str, last_order_number: int, last_check_number: int):
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
                last_order_number=last_order_number,
                last_check_number=last_check_number,
            )
            session.add(account_seq)
            session.commit()

            ui.notify("Cuenta creada exitosamente", type="positive")
            load_accounts()
            edit_dialog.close()
        except Exception as e:
            session.rollback()
            ui.notify(f"Error al crear cuenta: {str(e)}", type="negative")
        finally:
            session.close()

    def update_account(
        account_id: int,
        name: str,
        number: str,
        last_order_number: int,
        last_check_number: int,
    ):
        """Update an existing account"""
        if not name or not number:
            ui.notify("Por favor complete todos los campos", type="negative")
            return

        session = session_factory()
        try:
            # Check if another account has the same number
            existing = session.query(Account).filter(Account.number == number, Account.id != account_id).first()
            if existing:
                ui.notify("Ya existe otra cuenta con este número", type="negative")
                return

            account = session.query(Account).filter_by(id=account_id).first()
            if account:
                account.name = name
                account.number = number

                # Update sequence numbers
                if account.account_sequence:
                    account.account_sequence.last_order_number = last_order_number
                    account.account_sequence.last_check_number = last_check_number
                else:
                    # Create sequence if it doesn't exist
                    account_seq = AccountSequence(
                        account_id=account.id,
                        last_order_number=last_order_number,
                        last_check_number=last_check_number,
                    )
                    session.add(account_seq)

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

    def show_account_dialog(account_id: int | None = None):
        """Show dialog to create or edit an account"""
        nonlocal edit_dialog, selected_account

        is_create_mode = account_id is None
        account_data = None

        if not is_create_mode:
            account_data = next((a for a in accounts_data if a["id"] == account_id), None)
            if not account_data:
                ui.notify("Cuenta no encontrada", type="negative")
                return
            selected_account = account_data

        with ui.dialog() as dialog, ui.card().classes("p-6 min-w-96"):
            edit_dialog = dialog

            title = "Nueva Cuenta" if is_create_mode else "Editar Cuenta"
            button_text = "Crear" if is_create_mode else "Guardar"

            ui.label(title).classes("text-xl font-semibold mb-4")

            name_value = "" if is_create_mode else account_data["name"]
            number_value = "" if is_create_mode else account_data["number"]
            order_number_value = 0 if is_create_mode else account_data["last_order_number"]
            check_number_value = 0 if is_create_mode else account_data["last_check_number"]

            name_input = text_input("Nombre de la Cuenta", value=name_value)
            number_input = text_input("Número de Cuenta", value=number_value)

            with ui.row().classes("w-full gap-4"):
                with ui.column().classes("flex-1"):
                    order_number_input = (
                        ui.number(
                            label="Último Número de OP",
                            value=order_number_value,
                            min=0,
                            step=1,
                        )
                        .props("outlined")
                        .classes("w-full")
                    )

                with ui.column().classes("flex-1"):
                    check_number_input = (
                        ui.number(
                            label="Último Número de Cheque",
                            value=check_number_value,
                            min=0,
                            step=1,
                        )
                        .props("outlined")
                        .classes("w-full")
                    )

            with ui.row().classes("w-full gap-4 mt-6 justify-end"):
                secondary_button(
                    "Cancelar",
                    on_click=lambda: dialog.close(),
                )

                if is_create_mode:
                    primary_button(
                        button_text,
                        on_click=lambda: create_account(
                            name_input.value,
                            number_input.value,
                            int(order_number_input.value or 0),
                            int(check_number_input.value or 0),
                        ),
                    )
                else:
                    primary_button(
                        button_text,
                        on_click=lambda: update_account(
                            account_id,
                            name_input.value,
                            number_input.value,
                            int(order_number_input.value or 0),
                            int(check_number_input.value or 0),
                        ),
                    )

        dialog.open()

    def show_delete_dialog(account_id: int):
        """Show confirmation dialog to delete an account"""
        nonlocal delete_dialog

        account_data = next((a for a in accounts_data if a["id"] == account_id), None)
        if not account_data:
            ui.notify("Cuenta no encontrada", type="negative")
            return

        with ui.dialog() as dialog, ui.card().classes("p-6 min-w-96"):
            delete_dialog = dialog
            ui.label("Confirmar Eliminación").classes("text-xl font-semibold mb-4")
            ui.label(f"¿Está seguro que desea eliminar la cuenta '{account_data['name']}'?").classes("mb-4")

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

    with ui.column().classes("w-full p-6"), ui.card().classes("w-full max-w-6xl mx-auto p-6 shadow-lg"):
        with ui.row().classes("w-full justify-between items-center mb-4"):
            ui.label("Gestión de Cuentas Bancarias").classes("text-2xl font-normal text-gray-700")
            primary_button(
                "Crear Cuenta",
                icon="add_circle",
                on_click=lambda: show_account_dialog(),
            ).props("color=green")

        ui.separator().classes("mb-6")

        columns = [
            {
                "name": "name",
                "label": "Nombre de la Cuenta",
                "field": "name",
                "align": "left",
                "sortable": True,
                "type": "string",
            },
            {
                "name": "number",
                "label": "Número de Cuenta",
                "field": "number",
                "align": "left",
                "sortable": True,
                "type": "string",
            },
            {
                "name": "last_order_number",
                "label": "Último N° OP",
                "field": "last_order_number",
                "align": "center",
                "sortable": True,
                "type": "number",
            },
            {
                "name": "last_check_number",
                "label": "Último N° Cheque",
                "field": "last_check_number",
                "align": "center",
                "sortable": True,
                "type": "number",
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
            rows=accounts_data,
            row_key="id",
            pagination={
                "rowsPerPage": 10,
                "sortBy": "name",
                "descending": False,
            },
        )

        table.props(':rows-per-page-options="[10, 20, 50, 0]"')

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
                    <q-btn
                        flat
                        round
                        dense
                        icon="delete"
                        color="red"
                        @click="() => $parent.$emit('delete_row', props.row)"
                    >
                        <q-tooltip>Eliminar</q-tooltip>
                    </q-btn>
                </q-td>
                """,
        )

        table.on("edit_row", lambda e: show_account_dialog(e.args["id"]))
        table.on("delete_row", lambda e: show_delete_dialog(e.args["id"]))

    load_accounts()
