from typing import Callable
from datetime import datetime
from pathlib import Path

from nicegui import ui
from sqlalchemy.orm import Session, joinedload

from src.components import (
    primary_button,
    searchable_select,
)
from src.models import Account, PaymentOrder
from src.services.pdf_generator import generate_pdf


MONTH_NAMES = [
    '', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
]

ROWS_PER_PAGE = 48


def print_check_list_page(session_factory: Callable[[], Session]):
    """Create the print check list page"""

    accounts_data: list[str] = []
    
    account_select = None
    month_select = None
    year_select = None

    def load_accounts():
        """Load all accounts from database"""
        nonlocal accounts_data
        session = session_factory()
        try:
            accounts = session.query(Account).order_by(Account.name).all()
            accounts_data.clear()
            accounts_data.extend([account.name for account in accounts])
        finally:
            session.close()

    def get_account_by_name(account_name: str) -> Account | None:
        """Get account by name"""
        if not account_name:
            return None
        session = session_factory()
        try:
            account = session.query(Account).filter_by(name=account_name).first()
            return account
        finally:
            session.close()

    def split_into_pages(payment_orders, rows_per_page=ROWS_PER_PAGE):
        """Split payment orders into pages"""
        pages = []
        for i in range(0, len(payment_orders), rows_per_page):
            pages.append(payment_orders[i:i + rows_per_page])
        return pages

    def prepare_page_data(payment_orders, account_name, month_name, year, show_header=True):
        """Prepare data for a single page"""
        return {
            'account_name': account_name,
            'month': month_name,
            'year': year,
            'show_header': show_header,
            'payment_orders': payment_orders,
        }

    def generate_check_list():
        """Generate check list PDF"""
        account_name = account_select.value if account_select else ""
        month_str = month_select.value if month_select else ""
        year_str = year_select.value if year_select else ""

        if not all([account_name, month_str, year_str]):
            ui.notify("Por favor complete todos los campos", type="negative")
            return

        try:
            month_num = MONTH_NAMES.index(month_str)
            year = int(year_str)
        except (ValueError, IndexError):
            ui.notify("Valores de mes o año inválidos", type="negative")
            return

        account = get_account_by_name(account_name)
        if not account:
            ui.notify("Cuenta no encontrada", type="negative")
            return

        session = session_factory()
        try:
            start_date = datetime(year, month_num, 1).date()
            
            # Filter is done with half open interval, [start_date, end_date)
            # to avoid having to get last day of month
            if month_num < 12:
                end_date = datetime(year, month_num + 1, 1).date()
            else:
                end_date = datetime(year + 1, 1, 1).date()

            payment_orders = session.query(PaymentOrder).options(
                joinedload(PaymentOrder.supplier),
                joinedload(PaymentOrder.invoices),
                joinedload(PaymentOrder.account),
                joinedload(PaymentOrder.detail)
            ).filter(
                PaymentOrder.account_id == account.id,
                PaymentOrder.issue_date >= start_date,
                PaymentOrder.issue_date < end_date
            ).order_by(PaymentOrder.check_number).all()

            if not payment_orders:
                ui.notify(
                    f"No se encontraron órdenes de pago para {account_name} en {month_str} {year}",
                    type="warning"
                )
                return

            pages = split_into_pages(payment_orders, ROWS_PER_PAGE)
            
            pages_data = []
            for i, page_orders in enumerate(pages):
                page_data = prepare_page_data(
                    payment_orders=page_orders,
                    account_name=account_name,
                    month_name=month_str.upper(),
                    year=year,
                    show_header=(i == 0),
                )
                pages_data.append(page_data)

            output_path = f"Lista_Cheques_{account_name}_{month_str}_{year}.pdf"
            pdf_path = generate_pdf(
                template_name='check_list',
                pages_data=pages_data,
                output_path=output_path
            )
            
            ui.notify(
                f"PDF generado: {Path(pdf_path).name} ({len(payment_orders)} órdenes en {len(pages)} página(s))",
                type="positive"
            )

        except Exception as e:
            ui.notify(f"Error al generar PDF: {str(e)}", type="negative")
        finally:
            session.close()

    load_accounts()

    current_month = datetime.now().month
    current_year = datetime.now().year
    years = [str(year) for year in range(current_year, current_year - 5, -1)]
    months = MONTH_NAMES[1:]

    with ui.column().classes("w-full p-6"):
        with ui.card().classes("w-full max-w-4xl mx-auto p-6 shadow-lg"):
            ui.label("Imprimir Lista de Cheques").classes(
                "text-2xl font-normal text-gray-700 mb-6"
            )

            with ui.column().classes("w-full gap-4 mb-6"):
                account_select = searchable_select(
                    accounts_data,
                    label="Cuenta",
                )

                with ui.row().classes("w-full gap-4"):
                    with ui.column().classes("flex-1"):
                        month_select = ui.select(
                            months,
                            label="Mes",
                            value=MONTH_NAMES[current_month]
                        ).classes("w-full")

                    with ui.column().classes("flex-1"):
                        year_select = ui.select(
                            years,
                            label="Año",
                            value=str(current_year)
                        ).classes("w-full")

            with ui.row().classes("w-full justify-end mt-6"):
                primary_button(
                    "Generar PDF",
                    icon="picture_as_pdf",
                    on_click=generate_check_list
                )

