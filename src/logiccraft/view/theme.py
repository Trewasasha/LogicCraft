"""Централизованное хранилище стилей view-слоя LogicCraft"""
from dataclasses import dataclass, field
from PyQt6.QtGui import QFont
import logging
import os


@dataclass(frozen=True)
class _CardStyle:
    BACKGROUND: str = "#FFFFFF"
    BORDER: str = "#E5E0F8"
    SELECTED_BORDER: str = "#7C3AED"
    HEADER_BG: str = "#7C3AED"
    HEADER_TEXT: str = "#FFFFFF"
    ATTRS_TEXT: str = "#1F1F1F"
    METHODS_TEXT: str = "#1F1F1F"
    DIVIDER: str = "#E5E0F8"
    BORDER_WIDTH: int = 1
    SELECTED_BORDER_WIDTH: int = 2
    BORDER_RADIUS: int = 12

    @property
    def HEADER_FONT(self) -> QFont:
        f = QFont("Inter", 11, QFont.Weight.Bold)
        return f

    @property
    def ATTRS_FONT(self) -> QFont:
        return QFont("Menlo", 9)

    @property
    def METHODS_FONT(self) -> QFont:
        return QFont("Menlo", 9)


@dataclass(frozen=True)
class _ConnectionStyle:
    LINE_COLOR: str = "#9B72F5"
    LINE_WIDTH: int = 2
    SELECTED_COLOR: str = "#7C3AED"
    SELECTED_WIDTH: int = 3


@dataclass(frozen=True)
class _SceneStyle:
    BACKGROUND: str = "#F0EFFE"
    GRID_COLOR: str = "#E0D9FC"
    GRID_WIDTH: float = 0.5
    GRID_STEP: int = 50
    TEMP_LINE_COLOR: str = "#7C3AED"


@dataclass(frozen=True)
class _AnchorStyle:
    NORMAL_COLOR: str = "#9B72F5"
    HOVER_COLOR: str = "#7C3AED"
    BORDER_COLOR: str = "#FFFFFF"
    BORDER_WIDTH: float = 1.5
    HOVER_SCALE: float = 1.2


@dataclass(frozen=True)
class _ArrowStyle:
    COLOR: str = "#9B72F5"
    WIDTH_NORMAL: float = 2.0
    WIDTH_THIN: float = 1.5
    SIZE: int = 12


@dataclass(frozen=True)
class _DialogStyle:
    BACKGROUND: str = "#FFFFFF"
    BORDER: str = "#E5E0F8"
    TEXT_COLOR: str = "#1F1F1F"
    INPUT_BACKGROUND: str = "#F8F6FF"
    INPUT_BORDER: str = "#D4C9F8"
    INPUT_FOCUS_BORDER: str = "#7C3AED"
    BUTTON_PRIMARY: str = "#7C3AED"
    BUTTON_PRIMARY_HOVER: str = "#6D28D9"
    BUTTON_SECONDARY: str = "#F8F6FF"
    BUTTON_SECONDARY_HOVER: str = "#EDE9FE"
    SELECTION_COLOR: str = "#7C3AED"


@dataclass(frozen=True)
class _MenuStyle:
    BACKGROUND: str = "#FFFFFF"
    BORDER: str = "#E5E0F8"
    TEXT_COLOR: str = "#1F1F1F"
    HOVER_BACKGROUND: str = "#F3EEFF"
    HOVER_TEXT: str = "#7C3AED"
    DISABLED_TEXT: str = "#AAAAAA"
    SEPARATOR: str = "#E5E0F8"
    DELETE_COLOR: str = "#EF4444"


CardStyle = _CardStyle()
ConnectionStyle = _ConnectionStyle()
SceneStyle = _SceneStyle()
AnchorStyle = _AnchorStyle()
ArrowStyle = _ArrowStyle()
DialogStyle = _DialogStyle()
MenuStyle = _MenuStyle()


def apply_stylesheet(app) -> None:
    """Загружает и применяет style.qss к QApplication.

    При отсутствии файла логирует предупреждение и возвращает управление
    без исключения — приложение продолжает работу с системными стилями Qt.
    """
    qss_path = os.path.join(os.path.dirname(__file__), "..", "style.qss")
    qss_path = os.path.normpath(qss_path)
    try:
        with open(qss_path, "r", encoding="utf-8") as f:
            content = f.read()
        app.setStyleSheet(content)
    except FileNotFoundError:
        logging.warning("style.qss not found at %s, skipping stylesheet", qss_path)
