"""Централизованное хранилище стилей view-слоя LogicCraft"""
from dataclasses import dataclass, field
from PyQt6.QtGui import QFont
import logging
import os


@dataclass(frozen=True)
class _CardStyle:
    BACKGROUND: str = "#f5f5dc"
    BORDER: str = "#4169E1"
    SELECTED_BORDER: str = "#DC143C"
    HEADER_BG: str = "#4169E1"
    HEADER_TEXT: str = "white"
    ATTRS_TEXT: str = "#2c3e50"
    METHODS_TEXT: str = "#27ae60"
    DIVIDER: str = "#4169E1"
    BORDER_WIDTH: int = 2
    SELECTED_BORDER_WIDTH: int = 3

    @property
    def HEADER_FONT(self) -> QFont:
        return QFont("Arial", 10, QFont.Weight.Bold)

    @property
    def ATTRS_FONT(self) -> QFont:
        return QFont("Menlo", 9)

    @property
    def METHODS_FONT(self) -> QFont:
        return QFont("Menlo", 9)


@dataclass(frozen=True)
class _ConnectionStyle:
    LINE_COLOR: str = "#666666"
    LINE_WIDTH: int = 2
    SELECTED_COLOR: str = "#DC143C"
    SELECTED_WIDTH: int = 3


@dataclass(frozen=True)
class _SceneStyle:
    BACKGROUND: str = "#fafafa"
    GRID_COLOR: str = "#e0e0e0"
    GRID_WIDTH: float = 0.5
    GRID_STEP: int = 50
    TEMP_LINE_COLOR: str = "#4169E1"


@dataclass(frozen=True)
class _AnchorStyle:
    NORMAL_COLOR: str = "#FF6B6B"
    HOVER_COLOR: str = "#FF4444"
    BORDER_COLOR: str = "#FFFFFF"
    BORDER_WIDTH: float = 1.5
    HOVER_SCALE: float = 1.2


@dataclass(frozen=True)
class _ArrowStyle:
    COLOR: str = "#666666"
    WIDTH_NORMAL: float = 2.0
    WIDTH_THIN: float = 1.5
    SIZE: int = 12


CardStyle = _CardStyle()
ConnectionStyle = _ConnectionStyle()
SceneStyle = _SceneStyle()
AnchorStyle = _AnchorStyle()
ArrowStyle = _ArrowStyle()


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
