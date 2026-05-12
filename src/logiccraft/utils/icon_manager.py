"""Утилита для управления иконками"""
import logging
from PyQt6.QtGui import QIcon
from pathlib import Path

logger = logging.getLogger(__name__)


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

        logger.debug(f"Корень проекта: {project_root}")
        logger.debug(f"Ищем иконки в: {self.icons_dir}")

        if self.icons_dir.exists():
            icons = list(self.icons_dir.glob("*.png"))
            logger.debug(f"Найдено иконок: {len(icons)}")
            for icon in icons[:5]:
                logger.debug(f"  - {icon.name}")
        else:
            logger.warning(f"Папка с иконками не найдена: {self.icons_dir}")

    def get_icon(self, name: str) -> QIcon:
        """Получить иконку по имени (без расширения)"""
        logger.debug(f"Запрос иконки: {name}")

        if name in self._icons_cache:
            logger.debug(f"Иконка найдена в кэше: {name}")
            return self._icons_cache[name]

        for ext in ['.png', '.svg', '.ico']:
            icon_path = self.icons_dir / f"{name}{ext}"
            if icon_path.exists():
                logger.debug(f"Иконка загружена: {icon_path}")
                icon = QIcon(str(icon_path))
                self._icons_cache[name] = icon
                return icon

        logger.warning(f"Иконка не найдена: {name}")
        return QIcon()  # Возвращаем пустую иконку вместо None



# Глобальный экземпляр
icon_manager = IconManager()