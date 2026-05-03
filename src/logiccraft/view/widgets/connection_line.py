"""Линия связи между карточками"""
import math
import uuid
from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsTextItem
from PyQt6.QtCore import Qt, QPointF, QLineF, QObject, pyqtSignal
from PyQt6.QtGui import QPen, QColor, QFont

from .arrow_head import ArrowHead, ConnectionType
from ..theme import ConnectionStyle


class ConnectionSignals(QObject):
    """Сигналы для линии связи"""
    selected_changed = pyqtSignal(object, bool)
    about_to_delete = pyqtSignal(object)


class ConnectionLine(QGraphicsLineItem):
    """Линия связи с защитой от дублирования наконечников"""

    def __init__(self, source, target,
                 source_anchor: str = "right", target_anchor: str = "left",
                 connection_type: ConnectionType = ConnectionType.ASSOCIATION,
                 connection_id: str = None,
                 multiplicity: str = None,
                 name: str = None):
        super().__init__()

        self.id = connection_id or str(uuid.uuid4())
        self.source = source
        self.target = target
        self.source_anchor = source_anchor
        self.target_anchor = target_anchor
        self.connection_type = connection_type
        self.multiplicity = multiplicity or ""
        self.name = name or ""
        self._is_selected = False

        self.signals = ConnectionSignals()

        # Настройка пера
        pen = QPen(QColor(ConnectionStyle.LINE_COLOR), ConnectionStyle.LINE_WIDTH)
        type_value = connection_type.value if hasattr(connection_type, 'value') else str(connection_type)
        if type_value in ("dependency", "realization", "uc_include", "uc_extend"):
            pen.setStyle(Qt.PenStyle.DashLine)
        self.setPen(pen)
        self.setFlags(QGraphicsLineItem.GraphicsItemFlag.ItemIsSelectable)

        # Наконечник
        self.arrow_head = ArrowHead(QPointF(1, 0), self.connection_type)
        self.arrow_head.setParentItem(self)
        self.arrow_head.setZValue(100)

        # Текстовые метки
        label_font = QFont("Menlo", 9)
        self._source_mult_label = QGraphicsTextItem("", self)
        self._source_mult_label.setFont(label_font)
        self._source_mult_label.setDefaultTextColor(QColor("#7C3AED"))

        self._target_mult_label = QGraphicsTextItem("", self)
        self._target_mult_label.setFont(label_font)
        self._target_mult_label.setDefaultTextColor(QColor("#7C3AED"))

        self._name_label = QGraphicsTextItem("", self)
        self._name_label.setFont(QFont("Inter", 9))
        self._name_label.setDefaultTextColor(QColor("#6B7280"))

        # Стереотип-метка для Include/Extend
        self._stereotype_label = QGraphicsTextItem("", self)
        self._stereotype_label.setFont(QFont("Inter", 8, QFont.Weight.Medium))
        self._stereotype_label.setDefaultTextColor(QColor("#7C3AED"))
        self._update_stereotype_label()

        self._update_labels()
        self.update_position()

        if hasattr(source, 'signals'):
            source.signals.position_changed.connect(self.update_position)
        if hasattr(target, 'signals'):
            target.signals.position_changed.connect(self.update_position)

    def _update_labels(self):
        """Обновляет текст меток множественности и имени"""
        if self.multiplicity and ":" in self.multiplicity:
            src_m, tgt_m = self.multiplicity.split(":", 1)
        else:
            src_m, tgt_m = "", self.multiplicity

        self._source_mult_label.setPlainText(src_m)
        self._target_mult_label.setPlainText(tgt_m)
        self._name_label.setPlainText(self.name)

        self._source_mult_label.setVisible(bool(src_m))
        self._target_mult_label.setVisible(bool(tgt_m))
        self._name_label.setVisible(bool(self.name))

    def _update_stereotype_label(self):
        """Обновляет стереотип-метку для Include/Extend"""
        type_value = self.connection_type.value if hasattr(self.connection_type, 'value') else str(self.connection_type)
        if type_value == "uc_include":
            self._stereotype_label.setPlainText("«include»")
            self._stereotype_label.setVisible(True)
        elif type_value == "uc_extend":
            self._stereotype_label.setPlainText("«extend»")
            self._stereotype_label.setVisible(True)
        else:
            self._stereotype_label.setPlainText("")
            self._stereotype_label.setVisible(False)

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

        angle = math.atan2(-line_vec.dy(), line_vec.dx())
        offset = 12
        p2_adj = QPointF(
            p2.x() - math.cos(angle) * offset,
            p2.y() + math.sin(angle) * offset
        )

        self.setLine(QLineF(p1, p2_adj))
        self.arrow_head.setPos(self.mapFromScene(p2))
        self.arrow_head.set_direction(p2 - p1)

        # Позиционируем метки
        lp1 = self.mapFromScene(p1)
        lp2 = self.mapFromScene(p2)
        mid = QPointF((lp1.x() + lp2.x()) / 2, (lp1.y() + lp2.y()) / 2)

        # Множественность у источника
        self._source_mult_label.setPos(lp1.x() + 6, lp1.y() - 18)
        # Множественность у цели
        self._target_mult_label.setPos(lp2.x() - 20, lp2.y() - 18)
        # Имя по центру линии
        self._name_label.setPos(mid.x() - self._name_label.boundingRect().width() / 2, mid.y() - 18)
        # Стереотип по центру линии (чуть выше имени)
        sl_w = self._stereotype_label.boundingRect().width()
        offset = -32 if self._name_label.isVisible() else -18
        self._stereotype_label.setPos(mid.x() - sl_w / 2, mid.y() + offset)

    def is_selected(self):
        return self._is_selected

    def set_selected(self, selected):
        self._is_selected = selected
        color = QColor(ConnectionStyle.SELECTED_COLOR) if selected else QColor(ConnectionStyle.LINE_COLOR)
        width = ConnectionStyle.SELECTED_WIDTH if selected else ConnectionStyle.LINE_WIDTH
        pen = QPen(color, width)
        type_value = self.connection_type.value if hasattr(self.connection_type, 'value') else str(self.connection_type)
        if type_value in ("dependency", "realization"):
            pen.setStyle(Qt.PenStyle.DashLine)
        self.setPen(pen)
        if self.arrow_head:
            self.arrow_head.setPen(pen)
        self.signals.selected_changed.emit(self, selected)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.set_selected(not self._is_selected)
        event.accept()

    def set_connection_type(self, connection_type):
        self.connection_type = connection_type
        if self.arrow_head:
            self.arrow_head.set_connection_type(connection_type)
        type_value = connection_type.value if hasattr(connection_type, 'value') else str(connection_type)
        pen = self.pen()
        if type_value in ("dependency", "realization", "uc_include", "uc_extend"):
            pen.setStyle(Qt.PenStyle.DashLine)
        else:
            pen.setStyle(Qt.PenStyle.SolidLine)
        self.setPen(pen)
        self._update_stereotype_label()
        self.update_position()

    def set_multiplicity(self, multiplicity: str):
        """Обновить множественность"""
        self.multiplicity = multiplicity or ""
        self._update_labels()
        self.update_position()

    def set_name(self, name: str):
        """Обновить имя связи"""
        self.name = name or ""
        self._update_labels()
        self.update_position()