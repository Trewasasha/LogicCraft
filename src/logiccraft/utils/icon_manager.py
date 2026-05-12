"""Утилита для управления иконками"""
from PyQt6.QtGui import QIcon
from pathlib import Path


class IconManager:
    """Менеджер иконок приложения"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._init_paths()
        self._icons_cache = {}

    def _init_paths(self):
        """Инициализация путей к иконкам"""
        # Путь к корню проекта (LogicCraft/)
        current_file = Path(__file__).resolve()  # src/logiccraft/utils/icon_manager.py
        # Поднимаемся на 4 уровня вверх до корня проекта
        project_root = current_file.parent.parent.parent.parent  # LogicCraft/

        # Папка с иконками: LogicCraft/resources/icons/
        self.icons_dir = project_root / "resources" / "icons"

        print(f"[DEBUG] Корень проекта: {project_root}")
        print(f"[DEBUG] Ищем иконки в: {self.icons_dir}")

        if self.icons_dir.exists():
            icons = list(self.icons_dir.glob("*.png"))
            print(f"[DEBUG] Найдено иконок: {len(icons)}")
            for icon in icons[:5]:
                print(f"  - {icon.name}")
        else:
            print(f"[WARNING] Папка с иконками не найдена: {self.icons_dir}")

    def get_icon(self, name: str) -> QIcon:
        print(f"[DEBUG] Ищу иконку: {name}")

        if name in self._icons_cache:
            print(f"[DEBUG] Иконка в кэше: {name}")
            return self._icons_cache[name]

        for ext in ['.png', '.svg', '.ico']:
            icon_path = self.icons_dir / f"{name}{ext}"
            print(f"[DEBUG] Проверяю: {icon_path}")
            if icon_path.exists():
                print(f"[DEBUG] Найдено! {icon_path}")
                icon = QIcon(str(icon_path))
                self._icons_cache[name] = icon
                return icon

        print(f"[DEBUG] Иконка НЕ найдена: {name}")



# Глобальный экземпляр
icon_manager = IconManager()