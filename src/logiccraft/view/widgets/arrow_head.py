"""Наконечник стрелки для линий связи"""
import math
from PyQt6.QtWidgets import QGraphicsPolygonItem
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QPolygonF, QBrush, QPen, QColor
from enum import Enum

from ..theme import ArrowStyle


class ConnectionType(Enum):
    """Типы связей"""
    ASSOCIATION = "association"
    INHERITANCE = "inheritance"
    COMPOSITION = "composition"
    AGGREGATION = "aggregation"


class ArrowHead(QGraphicsPolygonItem):
    """Наконечник стрелки с поддержкой разных типов связей"""

    def __init__(self, direction: QPointF, connection_type: ConnectionType):
        super().__init__()
        self.connection_type = connection_type
        self.direction = direction
        self._update_shape()
        self._update_rotation()

    def _update_shape(self):
        """Обновляет форму наконечника в зависимости от типа связи"""
        size = ArrowStyle.SIZE
        type_value = self.connection_type.value if hasattr(self.connection_type, 'value') else str(self.connection_type)

        if type_value == "inheritance":
            points = [QPointF(size, 0), QPointF(0, -size * 0.6), QPointF(0, size * 0.6)]
            self.setPolygon(QPolygonF(points))
            self.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            self.setPen(QPen(QColor(ArrowStyle.COLOR), ArrowStyle.WIDTH_NORMAL))

        elif type_value == "composition":
            points = [QPointF(size, 0), QPointF(size / 2, -size * 0.6), QPointF(0, 0), QPointF(size / 2, size * 0.6)]
            self.setPolygon(QPolygonF(points))
            self.setBrush(QBrush(QColor(ArrowStyle.COLOR)))
            self.setPen(QPen(QColor(ArrowStyle.COLOR), ArrowStyle.WIDTH_THIN))

        elif type_value == "aggregation":
            points = [QPointF(size, 0), QPointF(size / 2, -size * 0.6), QPointF(0, 0), QPointF(size / 2, size * 0.6)]
            self.setPolygon(QPolygonF(points))
            self.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            self.setPen(QPen(QColor(ArrowStyle.COLOR), ArrowStyle.WIDTH_NORMAL))

        else:  # association
            points = [QPointF(size, 0), QPointF(0, -size * 0.6), QPointF(0, size * 0.6)]
            self.setPolygon(QPolygonF(points))
            self.setBrush(QBrush(QColor(ArrowStyle.COLOR)))
            self.setPen(QPen(QColor(ArrowStyle.COLOR), ArrowStyle.WIDTH_THIN))

        self.update()

    def _update_rotation(self):
        """Обновляет поворот наконечника"""
        if hasattr(self, 'direction') and self.direction:
            angle = math.degrees(math.atan2(self.direction.y(), self.direction.x()))
            self.setRotation(angle)

    def set_direction(self, direction: QPointF):
        self.direction = direction
        self._update_rotation()

    def set_connection_type(self, connection_type: ConnectionType):
        self.connection_type = connection_type
        self._update_shape()
        self.update()
