"""Main entry point for LogicCraft UML Editor"""

import sys
from PyQt6.QtWidgets import QApplication
from logiccraft.view import DiagramEditor


def main():
    """Запуск приложения"""
    app = QApplication(sys.argv)

    # Устанавливаем стиль
    app.setStyle("Fusion")

    # Создаем и показываем главное окно
    editor = DiagramEditor()
    editor.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()