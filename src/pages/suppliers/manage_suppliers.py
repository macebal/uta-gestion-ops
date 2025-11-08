from collections.abc import Callable
from typing import Any

from nicegui import ui
from sqlalchemy.orm import Session

from src.components import primary_button, secondary_button, text_input
from src.models import Supplier


def manage_suppliers_page(session_factory: Callable[[], Session]):
    """Create the supplier management page with CRUD operations"""

    suppliers_data: list[dict[str, Any]] = []
    filtered_suppliers_data: list[dict[str, Any]] = []
    table = None
    edit_dialog = None
    delete_dialog = None
    selected_supplier = None
    search_input = None

    def load_suppliers():
        """Load all suppliers from database"""
        nonlocal suppliers_data, filtered_suppliers_data, table
        session = session_factory()
        try:
            suppliers = session.query(Supplier).order_by(Supplier.name).all()
            suppliers_data.clear()
            for supplier in suppliers:
                suppliers_data.append(
                    {
                        "id": supplier.id,
                        "name": supplier.name,
                        "cuit": supplier.cuit or "",
                        "phone": supplier.phone or "",
                        "email": supplier.email or "",
                        "actions": supplier.id,
                    }
                )
            filter_suppliers()
        finally:
            session.close()

    def filter_suppliers():
        """Filter suppliers based on search query"""
        nonlocal filtered_suppliers_data, table
        search_query = search_input.value.lower() if search_input and search_input.value else ""

        if search_query:
            filtered_suppliers_data.clear()
            for supplier in suppliers_data:
                if search_query in supplier["name"].lower():
                    filtered_suppliers_data.append(supplier)
        else:
            filtered_suppliers_data = suppliers_data.copy()

        if table:
            table.rows = filtered_suppliers_data
            table.update()

    def create_supplier(name: str, cuit: str, phone: str, email: str):
        """Create a new supplier"""
        if not name:
            ui.notify("Por favor ingrese el nombre del proveedor", type="negative")
            return

        session = session_factory()
        try:
            existing = session.query(Supplier).filter_by(name=name).first()
            if existing:
                ui.notify("Ya existe un proveedor con este nombre", type="negative")
                return

            new_supplier = Supplier(
                name=name,
                cuit=cuit if cuit else None,
                phone=phone if phone else None,
                email=email if email else None,
            )
            session.add(new_supplier)
            session.commit()

            ui.notify("Proveedor creado exitosamente", type="positive")
            load_suppliers()

            name_input.value = ""
            cuit_input.value = ""
            phone_input.value = ""
            email_input.value = ""
        except Exception as e:
            session.rollback()
            ui.notify(f"Error al crear proveedor: {str(e)}", type="negative")
        finally:
            session.close()

    def update_supplier(supplier_id: int, name: str, cuit: str, phone: str, email: str):
        """Update an existing supplier"""
        if not name:
            ui.notify("Por favor ingrese el nombre del proveedor", type="negative")
            return

        session = session_factory()
        try:
            existing = session.query(Supplier).filter(Supplier.name == name, Supplier.id != supplier_id).first()
            if existing:
                ui.notify("Ya existe otro proveedor con este nombre", type="negative")
                return

            supplier = session.query(Supplier).filter_by(id=supplier_id).first()
            if supplier:
                supplier.name = name
                supplier.cuit = cuit if cuit else None
                supplier.phone = phone if phone else None
                supplier.email = email if email else None
                session.commit()
                ui.notify("Proveedor actualizado exitosamente", type="positive")
                load_suppliers()
                edit_dialog.close()
            else:
                ui.notify("Proveedor no encontrado", type="negative")
        except Exception as e:
            session.rollback()
            ui.notify(f"Error al actualizar proveedor: {str(e)}", type="negative")
        finally:
            session.close()

    def delete_supplier(supplier_id: int):
        """Delete a supplier"""
        session = session_factory()
        try:
            supplier = session.query(Supplier).filter_by(id=supplier_id).first()
            if supplier:
                # Check if supplier has payment orders or invoices
                if supplier.payment_orders or supplier.invoices:
                    ui.notify(
                        "No se puede eliminar: el proveedor tiene órdenes de pago o facturas asociadas",
                        type="negative",
                    )
                    delete_dialog.close()
                    return

                # Delete the supplier
                session.delete(supplier)
                session.commit()
                ui.notify("Proveedor eliminado exitosamente", type="positive")
                load_suppliers()
                delete_dialog.close()
            else:
                ui.notify("Proveedor no encontrado", type="negative")
        except Exception as e:
            session.rollback()
            ui.notify(f"Error al eliminar proveedor: {str(e)}", type="negative")
        finally:
            session.close()

    def show_edit_dialog(supplier_id: int):
        """Show dialog to edit a supplier"""
        nonlocal edit_dialog, selected_supplier

        supplier_data = next((s for s in suppliers_data if s["id"] == supplier_id), None)
        if not supplier_data:
            ui.notify("Proveedor no encontrado", type="negative")
            return

        selected_supplier = supplier_data

        with ui.dialog() as dialog, ui.card().classes("p-6 min-w-96"):
            edit_dialog = dialog
            ui.label("Editar Proveedor").classes("text-xl font-semibold mb-4")

            edit_name_input = text_input("Nombre del Proveedor", value=supplier_data["name"])
            edit_cuit_input = text_input("CUIT", value=supplier_data["cuit"])
            edit_phone_input = text_input("Teléfono", value=supplier_data["phone"])
            edit_email_input = text_input("Email", value=supplier_data["email"])

            with ui.row().classes("w-full gap-4 mt-6 justify-end"):
                secondary_button(
                    "Cancelar",
                    on_click=lambda: dialog.close(),
                )
                primary_button(
                    "Guardar",
                    on_click=lambda: update_supplier(
                        supplier_id,
                        edit_name_input.value,
                        edit_cuit_input.value,
                        edit_phone_input.value,
                        edit_email_input.value,
                    ),
                )

        dialog.open()

    def show_delete_dialog(supplier_id: int):
        """Show confirmation dialog to delete a supplier"""
        nonlocal delete_dialog

        # Find the supplier in the data
        supplier_data = next((s for s in suppliers_data if s["id"] == supplier_id), None)
        if not supplier_data:
            ui.notify("Proveedor no encontrado", type="negative")
            return

        with ui.dialog() as dialog, ui.card().classes("p-6 min-w-96"):
            delete_dialog = dialog
            ui.label("Confirmar Eliminación").classes("text-xl font-semibold mb-4")
            ui.label(f"¿Está seguro que desea eliminar el proveedor '{supplier_data['name']}'?").classes("mb-4")

            with ui.row().classes("w-full gap-4 mt-6 justify-end"):
                secondary_button(
                    "Cancelar",
                    on_click=lambda: dialog.close(),
                )
                primary_button(
                    "Eliminar",
                    on_click=lambda: delete_supplier(supplier_id),
                    classes="bg-red-500 text-white px-6 py-2 rounded-lg text-base",
                )

        dialog.open()

    with ui.column().classes("w-full p-6"), ui.card().classes("w-full max-w-6xl mx-auto p-6 shadow-lg"):
        ui.label("Gestión de Proveedores").classes("text-2xl font-normal text-gray-700 mb-6")

        with ui.card().classes("w-full p-4 bg-gray-50 mb-6"):
            ui.label("Nuevo Proveedor").classes("text-lg font-semibold text-gray-700 mb-4")

            with ui.column().classes("w-full gap-4"):
                with ui.row().classes("w-full gap-4"):
                    with ui.column().classes("flex-1"):
                        name_input = text_input("Nombre del Proveedor")
                    with ui.column().classes("flex-1"):
                        cuit_input = text_input("CUIT")

                with ui.row().classes("w-full gap-4"):
                    with ui.column().classes("flex-1"):
                        phone_input = text_input("Teléfono")
                    with ui.column().classes("flex-1"):
                        email_input = text_input("Email")

                with ui.row().classes("w-full justify-end"):
                    primary_button(
                        "Agregar",
                        icon="add",
                        on_click=lambda: create_supplier(
                            name_input.value,
                            cuit_input.value,
                            phone_input.value,
                            email_input.value,
                        ),
                    )

        ui.label("Proveedores Existentes").classes("text-lg font-semibold text-gray-700 mb-4")

        with ui.row().classes("w-full mb-4"):
            search_input = (
                ui.input(
                    label="Buscar proveedor",
                    value="",
                    on_change=lambda e: filter_suppliers(),
                )
                .classes("w-full")
                .props("outlined prepend-icon=search clearable")
            )

        columns = [
            {
                "name": "name",
                "label": "Nombre del Proveedor",
                "field": "name",
                "align": "left",
                "sortable": True,
            },
            {
                "name": "cuit",
                "label": "CUIT",
                "field": "cuit",
                "align": "left",
                "sortable": True,
            },
            {
                "name": "phone",
                "label": "Teléfono",
                "field": "phone",
                "align": "left",
                "sortable": True,
            },
            {
                "name": "email",
                "label": "Email",
                "field": "email",
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
            rows=filtered_suppliers_data,
            row_key="id",
            pagination={
                "rowsPerPage": 10,
                "sortBy": "name",
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

    load_suppliers()
