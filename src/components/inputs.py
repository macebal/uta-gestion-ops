from collections.abc import Callable

from nicegui import ui


def text_input(label: str, value: str = "", on_change: Callable | None = None, readonly: bool = False, **kwargs):
    """
    Standardized text input field with outlined style

    Args:
        label: Label for the input field
        value: Default value for the input
        on_change: Callback function when value changes
        readonly: Whether the input is read-only
        **kwargs: Additional arguments passed to ui.input (e.g., classes)
    """
    classes = kwargs.pop("classes", "w-full")
    props_str = "outlined"
    if readonly:
        props_str += " readonly"
    input_field = ui.input(label=label, value=value, on_change=on_change).classes(classes).props(props_str)
    return input_field


def select_field(options: list, label: str, value=None, **kwargs):
    """
    Standardized select/dropdown field with outlined style

    Args:
        options: List of options for the dropdown
        label: Label for the select field
        value: Default selected value
        **kwargs: Additional arguments passed to ui.select (e.g., classes, on_change)
    """
    classes = kwargs.pop("classes", "w-full")
    return ui.select(options, label=label, value=value).classes(classes).props("outlined", **kwargs)


def select_with_edit(options: list, label: str, value=None, on_edit=None, **kwargs):
    """
    Select field with an edit icon button next to it

    Args:
        options: List of options for the dropdown
        label: Label for the select field
        value: Default selected value
        on_edit: Callback function when edit icon is clicked
        **kwargs: Additional arguments passed to ui.select
    """
    with ui.row().classes("w-full gap-2 items-center"):
        classes = kwargs.pop("classes", "flex-1")
        ui.select(options, label=label, value=value).classes(classes).props("outlined", **kwargs)
        icon = ui.icon("edit").classes("text-yellow-500 cursor-pointer text-xl")
        if on_edit:
            icon.on("click", on_edit)
        return icon


def date_input(label: str, value: str = "", **kwargs):
    """
    Standardized date input field with outlined style

    Args:
        label: Label for the date input
        value: Default date value (format: DD/MM/YYYY)
        **kwargs: Additional arguments passed to ui.input
    """
    classes = kwargs.pop("classes", "w-full")
    return ui.input(label=label, value=value).classes(classes).props("outlined", **kwargs)


def number_input(label: str, value: str = "", **kwargs):
    """
    Standardized number input field with outlined style

    Args:
        label: Label for the number input
        value: Default number value
        **kwargs: Additional arguments passed to ui.input
    """
    classes = kwargs.pop("classes", "w-full")
    return ui.input(label=label, value=value).classes(classes).props("outlined", **kwargs)


def searchable_select(options: list, label: str, value=None, on_change=None, **kwargs):
    """
    Searchable/filterable select dropdown field with outlined style

    Args:
        options: List of options for the dropdown
        label: Label for the select field
        value: Default selected value
        on_change: Callback function when selection changes
        **kwargs: Additional arguments passed to ui.select
    """
    classes = kwargs.pop("classes", "w-full")
    select = (
        ui.select(options, label=label, value=value, with_input=True, on_change=on_change)
        .classes(classes)
        .props("outlined use-input")
    )
    return select


def date_input_with_calendar(label: str, value: str = "", **kwargs):
    """
    Date input field with mask and calendar picker

    Args:
        label: Label for the date input
        value: Default date value (format: DD/MM/YYYY)
        **kwargs: Additional arguments (classes, etc.)
    """
    classes = kwargs.pop("classes", "w-full")

    with ui.input(label).props("outlined").classes(classes) as date_input:
        date_input.props('mask="##/##/####"')
        if value:
            date_input.value = value

        with date_input, ui.menu().props("no-parent-event") as date_menu:
            with ui.date().props("mask=DD/MM/YYYY") as date_picker:
                date_picker.bind_value(date_input)
                with ui.row().classes("justify-end q-pa-sm"):
                    ui.button("Cerrar", on_click=date_menu.close).props("flat")

        with date_input.add_slot("append"):
            ui.icon("event").on("click", date_menu.open).classes("cursor-pointer")

    return date_input
