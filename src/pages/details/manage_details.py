from collections.abc import Callable
from typing import Any

from nicegui import ui
from sqlalchemy.orm import Session

from src.components import filtered_table, primary_button, secondary_button, text_input
from src.models import Detail


def manage_details_page(session_factory: Callable[[], Session]):
    """Create the payment details management page with CRUD operations"""

    details_data: list[dict[str, Any]] = []
    table = None
    edit_dialog = None
    delete_dialog = None
    selected_detail = None

    def load_details():
        """Load all details from database"""
        nonlocal details_data, table
        session = session_factory()
        try:
            details = session.query(Detail).order_by(Detail.value).all()
            details_data.clear()
            for detail in details:
                details_data.append(
                    {
                        "id": detail.id,
                        "value": detail.value,
                        "actions": detail.id,
                    }
                )
            if table and hasattr(table, "refresh_data"):
                table.refresh_data()
        finally:
            session.close()

    def create_detail(value: str):
        """Create a new detail"""
        if not value:
            ui.notify("Por favor ingrese el detalle", type="negative")
            return

        session = session_factory()
        try:
            existing = session.query(Detail).filter_by(value=value).first()
            if existing:
                ui.notify("Ya existe un detalle con este texto", type="negative")
                return

            new_detail = Detail(value=value)
            session.add(new_detail)
            session.commit()

            ui.notify("Detalle creado exitosamente", type="positive")
            load_details()
            edit_dialog.close()
        except Exception as e:
            session.rollback()
            ui.notify(f"Error al crear detalle: {str(e)}", type="negative")
        finally:
            session.close()

    def update_detail(detail_id: int, value: str):
        """Update an existing detail"""
        if not value:
            ui.notify("Por favor ingrese el detalle", type="negative")
            return

        session = session_factory()
        try:
            existing = session.query(Detail).filter(Detail.value == value, Detail.id != detail_id).first()
            if existing:
                ui.notify("Ya existe otro detalle con este texto", type="negative")
                return

            detail = session.query(Detail).filter_by(id=detail_id).first()
            if detail:
                detail.value = value
                session.commit()
                ui.notify("Detalle actualizado exitosamente", type="positive")
                load_details()
                edit_dialog.close()
            else:
                ui.notify("Detalle no encontrado", type="negative")
        except Exception as e:
            session.rollback()
            ui.notify(f"Error al actualizar detalle: {str(e)}", type="negative")
        finally:
            session.close()

    def delete_detail(detail_id: int):
        """Delete a detail"""
        session = session_factory()
        try:
            detail = session.query(Detail).filter_by(id=detail_id).first()
            if detail:
                if detail.payment_orders:
                    ui.notify(
                        "No se puede eliminar: el detalle tiene órdenes de pago asociadas",
                        type="negative",
                    )
                    delete_dialog.close()
                    return

                session.delete(detail)
                session.commit()
                ui.notify("Detalle eliminado exitosamente", type="positive")
                load_details()
                delete_dialog.close()
            else:
                ui.notify("Detalle no encontrado", type="negative")
        except Exception as e:
            session.rollback()
            ui.notify(f"Error al eliminar detalle: {str(e)}", type="negative")
        finally:
            session.close()

    def show_detail_dialog(detail_id: int | None = None):
        """Show dialog to create or edit a detail"""
        nonlocal edit_dialog, selected_detail

        # Determine if we're in create or edit mode
        is_create_mode = detail_id is None
        detail_data = None

        if not is_create_mode:
            detail_data = next((d for d in details_data if d["id"] == detail_id), None)
            if not detail_data:
                ui.notify("Detalle no encontrado", type="negative")
                return
            selected_detail = detail_data

        with ui.dialog() as dialog, ui.card().classes("p-6 min-w-96"):
            edit_dialog = dialog

            # Set title and button text based on mode
            title = "Nuevo Detalle" if is_create_mode else "Editar Detalle"
            button_text = "Crear" if is_create_mode else "Guardar"

            ui.label(title).classes("text-xl font-semibold mb-4")

            initial_value = "" if is_create_mode else detail_data["value"]
            value_input = text_input("Detalle", value=initial_value)

            with ui.row().classes("w-full gap-4 mt-6 justify-end"):
                secondary_button(
                    "Cancelar",
                    on_click=lambda: dialog.close(),
                )

                if is_create_mode:
                    primary_button(
                        button_text,
                        on_click=lambda: create_detail(value_input.value),
                    )
                else:
                    primary_button(
                        button_text,
                        on_click=lambda: update_detail(detail_id, value_input.value),
                    )

        dialog.open()

    def show_delete_dialog(detail_id: int):
        """Show confirmation dialog to delete a detail"""
        nonlocal delete_dialog

        detail_data = next((d for d in details_data if d["id"] == detail_id), None)
        if not detail_data:
            ui.notify("Detalle no encontrado", type="negative")
            return

        with ui.dialog() as dialog, ui.card().classes("p-6 min-w-96"):
            delete_dialog = dialog
            ui.label("Confirmar Eliminación").classes("text-xl font-semibold mb-4")
            ui.label(f"¿Está seguro que desea eliminar el detalle '{detail_data['value']}'?").classes("mb-4")

            with ui.row().classes("w-full gap-4 mt-6 justify-end"):
                secondary_button(
                    "Cancelar",
                    on_click=lambda: dialog.close(),
                )
                primary_button(
                    "Eliminar",
                    on_click=lambda: delete_detail(detail_id),
                    classes="bg-red-500 text-white px-6 py-2 rounded-lg text-base",
                )

        dialog.open()

    with ui.column().classes("w-full p-6"), ui.card().classes("w-full max-w-6xl mx-auto p-6 shadow-lg"):
        with ui.row().classes("w-full justify-between items-center mb-4"):
            ui.label("Gestión de Detalles de Pago").classes("text-2xl font-normal text-gray-700")
            primary_button(
                "Crear Detalle",
                icon="add_circle",
                on_click=lambda: show_detail_dialog(),
            ).props("color=green")

        ui.separator().classes("mb-6")

        columns = [
            {
                "name": "value",
                "label": "Detalle de Pago",
                "field": "value",
                "align": "left",
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
            rows=details_data,
            row_key="id",
            pagination={
                "rowsPerPage": 10,
                "sortBy": "value",
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

        table.on("edit_row", lambda e: show_detail_dialog(e.args["id"]))
        table.on("delete_row", lambda e: show_delete_dialog(e.args["id"]))

    load_details()
