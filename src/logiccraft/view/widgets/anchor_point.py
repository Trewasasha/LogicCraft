"""Точка привязки на карточке"""
from PyQt6.QtWidgets import QGraphicsEllipseItem
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QBrush, QPen, QColor

from ..theme import AnchorStyle


class AnchorPoint(QGraphicsEllipseItem):
    """Точка привязки для создания связей"""

    def __init__(self, parent_card, anchor_name: str, size: int = 8):
        super().__init__(-size/2, -size/2, size, size)
        self.parent_card = parent_card
        self.anchor_name = anchor_name
        self.size = size
        self._drag_start = None

        self.setBrush(QBrush(QColor(AnchorStyle.NORMAL_COLOR)))
        self.setPen(QPen(QColor(AnchorStyle.BORDER_COLOR), AnchorStyle.BORDER_WIDTH))
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setAcceptHoverEvents(True)
        self.setZValue(1000)

    def hoverEnterEvent(self, event):
        self.setBrush(QBrush(QColor(AnchorStyle.HOVER_COLOR)))
        self.setScale(AnchorStyle.HOVER_SCALE)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setBrush(QBrush(QColor(AnchorStyle.NORMAL_COLOR)))
        self.setScale(1.0)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = self.scenePos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            scene = self.scene()
            if scene and hasattr(scene, 'start_connection'):
                scene.start_connection(self.parent_card, self.anchor_name)
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_start:
            current_pos = self.mapToScene(event.pos())
            scene = self.scene()
            if scene and hasattr(scene, 'update_temp_line'):
                scene.update_temp_line(current_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._drag_start:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            end_pos = self.mapToScene(event.pos())

            search_rect = self._create_search_rect(end_pos)
            items = self.scene().items(search_rect)

            target_anchor = None
            for item in items:
                if isinstance(item, AnchorPoint) and item.parent_card != self.parent_card:
                    target_anchor = item
                    break

            scene = self.scene()
            if target_anchor and hasattr(scene, 'finish_connection'):
                scene.finish_connection(target_anchor.parent_card, target_anchor.anchor_name)
            elif hasattr(scene, 'cancel_connection'):
                scene.cancel_connection()

        self._drag_start = None
        super().mouseReleaseEvent(event)

    def _create_search_rect(self, center: QPointF) -> QRectF:
        return QRectF(center.x() - 5, center.y() - 5, 10, 10)
