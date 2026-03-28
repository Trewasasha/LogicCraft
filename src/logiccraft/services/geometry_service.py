"""Сервис для геометрических расчетов"""
import math
from PyQt6.QtCore import QPointF, QLineF
from typing import Tuple, Optional


class GeometryService:
    """Геометрические расчеты для диаграмм"""

    @staticmethod
    def calculate_anchor_point(rect, anchor_name: str) -> QPointF:
        """Вычислить точку привязки на прямоугольнике"""
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

        if anchor_name == "top":
            return QPointF(x + w / 2, y)
        elif anchor_name == "bottom":
            return QPointF(x + w / 2, y + h)
        elif anchor_name == "left":
            return QPointF(x, y + h / 2)
        elif anchor_name == "right":
            return QPointF(x + w, y + h / 2)
        else:
            return QPointF(x + w / 2, y + h / 2)

    @staticmethod
    def calculate_arrow_direction(p1: QPointF, p2: QPointF) -> QPointF:
        """Вычислить направление стрелки"""
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        length = math.sqrt(dx * dx + dy * dy)

        if length == 0:
            return QPointF(0, 0)

        return QPointF(dx / length, dy / length)

    @staticmethod
    def adjust_line_for_arrow(p1: QPointF, p2: QPointF, arrow_size: float = 12) -> Tuple[QPointF, QPointF]:
        """Скорректировать линию с учетом наконечника стрелки"""
        direction = GeometryService.calculate_arrow_direction(p1, p2)
        length = math.sqrt((p2.x() - p1.x())**2 + (p2.y() - p1.y())**2)

        if length <= arrow_size:
            return p1, p2

        # Отодвигаем конец линии на размер стрелки
        adjusted_p2 = QPointF(
            p2.x() - direction.x() * arrow_size,
            p2.y() - direction.y() * arrow_size
        )

        return p1, adjusted_p2

    @staticmethod
    def calculate_arrow_head_points(p1: QPointF, p2: QPointF, size: float = 12) -> list:
        """Вычислить точки для треугольника стрелки"""
        direction = GeometryService.calculate_arrow_direction(p1, p2)

        # Перпендикулярное направление
        perp = QPointF(-direction.y(), direction.x())

        # Точки треугольника
        tip = p2
        left = QPointF(
            tip.x() - direction.x() * size + perp.x() * size * 0.6,
            tip.y() - direction.y() * size + perp.y() * size * 0.6
        )
        right = QPointF(
            tip.x() - direction.x() * size - perp.x() * size * 0.6,
            tip.y() - direction.y() * size - perp.y() * size * 0.6
        )

        return [tip, left, right]

    @staticmethod
    def calculate_diamond_points(p1: QPointF, p2: QPointF, size: float = 12) -> list:
        """Вычислить точки для ромба"""
        direction = GeometryService.calculate_arrow_direction(p1, p2)
        perp = QPointF(-direction.y(), direction.x())

        center = QPointF(
            p2.x() - direction.x() * size * 0.7,
            p2.y() - direction.y() * size * 0.7
        )

        points = [
            center + direction * size,
            center + perp * size * 0.5,
            center - direction * size * 0.5,
            center - perp * size * 0.5
        ]

        return points

    @staticmethod
    def point_to_rect_distance(point: QPointF, rect) -> float:
        """Расстояние от точки до прямоугольника"""
        # Находим ближайшую точку на прямоугольнике
        rx, ry, rw, rh = rect.x(), rect.y(), rect.width(), rect.height()

        # Проекция на прямоугольник
        cx = max(rx, min(point.x(), rx + rw))
        cy = max(ry, min(point.y(), ry + rh))

        closest = QPointF(cx, cy)
        return math.sqrt((point.x() - closest.x())**2 + (point.y() - closest.y())**2)

    @staticmethod
    def find_best_anchor(rect, target_point: QPointF) -> str:
        """Найти лучшую точку привязки для соединения"""
        anchors = ["top", "bottom", "left", "right"]
        anchor_points = {
            "top": GeometryService.calculate_anchor_point(rect, "top"),
            "bottom": GeometryService.calculate_anchor_point(rect, "bottom"),
            "left": GeometryService.calculate_anchor_point(rect, "left"),
            "right": GeometryService.calculate_anchor_point(rect, "right")
        }

        best_anchor = "right"
        min_distance = float('inf')

        for anchor, point in anchor_points.items():
            dist = math.sqrt((point.x() - target_point.x())**2 +
                             (point.y() - target_point.y())**2)
            if dist < min_distance:
                min_distance = dist
                best_anchor = anchor

        return best_anchor