"""Сцена диаграммы"""
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsLineItem
from PyQt6.QtCore import Qt, QPointF, QLineF, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QPen, QPainter

from ..theme import SceneStyle

class DiagramScene(QGraphicsScene):
    """Сцена для отображения UML диаграммы с сеткой и поддержкой связей"""

    connection_ready = pyqtSignal(str, str, str, str)
    card_moved = pyqtSignal(str, float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundBrush(QBrush(QColor(SceneStyle.BACKGROUND)))
        self.setSceneRect(-5000, -5000, 10000, 10000)

        self.temp_line = None
        self.connection_source = None
        self.source_anchor = None
        self.connection_active = False

    def drawBackground(self, painter, rect):
        """Сетка фона"""
        super().drawBackground(painter, rect)
        pen = QPen(QColor(SceneStyle.GRID_COLOR), SceneStyle.GRID_WIDTH)
        painter.setPen(pen)

        left = int(rect.left()) - (int(rect.left()) % SceneStyle.GRID_STEP)
        top = int(rect.top()) - (int(rect.top()) % SceneStyle.GRID_STEP)

        for x in range(left, int(rect.right()), SceneStyle.GRID_STEP):
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
        for y in range(top, int(rect.bottom()), SceneStyle.GRID_STEP):
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)

    def start_connection(self, source_card, anchor_name):
        """Появление синего пунктира при начале тяги"""
        self.connection_source = source_card
        self.source_anchor = anchor_name
        self.connection_active = True

        start_pos = source_card.get_anchor_point(anchor_name)
        self.temp_line = QGraphicsLineItem(QLineF(start_pos, start_pos))
        self.temp_line.setPen(QPen(QColor(SceneStyle.TEMP_LINE_COLOR), 2, Qt.PenStyle.DashLine))

        # Временная линия должна быть прозрачной для кликов
        self.temp_line.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.temp_line.setZValue(1000)
        self.addItem(self.temp_line)

    def mouseMoveEvent(self, event):
        """Тянем линию за мышкой"""
        if self.connection_active and self.temp_line:
            line = self.temp_line.line()
            line.setP2(event.scenePos())
            self.temp_line.setLine(line)
        super().mouseMoveEvent(event)

    def finish_connection(self, target_card, target_anchor):
        """Завершение: удаляем пунктир и шлем сигнал контроллеру"""
        if not self.connection_active:
            return

        if self.temp_line:
            self.removeItem(self.temp_line)
            self.temp_line = None

        if self.connection_source and target_card and self.connection_source != target_card:
            self.connection_ready.emit(
                self.connection_source.id,
                target_card.id,
                self.source_anchor,
                target_anchor
            )

        self.connection_source = None
        self.source_anchor = None
        self.connection_active = False

    def cancel_connection(self):
        """Отмена тяги"""
        if self.temp_line:
            self.removeItem(self.temp_line)
            self.temp_line = None
        self.connection_source = None
        self.source_anchor = None
        self.connection_active = False

    def on_card_moved(self, card):
        """Snap to grid + групповое перемещение"""
        from ..widgets.uml_card import UMLCard
        grid = SceneStyle.GRID_STEP

        # Если выделено несколько — двигаем все вместе
        selected_cards = [item for item in self.selectedItems() if isinstance(item, UMLCard)]
        targets = selected_cards if len(selected_cards) > 1 else [card]

        for c in targets:
            x = round(c.pos().x() / grid) * grid
            y = round(c.pos().y() / grid) * grid
            if c.pos().x() != x or c.pos().y() != y:
                c.setPos(x, y)
            self.card_moved.emit(c.id, c.pos().x(), c.pos().y())