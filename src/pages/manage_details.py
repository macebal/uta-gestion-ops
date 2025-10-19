from typing import Callable, Dict, Any

from nicegui import ui
from sqlalchemy.orm import Session

from src.components import primary_button, secondary_button, text_input
from src.models import Detail


def manage_details_page(session_factory: Callable[[], Session]):
    """Create the payment details management page with CRUD operations"""

    details_data: list[Dict[str, Any]] = []
    filtered_details_data: list[Dict[str, Any]] = []
    table = None
    edit_dialog = None
    delete_dialog = None
    selected_detail = None
    search_input = None

    def load_details():
        """Load all details from database"""
        nonlocal details_data, filtered_details_data, table
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
            filter_details()
        finally:
            session.close()

    def filter_details():
        """Filter details based on search query"""
        nonlocal filtered_details_data, table
        search_query = (
            search_input.value.lower() if search_input and search_input.value else ""
        )

        if search_query:
            filtered_details_data.clear()
            for detail in details_data:
                if search_query in detail["value"].lower():
                    filtered_details_data.append(detail)
        else:
            filtered_details_data = details_data.copy()

        if table:
            table.rows = filtered_details_data
            table.update()

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
            value_input.value = ""
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
            existing = (
                session.query(Detail)
                .filter(Detail.value == value, Detail.id != detail_id)
                .first()
            )
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

    def show_edit_dialog(detail_id: int):
        """Show dialog to edit a detail"""
        nonlocal edit_dialog, selected_detail

        detail_data = next((d for d in details_data if d["id"] == detail_id), None)
        if not detail_data:
            ui.notify("Detalle no encontrado", type="negative")
            return

        selected_detail = detail_data

        with ui.dialog() as dialog, ui.card().classes("p-6 min-w-96"):
            edit_dialog = dialog
            ui.label("Editar Detalle").classes("text-xl font-semibold mb-4")

            edit_value_input = text_input("Detalle", value=detail_data["value"])

            with ui.row().classes("w-full gap-4 mt-6 justify-end"):
                secondary_button(
                    "Cancelar",
                    on_click=lambda: dialog.close(),
                )
                primary_button(
                    "Guardar",
                    on_click=lambda: update_detail(detail_id, edit_value_input.value),
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
            ui.label(
                f"¿Está seguro que desea eliminar el detalle '{detail_data['value']}'?"
            ).classes("mb-4")

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

    with ui.column().classes("w-full p-6"):
        with ui.card().classes("w-full max-w-6xl mx-auto p-6 shadow-lg"):
            ui.label("Gestión de Detalles de Pago").classes(
                "text-2xl font-normal text-gray-700 mb-6"
            )

            with ui.card().classes("w-full p-4 bg-gray-50 mb-6"):
                ui.label("Nuevo Detalle").classes(
                    "text-lg font-semibold text-gray-700 mb-4"
                )

                with ui.row().classes("w-full gap-4 items-end"):
                    with ui.column().classes("flex-1"):
                        value_input = text_input("Detalle de Pago")

                    primary_button(
                        "Agregar",
                        icon="add",
                        on_click=lambda: create_detail(value_input.value),
                    )

            ui.label("Detalles Existentes").classes(
                "text-lg font-semibold text-gray-700 mb-4"
            )

            with ui.row().classes("w-full mb-4"):
                search_input = (
                    ui.input(
                        label="Buscar detalle",
                        value="",
                        on_change=lambda e: filter_details(),
                    )
                    .classes("w-full")
                    .props("outlined prepend-icon=search clearable")
                )

            columns = [
                {
                    "name": "value",
                    "label": "Detalle de Pago",
                    "field": "value",
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
                rows=filtered_details_data,
                row_key="id",
                pagination={
                    "rowsPerPage": 10,
                    "sortBy": "value",
                    "descending": False,
                },
            ).classes("w-full")

            table.props(
                """
                :rows-per-page-options="[10, 20, 50, 0]"
                :rows-per-page-label="'Filas por página:'"
                :pagination-label="(first, last, total) => `${first}-${last} de ${total}`"
            """
            )

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

            table.on("edit_row", lambda e: show_edit_dialog(e.args["id"]))
            table.on("delete_row", lambda e: show_delete_dialog(e.args["id"]))

    load_details()
