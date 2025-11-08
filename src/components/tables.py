from datetime import datetime
from decimal import Decimal
from typing import Literal, NotRequired, TypedDict

from nicegui import ui


class ColumnConfig(TypedDict):
    """Configuration for a table column"""

    name: str
    label: str
    field: str
    align: Literal["left", "center", "right"]
    sortable: NotRequired[bool]
    type: Literal["string", "number", "date"]


class FilterConfig(TypedDict):
    """Configuration for a table filter"""

    column: str
    operation: str
    value: str
    value2: NotRequired[str]


def scrollable_table(
    columns: list,
    rows: list,
    height: str = "200px",
    footer_row_html: str | None = None,
    custom_slots: dict | None = None,
    **kwargs,
):
    """
    Standardized scrollable table with sticky header and optional sticky footer

    Args:
        columns: List of column definitions (dicts with name, label, field, align)
        rows: List of row data (list of dicts)
        height: Table height (default: 200px)
        footer_row_html: Optional HTML for footer row (will be sticky at bottom)
        custom_slots: Optional dict of slot_name -> html for custom slots
        **kwargs: Additional arguments passed to ui.table

    Returns:
        The ui.table element
    """
    classes = kwargs.pop("classes", "w-full max-w-2xl")

    table = (
        ui.table(columns=columns, rows=rows)
        .classes(classes)
        .props("virtual-scroll sticky-header")
        .style(f"height: {height}")
    )

    # Add custom slots if provided
    if custom_slots:
        for slot_name, slot_html in custom_slots.items():
            table.add_slot(slot_name, slot_html)

    # Add footer row if provided
    if footer_row_html:
        table.add_slot("bottom-row", footer_row_html)

    return table


def create_invoice_table(rows: list, total: str, on_add_click=None, on_delete_click=None):
    """
    Specialized table for invoices with total and add button in footer

    Args:
        rows: List of invoice rows (dicts with factura, importe)
        total: Total amount string (e.g., "$22,000.00")
        on_add_click: Callback for add button
        on_delete_click: Callback for delete action (receives row data)

    Returns:
        The configured table element
    """
    columns = [
        {
            "name": "factura",
            "label": "Factura",
            "field": "factura",
            "align": "left",
        },
        {
            "name": "importe",
            "label": "Importe",
            "field": "importe",
            "align": "right",
        },
        {
            "name": "acciones",
            "label": "Acciones",
            "field": "acciones",
            "align": "center",
        },
    ]

    # Action cell slot with delete icon
    action_slot_html = """
        <q-td :props="props">
            <q-icon name="close" class="text-red-500 cursor-pointer" size="sm" />
        </q-td>
    """

    # Footer row with total and add button
    footer_html = f"""
        <q-tr style="position: sticky; bottom: 0; background-color: white; z-index: 1;">
            <q-td style="background-color: white;"></q-td>
            <q-td class="text-right" style="background-color: white;">
                <div class="text-lg font-semibold text-gray-800">{total}</div>
            </q-td>
            <q-td class="text-center" style="background-color: white;">
                <q-btn label="AGREGAR" class="bg-blue-500 text-white" unelevated />
            </q-td>
        </q-tr>
    """

    custom_slots = {
        "body-cell-acciones": action_slot_html,
    }

    return scrollable_table(
        columns=columns,
        rows=rows,
        height="200px",
        footer_row_html=footer_html,
        custom_slots=custom_slots,
    )


def simple_table(columns: list, rows: list, **kwargs):
    """
    Simple table without scrolling or special features

    Args:
        columns: List of column definitions
        rows: List of row data
        **kwargs: Additional arguments passed to ui.table

    Returns:
        The ui.table element
    """
    classes = kwargs.pop("classes", "w-full")
    return ui.table(columns=columns, rows=rows).classes(classes)


def filtered_table(
    columns: list[ColumnConfig],
    rows: list[dict],
    row_key: str = "id",
    pagination: dict | None = None,
    custom_slots: dict | None = None,
    **kwargs,
) -> ui.table:
    """
    Table with built-in filtering capabilities

    Args:
        columns: List of column configurations with type information
        rows: List of row data (will be filtered internally)
        row_key: Key field for row identification (default: "id")
        pagination: Pagination configuration dict
        custom_slots: Dict of slot_name -> html for custom slots
        **kwargs: Additional arguments passed to ui.table

    Returns:
        The ui.table element with filtering UI
    """
    from .buttons import primary_button, secondary_button
    from .inputs import text_input

    active_filters: list[FilterConfig] = []
    filtered_rows: list[dict] = rows.copy()
    table_element = None
    filters_container = None
    add_filter_dialog = None

    # Operation labels for different types
    STRING_OPERATIONS = {
        "contains": "Contiene",
        "startswith": "Comienza con",
        "endswith": "Termina con",
    }

    NUMBER_OPERATIONS = {
        "equals": "Igual a",
        "greater": "Mayor que",
        "less": "Menor que",
        "greater_equal": "Mayor o igual que",
        "less_equal": "Menor o igual que",
    }

    DATE_OPERATIONS = {
        "equals": "Igual a",
        "before": "Antes de",
        "after": "Después de",
        "between": "Entre",
    }

    def get_operations_for_type(column_type: str) -> dict[str, str]:
        """Get available operations for a column type"""

        match column_type:
            case "string":
                return STRING_OPERATIONS
            case "number":
                return NUMBER_OPERATIONS
            case "date":
                return DATE_OPERATIONS
            case _:
                return {}

    def get_filter_label(filter_config: FilterConfig) -> str:
        """Generate a readable label for a filter"""
        column = next((col for col in columns if col["name"] == filter_config["column"]), None)
        if not column:
            return ""

        column_label = column["label"]
        operation = filter_config["operation"]
        value = filter_config["value"]

        operations = get_operations_for_type(column["type"])
        operation_label = operations.get(operation, operation)

        if operation == "between":
            value2 = filter_config.get("value2", "")
            return f"{column_label}: {operation_label} {value} y {value2}"
        else:
            return f"{column_label}: {operation_label} '{value}'"

    def apply_filter(row: dict, filter_config: FilterConfig) -> bool:
        """Check if a row matches a filter"""
        column = next((col for col in columns if col["name"] == filter_config["column"]), None)
        if not column:
            return True

        field_value = row.get(column["field"])
        if field_value is None:
            return False

        column_type = column["type"]
        operation = filter_config["operation"]
        filter_value = filter_config["value"]

        try:
            if column_type == "string":
                field_str = str(field_value).lower()
                filter_str = filter_value.lower()

                if operation == "contains":
                    return filter_str in field_str
                elif operation == "startswith":
                    return field_str.startswith(filter_str)
                elif operation == "endswith":
                    return field_str.endswith(filter_str)

            elif column_type == "number":
                field_num = Decimal(str(field_value).replace("$", "").replace(",", ""))
                filter_num = Decimal(filter_value)

                match operation:
                    case "equals":
                        return field_num == filter_num
                    case "greater":
                        return field_num > filter_num
                    case "less":
                        return field_num < filter_num
                    case "greater_equal":
                        return field_num >= filter_num
                    case "less_equal":
                        return field_num <= filter_num

            elif column_type == "date":
                if isinstance(field_value, str):
                    field_date = datetime.strptime(field_value, "%d/%m/%Y").date()
                else:
                    field_date = field_value

                filter_date = datetime.strptime(filter_value, "%d/%m/%Y").date()

                if operation == "equals":
                    return field_date == filter_date
                elif operation == "before":
                    return field_date < filter_date
                elif operation == "after":
                    return field_date > filter_date
                elif operation == "between":
                    filter_date2 = datetime.strptime(filter_config.get("value2", ""), "%d/%m/%Y").date()
                    return filter_date <= field_date <= filter_date2

        except (ValueError, TypeError, Exception):
            return False

        return True

    def apply_all_filters():
        """Apply all active filters to the rows"""
        nonlocal filtered_rows, table_element

        if not active_filters:
            filtered_rows = rows.copy()
        else:
            filtered_rows = [row for row in rows if all(apply_filter(row, f) for f in active_filters)]

        if table_element:
            table_element.rows = filtered_rows
            table_element.update()

    def refresh_data():
        """Refresh table data and reapply filters"""
        apply_all_filters()

    def render_filters():
        """Render active filters as chips"""
        nonlocal filters_container

        if filters_container:
            filters_container.clear()
            with filters_container:
                if not active_filters:
                    ui.label("No hay filtros activos").classes("text-gray-500 text-sm")
                else:
                    with ui.row().classes("gap-2 flex-wrap"):
                        for filter_item in active_filters:
                            label = get_filter_label(filter_item)
                            with ui.chip(label, removable=True).classes("bg-blue-100") as chip:
                                chip.on("remove", lambda f=filter_item: remove_filter(f))

    def add_filter(column_name: str, operation: str, value: str, value2: str = ""):
        """Add a new filter"""
        nonlocal add_filter_dialog

        if not value:
            ui.notify("Por favor ingrese un valor", type="negative")
            return

        column = next((col for col in columns if col["name"] == column_name), None)
        if not column:
            ui.notify("Columna no encontrada", type="negative")
            return

        if operation == "between" and not value2:
            ui.notify("Por favor ingrese el segundo valor", type="negative")
            return

        filter_config: FilterConfig = {
            "column": column_name,
            "operation": operation,
            "value": value,
        }

        if operation == "between":
            filter_config["value2"] = value2

        active_filters.append(filter_config)

        render_filters()
        apply_all_filters()

        if add_filter_dialog:
            add_filter_dialog.close()

        ui.notify("Filtro agregado", type="positive")

    def remove_filter(filter_config: FilterConfig):
        """Remove a filter"""
        active_filters.remove(filter_config)
        render_filters()
        apply_all_filters()
        ui.notify("Filtro eliminado", type="positive")

    def show_add_filter_dialog():
        """Show dialog to add a new filter"""
        nonlocal add_filter_dialog

        with ui.dialog() as dialog, ui.card().classes("p-6 min-w-96"):
            add_filter_dialog = dialog
            ui.label("Agregar Filtro").classes("text-xl font-semibold mb-4")

            column_options = {col["name"]: col["label"] for col in columns if col.get("type")}
            column_select = ui.select(
                options=column_options,
                label="Columna",
                value=list(column_options.keys())[0] if column_options else None,
            ).classes("w-full mb-4")

            operation_select = ui.select(options={}, label="Operación").classes("w-full mb-4")

            value_input = text_input("Valor")
            value2_input = text_input("Valor 2")
            value2_input.visible = False

            def update_operations():
                """Update operations based on selected column"""
                column = next((col for col in columns if col["name"] == column_select.value), None)
                if column:
                    operations = get_operations_for_type(column["type"])
                    operation_select.options = operations
                    operation_select.value = list(operations.keys())[0] if operations else None
                    operation_select.update()

            def update_value2_visibility():
                """Show/hide second value input for between operation"""
                value2_input.visible = operation_select.value == "between"

            column_select.on("update:model-value", lambda: update_operations())
            operation_select.on("update:model-value", lambda: update_value2_visibility())

            update_operations()

            with ui.row().classes("w-full gap-4 mt-6 justify-end"):
                secondary_button(
                    "Cancelar",
                    on_click=lambda: dialog.close(),
                )
                primary_button(
                    "Agregar",
                    on_click=lambda: add_filter(
                        column_select.value, operation_select.value, value_input.value, value2_input.value
                    ),
                )

        dialog.open()

    with ui.column().classes("w-full"):
        with ui.row().classes("w-full items-center justify-between mb-4"):
            ui.label("Filtros").classes("text-lg font-semibold text-gray-700")
            primary_button("Agregar Filtro", icon="add", on_click=show_add_filter_dialog)

        filters_container = ui.column().classes("w-full min-h-8 py-2 mb-4")
        render_filters()

        classes = kwargs.pop("classes", "w-full")

        table_element = ui.table(
            columns=columns,
            rows=filtered_rows,
            row_key=row_key,
            pagination=pagination or {"rowsPerPage": 10},
        ).classes(classes)

        if custom_slots:
            for slot_name, slot_html in custom_slots.items():
                table_element.add_slot(slot_name, slot_html)

    # Attach refresh method to table for external data updates
    table_element.refresh_data = refresh_data  # type: ignore

    return table_element
