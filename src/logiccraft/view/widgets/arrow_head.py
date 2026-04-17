"""Наконечник стрелки для линий связи"""
import math
from PyQt6.QtWidgets import QGraphicsPolygonItem
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QPolygonF, QBrush, QPen, QColor
from enum import Enum


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
        print(f"DEBUG: ArrowHead created with type {connection_type}")

    def _update_shape(self):
        """Обновляет форму наконечника в зависимости от типа связи"""
        size = 12  # размер наконечника

        # Получаем строковое значение типа
        type_value = self.connection_type.value if hasattr(self.connection_type, 'value') else str(self.connection_type)
        print(f"DEBUG: ArrowHead._update_shape called with type: {type_value}")

        if type_value == "inheritance":
            # Треугольник (полый) для наследования
            points = [
                QPointF(size, 0),
                QPointF(0, -size * 0.6),
                QPointF(0, size * 0.6)
            ]
            polygon = QPolygonF(points)
            self.setPolygon(polygon)
            self.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            self.setPen(QPen(QColor("#666666"), 2))
            print("DEBUG: Set INHERITANCE shape")

        elif type_value == "composition":
            # Закрашенный ромб для композиции
            points = [
                QPointF(size, 0),
                QPointF(size / 2, -size * 0.6),
                QPointF(0, 0),
                QPointF(size / 2, size * 0.6)
            ]
            polygon = QPolygonF(points)
            self.setPolygon(polygon)
            self.setBrush(QBrush(QColor("#666666")))
            self.setPen(QPen(QColor("#666666"), 1.5))
            print("DEBUG: Set COMPOSITION shape")

        elif type_value == "aggregation":
            # Пустой ромб для агрегации
            points = [
                QPointF(size, 0),
                QPointF(size / 2, -size * 0.6),
                QPointF(0, 0),
                QPointF(size / 2, size * 0.6)
            ]
            polygon = QPolygonF(points)
            self.setPolygon(polygon)
            self.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            self.setPen(QPen(QColor("#666666"), 2))
            print("DEBUG: Set AGGREGATION shape")
        else:
            # Ассоциация - закрашенный треугольник (по умолчанию)
            points = [
                QPointF(size, 0),
                QPointF(0, -size * 0.6),
                QPointF(0, size * 0.6)
            ]
            polygon = QPolygonF(points)
            self.setPolygon(polygon)
            self.setBrush(QBrush(QColor("#666666")))
            self.setPen(QPen(QColor("#666666"), 1.5))
            print("DEBUG: Set ASSOCIATION shape")

        # Принудительно обновляем отображение
        self.update()

    def _update_rotation(self):
        """Обновляет поворот наконечника"""
        if hasattr(self, 'direction') and self.direction:
            angle = math.degrees(math.atan2(self.direction.y(), self.direction.x()))
            self.setRotation(angle)

    def set_direction(self, direction: QPointF):
        """Устанавливает направление и обновляет поворот"""
        self.direction = direction
        self._update_rotation()

    def set_connection_type(self, connection_type: ConnectionType):
        """Устанавливает тип связи и обновляет форму"""
        print(f"DEBUG: ArrowHead.set_connection_type called with {connection_type}")
        self.connection_type = connection_type
        self._update_shape()
        self.update()
        print(f"DEBUG: ArrowHead type updated to {self.connection_type}")