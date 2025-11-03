from nicegui import native, ui
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base
from src.pages.home import home_page
from src.pages.payment_orders.create_payment_order import create_payment_order_page
from src.pages.payment_orders.print_payment_orders import print_payment_orders_page
from src.pages.checks.print_check_list import print_check_list_page
from src.pages.accounts.manage_accounts import manage_accounts_page
from src.pages.suppliers.manage_suppliers import manage_suppliers_page
from src.pages.details.manage_details import manage_details_page
from src.components.menu import create_menu


DATABASE_URL = "sqlite:///gestion_ops.db"
engine = create_engine(DATABASE_URL, echo=True)

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@ui.page("/")
def page():
    ui.page_title("UTA - Gestión de Órdenes de Pago")
    create_menu()
    home_page(SessionLocal)


@ui.page("/payment-orders/create")
def payment_order_page():
    ui.page_title("Nueva Orden de Pago")
    create_menu()
    create_payment_order_page(SessionLocal)


@ui.page("/payment-orders/print")
def print_orders_page():
    ui.page_title("Imprimir Órdenes de Pago")
    create_menu()
    print_payment_orders_page(SessionLocal)


@ui.page("/checks/print")
def print_checks_page():
    ui.page_title("Imprimir Lista de Cheques")
    create_menu()
    print_check_list_page(SessionLocal)


@ui.page("/accounts/manage")
def accounts_page():
    ui.page_title("Gestión de Cuentas")
    create_menu()
    manage_accounts_page(SessionLocal)


@ui.page("/suppliers/manage")
def suppliers_page():
    ui.page_title("Gestión de Proveedores")
    create_menu()
    manage_suppliers_page(SessionLocal)


@ui.page("/details/manage")
def details_page():
    ui.page_title("Gestión de Detalles")
    create_menu()
    manage_details_page(SessionLocal)


ui.run(
    reload=False,
    native=True,
    port=native.find_open_port(),
    window_size=(1200, 700),
    title="UTA - Gestión de Órdenes de Pago",
)
