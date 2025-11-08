from nicegui import ui


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
