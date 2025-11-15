from nicegui import ui
from nicegui.testing import User

from src.components.menu import create_menu


async def test_about_button_exists(user: User):
    @ui.page("/test-menu")
    def test_page():
        create_menu()

    await user.open("/test-menu")

    about_button = user.find("about_button")
    assert about_button.elements


async def test_about_dialog_opens_and_shows_content(user: User):
    @ui.page("/test-menu")
    def test_page():
        create_menu()

    await user.open("/test-menu")

    user.find("about_button").click()

    await user.should_see("UTA - Gestión de Órdenes de Pago")
    await user.should_see("Creado por Mariano Acebal")
    await user.should_see("Versión:")
    await user.should_see("https://github.com/macebal/uta-gestion-ops")


async def test_about_dialog_close_button_works(user: User):
    @ui.page("/test-menu")
    def test_page():
        create_menu()

    await user.open("/test-menu")

    user.find("about_button").click()

    await user.should_see("UTA - Gestión de Órdenes de Pago")

    user.find("Cerrar").click()

    dialogs = user.find(ui.dialog).elements
    assert all(not dialog.value for dialog in dialogs)
