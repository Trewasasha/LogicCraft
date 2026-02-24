import sys
import asyncio
from pathlib import Path
import flet as ft
import uvicorn

# Исправление путей
root_path = Path(__file__).resolve().parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from logiccraft.view.editor import DiagramEditor
from logiccraft.controllers.api_server import app as fastapi_app

def main_window(page: ft.Page):
    page.title = "LogicCraft UML Architect"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.Colors.BLUE_GREY_900
    page.window_width = 1200
    page.window_height = 800

    editor = DiagramEditor()
    page.add(ft.Container(content=editor, expand=True))
    page.update()

def run_fastapi():
    """Функция для запуска сервера в отдельном потоке, чтобы не вешать GUI"""
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="warning")

if __name__ == "__main__":
    import threading

    # 1. Запускаем сервер в фоновом потоке
    api_thread = threading.Thread(target=run_fastapi, daemon=True)
    api_thread.start()

    # 2. Запускаем Flet в основном потоке (Mac это любит)
    # Используем современный ft.run, который сам создаст нужный loop
    ft.run(main_window)