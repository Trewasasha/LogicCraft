"""Наконечник стрелки для линий связи"""
import math
from PyQt6.QtWidgets import QGraphicsPathItem
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QPolygonF, QBrush, QColor, QPen, QPainterPath
from enum import Enum

from ..theme import ArrowStyle


class ConnectionType(Enum):
    """Типы связей"""
    ASSOCIATION = "association"
    INHERITANCE = "inheritance"
    COMPOSITION = "composition"
    AGGREGATION = "aggregation"
    DEPENDENCY = "dependency"
    REALIZATION = "realization"
    INTERACTION = "interaction"
    # Use Case
    UC_ASSOCIATION = "uc_association"
    UC_INCLUDE = "uc_include"
    UC_EXTEND = "uc_extend"


class ArrowHead(QGraphicsPathItem):
    """Наконечник стрелки на базе QPainterPath, устойчивый к любым входным типам данных"""

    def __init__(self, direction: QPointF, connection_type):
        super().__init__()
        self.connection_type = connection_type
        self.direction = direction
        self._update_shape()
        self._update_rotation()

    def _get_clean_type(self) -> str:
        """Абсолютно безопасное извлечение типа связи при любых типах данных из контроллера"""
        if connection_type_attr := getattr(self.connection_type, 'value', None):
            val = str(connection_type_attr)
        else:
            val = str(self.connection_type)

        # Если пришла строка вида "ConnectionType.UC_INCLUDE"
        if "." in val:
            val = val.split(".")[-1]

        return val.lower().strip()

    def _update_shape(self):
        """Обновляет форму наконечника через векторный путь QPainterPath"""
        size = ArrowStyle.SIZE
        type_str = self._get_clean_type()

        normal_pen = QPen(QColor(ArrowStyle.COLOR), ArrowStyle.WIDTH_NORMAL)
        thin_pen = QPen(QColor(ArrowStyle.COLOR), ArrowStyle.WIDTH_THIN)
        background_brush = QBrush(QColor("#FFFFFF"))

        path = QPainterPath()

        # Проверяем все возможные вариации строк (включая префиксы use_case / uc)
        if type_str in ("inheritance", "realization"):
            path.moveTo(size, 0)
            path.lineTo(0, -size * 0.6)
            path.lineTo(0, size * 0.6)
            path.closeSubpath()
            self.setPath(path)
            self.setBrush(background_brush)
            self.setPen(normal_pen)

        elif type_str == "composition":
            path.moveTo(size, 0)
            path.lineTo(size / 2, -size * 0.6)
            path.lineTo(0, 0)
            path.lineTo(size / 2, size * 0.6)
            path.closeSubpath()
            self.setPath(path)
            self.setBrush(QBrush(QColor(ArrowStyle.COLOR)))
            self.setPen(thin_pen)

        elif type_str == "aggregation":
            path.moveTo(size, 0)
            path.lineTo(size / 2, -size * 0.6)
            path.lineTo(0, 0)
            path.lineTo(size / 2, size * 0.6)
            path.closeSubpath()
            self.setPath(path)
            self.setBrush(background_brush)
            self.setPen(normal_pen)

        elif type_str in ("dependency", "uc_include", "uc_extend", "include", "extend"):
            # Идеальный открытый уголок без заливки ядра
            path.moveTo(0, -size * 0.5)
            path.lineTo(size, 0)
            path.lineTo(0, size * 0.5)
            self.setPath(path)
            self.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            self.setPen(normal_pen)

        elif type_str in ("uc_association", "association_none", "none"):
            # Обычная ассоциация в Use Case — просто линия
            self.setPath(path)
            self.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            self.setPen(QPen(Qt.PenStyle.NoPen))

        else:  # association, interaction
            path.moveTo(size, 0)
            path.lineTo(0, -size * 0.5)
            path.lineTo(0, size * 0.5)
            path.closeSubpath()
            self.setPath(path)
            self.setBrush(QBrush(QColor(ArrowStyle.COLOR)))
            self.setPen(thin_pen)

        self.update()

    def _update_rotation(self):
        if hasattr(self, 'direction') and self.direction:
            angle = math.degrees(math.atan2(self.direction.y(), self.direction.x()))
            self.setRotation(angle)

    def set_direction(self, direction: QPointF):
        self.direction = direction
        self._update_rotation()

    def set_connection_type(self, connection_type):
        self.connection_type = connection_type
        self._update_shape()
        self.update()