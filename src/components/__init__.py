"""Reusable UI components for the application"""

from .buttons import icon_button, primary_button, secondary_button, small_button
from .inputs import (
    date_input,
    date_input_with_calendar,
    number_input,
    searchable_select,
    select_field,
    select_with_edit,
    text_input,
)
from .menu import create_menu
from .tables import create_invoice_table, scrollable_table, simple_table

__all__ = [
    # Buttons
    "primary_button",
    "secondary_button",
    "small_button",
    "icon_button",
    # Inputs
    "text_input",
    "select_field",
    "select_with_edit",
    "date_input",
    "date_input_with_calendar",
    "number_input",
    "searchable_select",
    # Tables
    "scrollable_table",
    "simple_table",
    "create_invoice_table",
    # Menu
    "create_menu",
]
