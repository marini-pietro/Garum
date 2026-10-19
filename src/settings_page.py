import flet as ft

def show_settings(e: ft.Event[ft.IconButton]):
    page = e.page
    page.dialog = ft.AlertDialog(
        title=ft.Text("Settings"),
        content=ft.Text("Settings dialog content goes here."),
        actions=[
            ft.TextButton("Close", on_click=lambda e: page.dialog.close())
        ],
    )
    page.dialog.open = True
    page.update()