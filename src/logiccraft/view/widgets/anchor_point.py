"""Точка привязки на карточке"""
from PyQt6.QtWidgets import QGraphicsEllipseItem
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QBrush, QPen, QColor


class AnchorPoint(QGraphicsEllipseItem):
    """Точка привязки для создания связей"""

    def __init__(self, parent_card, anchor_name: str, size: int = 8):
        super().__init__(-size/2, -size/2, size, size)
        self.parent_card = parent_card
        self.anchor_name = anchor_name
        self.size = size
        self._drag_start = None

        # Настройка внешнего вида
        self.setBrush(QBrush(QColor("#FF6B6B")))
        self.setPen(QPen(QColor("#FFFFFF"), 1.5))
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setAcceptHoverEvents(True)
        self.setZValue(1000)

    def hoverEnterEvent(self, event):
        """При наведении мыши"""
        self.setBrush(QBrush(QColor("#FF4444")))
        self.setScale(1.2)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """При уходе мыши"""
        self.setBrush(QBrush(QColor("#FF6B6B")))
        self.setScale(1.0)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        """Начало перетаскивания для создания связи"""
        if event.button() == Qt.MouseButton.LeftButton:
            print(f"DEBUG: AnchorPoint mousePress - anchor={self.anchor_name}, card={self.parent_card.id}")
            self._drag_start = self.scenePos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

            # Уведомляем сцену о начале создания связи
            scene = self.scene()
            if scene and hasattr(scene, 'start_connection'):
                scene.start_connection(self.parent_card, self.anchor_name)
            else:
                print("DEBUG: scene or start_connection not found!")

            event.accept()

    def mouseMoveEvent(self, event):
        """Перемещение для создания связи"""
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_start:
            current_pos = self.mapToScene(event.pos())
            scene = self.scene()
            if scene and hasattr(scene, 'update_temp_line'):
                scene.update_temp_line(current_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Завершение создания связи"""
        if event.button() == Qt.MouseButton.LeftButton and self._drag_start:
            print(f"DEBUG: AnchorPoint mouseRelease - anchor={self.anchor_name}")
            self.setCursor(Qt.CursorShape.ArrowCursor)
            end_pos = self.mapToScene(event.pos())

            # Ищем целевую точку привязки
            search_rect = self._create_search_rect(end_pos)
            items = self.scene().items(search_rect)
            print(f"DEBUG: found {len(items)} items in search rect")

            target_anchor = None
            for item in items:
                if isinstance(item, AnchorPoint) and item.parent_card != self.parent_card:
                    target_anchor = item
                    print(f"DEBUG: found target anchor at {target_anchor.anchor_name} on card {target_anchor.parent_card.id}")
                    break
                else:
                    print("DEBUG: finish_connection not found!")

            scene = self.scene()
            if target_anchor:
                # Завершаем создание связи
                if hasattr(scene, 'finish_connection'):
                    print("DEBUG: calling finish_connection")
                    scene.finish_connection(target_anchor.parent_card, target_anchor.anchor_name)
            else:
                # Отменяем создание связи
                if hasattr(scene, 'cancel_connection'):
                    scene.cancel_connection()

        self._drag_start = None
        super().mouseReleaseEvent(event)

    def _create_search_rect(self, center: QPointF) -> QRectF:
        """Создать прямоугольник для поиска"""
        return QRectF(center.x() - 5, center.y() - 5, 10, 10)