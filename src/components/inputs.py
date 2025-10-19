from nicegui import ui


def text_input(label: str, value: str = "", **kwargs):
    """
    Standardized text input field with outlined style

    Args:
        label: Label for the input field
        value: Default value for the input
        **kwargs: Additional arguments passed to ui.input (e.g., classes, on_change)
    """
    classes = kwargs.pop("classes", "w-full")
    return (
        ui.input(label=label, value=value).classes(classes).props("outlined", **kwargs)
    )


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
    return (
        ui.select(options, label=label, value=value)
        .classes(classes)
        .props("outlined", **kwargs)
    )


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
        ui.select(options, label=label, value=value).classes(classes).props(
            "outlined", **kwargs
        )
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
    return (
        ui.input(label=label, value=value).classes(classes).props("outlined", **kwargs)
    )


def number_input(label: str, value: str = "", **kwargs):
    """
    Standardized number input field with outlined style

    Args:
        label: Label for the number input
        value: Default number value
        **kwargs: Additional arguments passed to ui.input
    """
    classes = kwargs.pop("classes", "w-full")
    return (
        ui.input(label=label, value=value).classes(classes).props("outlined", **kwargs)
    )
