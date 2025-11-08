from collections.abc import Callable

from nicegui import ui
from sqlalchemy.orm import Session

from src.components import payment_order_form


def create_payment_order_page(session_factory: Callable[[], Session]):
    """Create the payment order form page"""

    with ui.column().classes("w-full p-6"), ui.card().classes("w-full max-w-4xl mx-auto p-6 shadow-lg"):
        payment_order_form(session_factory=session_factory, mode="create")
