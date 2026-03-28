"""Линия связи между карточками"""
import math
import uuid
from PyQt6.QtWidgets import QGraphicsLineItem
from PyQt6.QtCore import Qt, QPointF, QLineF, QObject, pyqtSignal
from PyQt6.QtGui import QPen, QColor

from .arrow_head import ArrowHead, ConnectionType

class ConnectionSignals(QObject):
    """Сигналы для линии связи"""
    selected_changed = pyqtSignal(object, bool)
    about_to_delete = pyqtSignal(object)

class ConnectionLine(QGraphicsLineItem):
    """Линия связи с защитой от дублирования наконечников"""

    def __init__(self, source, target,
                 source_anchor: str = "right", target_anchor: str = "left",
                 connection_type: ConnectionType = ConnectionType.ASSOCIATION,
                 connection_id: str = None):
        super().__init__()

        self.id = connection_id or str(uuid.uuid4())
        self.source = source
        self.target = target
        self.source_anchor = source_anchor
        self.target_anchor = target_anchor
        self.connection_type = connection_type
        self._is_selected = False

        self.signals = ConnectionSignals()

        # Настройка пера
        self.setPen(QPen(QColor("#666666"), 2))
        self.setFlags(QGraphicsLineItem.GraphicsItemFlag.ItemIsSelectable)

        # Создаем наконечник ОДИН раз и сохраняем ссылку
        self.arrow_head = ArrowHead(QPointF(1, 0), self.connection_type)
        self.arrow_head.setParentItem(self)
        self.arrow_head.setZValue(100)

        self.update_position()

        # Связываем движение карточек с обновлением линии
        if hasattr(source, 'signals'):
            source.signals.position_changed.connect(self.update_position)
        if hasattr(target, 'signals'):
            target.signals.position_changed.connect(self.update_position)

    def update_position(self):
        """Обновление координат без пересоздания наконечника"""
        if not self.source or not self.target or not self.arrow_head:
            return

        self.prepareGeometryChange()

        p1 = self.source.get_anchor_point(self.source_anchor)
        p2 = self.target.get_anchor_point(self.target_anchor)

        line_vec = QLineF(p1, p2)
        if line_vec.length() < 10:
            self.arrow_head.setVisible(False)
            self.setLine(line_vec)
            return

        self.arrow_head.setVisible(True)

        # Расчет отступа, чтобы линия не заходила внутрь стрелки
        angle = math.atan2(-line_vec.dy(), line_vec.dx())
        offset = 12
        p2_adj = QPointF(
            p2.x() - math.cos(angle) * offset,
            p2.y() + math.sin(angle) * offset
        )

        self.setLine(QLineF(p1, p2_adj))
        self.arrow_head.setPos(self.mapFromScene(p2))
        self.arrow_head.set_direction(p2 - p1)

    def is_selected(self):
        """Возвращает состояние выделения (исправляет AttributeError)"""
        return self._is_selected

    def set_selected(self, selected):
        """Управляет визуальным выделением"""
        self._is_selected = selected
        color = QColor("#DC143C") if selected else QColor("#666666")
        width = 3 if selected else 2
        pen = QPen(color, width)
        self.setPen(pen)
        if self.arrow_head:
            self.arrow_head.setPen(pen)
        self.signals.selected_changed.emit(self, selected)

    def mousePressEvent(self, event):
        """Выделение линии при клике"""
        # Важно вызвать super(), чтобы QGraphicsItem пометил себя как selected
        super().mousePressEvent(event)

        # Переключаем наше внутреннее состояние
        self.set_selected(not self._is_selected)

        # Поглощаем событие, чтобы оно не ушло на сцену (не сняло выделение)
        event.accept()

    def set_connection_type(self, connection_type):
        """Смена типа без удаления объекта наконечника"""
        self.connection_type = connection_type
        if self.arrow_head:
            self.arrow_head.set_connection_type(connection_type)
        self.update_position()