from typing import Optional

from nicegui import ui


def primary_button(text: str, on_click=None, icon: Optional[str] = None, **kwargs):
    """
    Standardized primary button with blue background

    Args:
        text: Button text
        on_click: Click handler function
        icon: Optional icon name
        **kwargs: Additional arguments (e.g., classes)
    """
    classes = kwargs.pop(
        "classes", "bg-blue-500 text-white px-6 py-2 rounded-lg text-base"
    )
    btn = ui.button(text, icon=icon).classes(classes)
    if on_click:
        btn.on("click", on_click)
    return btn


def secondary_button(text: str, on_click=None, icon: Optional[str] = None, **kwargs):
    """
    Standardized secondary button with gray background

    Args:
        text: Button text
        on_click: Click handler function
        icon: Optional icon name
        **kwargs: Additional arguments (e.g., classes)
    """
    classes = kwargs.pop(
        "classes", "bg-gray-500 text-white px-6 py-2 rounded-lg text-base"
    )
    btn = ui.button(text, icon=icon).classes(classes)
    if on_click:
        btn.on("click", on_click)
    return btn


def small_button(text: str, on_click=None, icon: Optional[str] = None, **kwargs):
    """
    Standardized small button with blue background

    Args:
        text: Button text
        on_click: Click handler function
        icon: Optional icon name
        **kwargs: Additional arguments (e.g., classes)
    """
    classes = kwargs.pop("classes", "bg-blue-500 text-white px-4 py-1 rounded")
    btn = ui.button(text, icon=icon).classes(classes)
    if on_click:
        btn.on("click", on_click)
    return btn


def icon_button(icon: str, on_click=None, color: str = "text-gray-600", **kwargs):
    """
    Icon-only button

    Args:
        icon: Icon name
        on_click: Click handler function
        color: Tailwind color class for the icon
        **kwargs: Additional arguments
    """
    classes = kwargs.pop("classes", f"{color} cursor-pointer text-xl")
    btn = ui.icon(icon).classes(classes)
    if on_click:
        btn.on("click", on_click)
    return btn
