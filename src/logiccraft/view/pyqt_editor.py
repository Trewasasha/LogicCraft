import sys
import json
import random
import math
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QToolBar, QFileDialog, QMessageBox, QGraphicsView,
    QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem,
    QGraphicsItem, QInputDialog, QListWidget, QListWidgetItem,
    QDialog, QDialogButtonBox, QLineEdit, QApplication,
    QGraphicsEllipseItem, QGraphicsPolygonItem, QComboBox
)
from PyQt6.QtCore import Qt, QPointF, QRectF, QLineF, QObject, pyqtSignal
from PyQt6.QtGui import (
    QBrush, QColor, QPen, QFont, QPainter, QAction, QPolygonF
)
import uuid


class ConnectionType(Enum):
    """Типы связей между классами"""
    ASSOCIATION = "association"      # Ассоциация (простая линия)
    INHERITANCE = "inheritance"      # Наследование (треугольник)
    COMPOSITION = "composition"      # Композиция (закрашенный ромб)
    AGGREGATION = "aggregation"      # Агрегация (пустой ромб)


class CardSignals(QObject):
    """Сигналы для карточки"""
    selected_changed = pyqtSignal(object, bool)
    position_changed = pyqtSignal(object)
    anchor_moved = pyqtSignal(object, str)  # карточка, позиция
    about_to_delete = pyqtSignal(object)  # сигнал перед удалением


class AnchorPoint(QGraphicsEllipseItem):
    """Точка привязки на карточке"""

    def __init__(self, parent_card, anchor_name: str, size: int = 8):
        super().__init__(-size/2, -size/2, size, size)
        self.parent_card = parent_card
        self.anchor_name = anchor_name
        self.size = size

        self.setBrush(QBrush(QColor("#FF6B6B")))
        self.setPen(QPen(QColor("#FFFFFF"), 1.5))
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setAcceptHoverEvents(True)
        self.setZValue(1000)
        self._drag_start = None

    def hoverEnterEvent(self, event):
        self.setBrush(QBrush(QColor("#FF4444")))
        self.setScale(1.2)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setBrush(QBrush(QColor("#FF6B6B")))
        self.setScale(1.0)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = self.scenePos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.parent_card.signals.anchor_moved.emit(self.parent_card, self.anchor_name)
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

            search_rect = QRectF(end_pos.x() - 5, end_pos.y() - 5, 10, 10)
            items = self.scene().items(search_rect)

            target_anchor = None
            for item in items:
                if isinstance(item, AnchorPoint) and item.parent_card != self.parent_card:
                    target_anchor = item
                    break

            scene = self.scene()
            if target_anchor:
                if hasattr(scene, 'finish_connection'):
                    scene.finish_connection(target_anchor.parent_card, target_anchor.anchor_name)
            else:
                if hasattr(scene, 'cancel_connection'):
                    scene.cancel_connection()

        self._drag_start = None
        super().mouseReleaseEvent(event)


class UMLCard(QGraphicsRectItem):
    """Карточка класса UML"""

    ANCHOR_TOP = "top"
    ANCHOR_BOTTOM = "bottom"
    ANCHOR_LEFT = "left"
    ANCHOR_RIGHT = "right"

    def __init__(self, name: str, x: float = 0, y: float = 0,
                 width: float = 160, height: float = 100,
                 attributes: list = None, methods: list = None,
                 card_id: str = None):
        super().__init__(0, 0, width, height)
        self.setPos(x, y)

        self.id = card_id or str(uuid.uuid4())
        self.name = name
        self.attributes = attributes or []
        self.methods = methods or []

        self.anchors = {}
        self._anchor_size = 8
        self.signals = CardSignals()

        self.setBrush(QBrush(QColor("#f5f5dc")))
        self.setPen(QPen(QColor("#4169E1"), 2))
        self.setFlags(
            QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        self._create_elements()
        self._create_anchors()
        self.update_content()

    def _create_elements(self):
        """Создание визуальных частей карточки"""
        self.header_bg = QGraphicsRectItem(0, 0, self.rect().width(), 30, self)
        self.header_bg.setBrush(QBrush(QColor("#4169E1")))
        self.header_bg.setPen(QPen(Qt.PenStyle.NoPen))

        self.header_text = QGraphicsTextItem(self.name, self)
        self.header_text.setDefaultTextColor(QColor("white"))
        self.header_text.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        self.attrs_text = QGraphicsTextItem("", self)
        self.attrs_text.setFont(QFont("Menlo", 9))
        self.attrs_text.setDefaultTextColor(QColor("#2c3e50"))

        self.methods_text = QGraphicsTextItem("", self)
        self.methods_text.setFont(QFont("Menlo", 9))
        self.methods_text.setDefaultTextColor(QColor("#27ae60"))

    def _create_anchors(self):
        """Создает объекты точек привязки"""
        for name in [self.ANCHOR_TOP, self.ANCHOR_BOTTOM, self.ANCHOR_LEFT, self.ANCHOR_RIGHT]:
            anchor = AnchorPoint(self, name, self._anchor_size)
            anchor.setParentItem(self)
            self.anchors[name] = anchor

    def _update_anchor_positions(self):
        """Расставляет точки по границам"""
        if not self.anchors:
            return

        r = self.rect()
        w, h = r.width(), r.height()

        self.anchors[self.ANCHOR_TOP].setPos(w / 2, 0)
        self.anchors[self.ANCHOR_BOTTOM].setPos(w / 2, h)
        self.anchors[self.ANCHOR_LEFT].setPos(0, h / 2)
        self.anchors[self.ANCHOR_RIGHT].setPos(w, h / 2)

    def update_content(self):
        """Пересчитывает размеры и положение текста"""
        n_attrs = len(self.attributes) if self.attributes else 1
        n_methods = len(self.methods) if self.methods else 1

        new_height = 35 + (n_attrs * 18) + 10 + (n_methods * 18)
        new_height = max(100, new_height)
        width = self.rect().width()

        self.setRect(0, 0, width, new_height)
        self.header_bg.setRect(0, 0, width, 30)

        self.header_text.setPlainText(self.name)
        tw = self.header_text.boundingRect().width()
        self.header_text.setPos((width - tw) / 2, 5)

        self.attrs_text.setPlainText("\n".join(self.attributes) if self.attributes else "")
        self.attrs_text.setPos(5, 35)

        attr_h = self.attrs_text.boundingRect().height()
        self.methods_text.setPlainText("\n".join(self.methods) if self.methods else "")
        self.methods_text.setPos(5, 35 + attr_h + 5)

        self._update_anchor_positions()

    def get_anchor_point(self, anchor_name: str) -> QPointF:
        """Возвращает позицию точки в координатах сцены"""
        if anchor_name in self.anchors:
            return self.anchors[anchor_name].scenePos()
        return self.scenePos()

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.GraphicsItemChange.ItemPositionHasChanged:
            self.signals.position_changed.emit(self)
        return super().itemChange(change, value)

    def setSelected(self, selected):
        super().setSelected(selected)
        pen_color = QColor("#DC143C") if selected else QColor("#4169E1")
        self.setPen(QPen(pen_color, 3 if selected else 2))

        for a in self.anchors.values():
            a.setVisible(selected)

        self.signals.selected_changed.emit(self, selected)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "x": self.pos().x(),
            "y": self.pos().y(),
            "attributes": self.attributes,
            "methods": self.methods
        }


class ConnectionSignals(QObject):
    """Сигналы для линии связи"""
    selected_changed = pyqtSignal(object, bool)
    about_to_delete = pyqtSignal(object)


class ArrowHead(QGraphicsPolygonItem):
    """Базовый класс для наконечников стрелок"""

    def __init__(self, direction: QPointF, connection_type: ConnectionType):
        super().__init__()
        self.connection_type = connection_type
        self.direction = direction
        self._update_shape()

    def _update_shape(self):
        """Обновляет форму наконечника в зависимости от направления и типа"""
        # Нормализуем направление
        length = math.sqrt(self.direction.x() ** 2 + self.direction.y() ** 2)
        if length == 0:
            return

        dx = self.direction.x() / length
        dy = self.direction.y() / length

        # Перпендикулярное направление
        px = -dy
        py = dx

        size = 12  # размер наконечника

        if self.connection_type == ConnectionType.INHERITANCE:
            # Треугольник (полый)
            points = [
                QPointF(size, 0),
                QPointF(0, -size * 0.6),
                QPointF(0, size * 0.6)
            ]
            polygon = QPolygonF(points)
            self.setPolygon(polygon)
            self.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            self.setPen(QPen(QColor("#666666"), 2))

        elif self.connection_type == ConnectionType.COMPOSITION:
            # Закрашенный ромб
            points = [
                QPointF(size, 0),
                QPointF(size / 2, -size * 0.6),
                QPointF(0, 0),
                QPointF(size / 2, size * 0.6)
            ]
            polygon = QPolygonF(points)
            self.setPolygon(polygon)
            self.setBrush(QBrush(QColor("#333333")))
            self.setPen(QPen(QColor("#666666"), 1.5))

        elif self.connection_type == ConnectionType.AGGREGATION:
            # Пустой ромб
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
        else:
            # Ассоциация - стрелка с закрашенным треугольником
            points = [
                QPointF(size, 0),
                QPointF(0, -size * 0.6),
                QPointF(0, size * 0.6)
            ]
            polygon = QPolygonF(points)
            self.setPolygon(polygon)
            self.setBrush(QBrush(QColor("#666666")))
            self.setPen(QPen(QColor("#666666"), 1.5))

    def set_direction(self, direction: QPointF):
        """Устанавливает направление и обновляет поворот"""
        self.direction = direction
        angle = math.degrees(math.atan2(direction.y(), direction.x()))
        self.setRotation(angle)
        self._update_shape()


class ConnectionLine(QGraphicsLineItem):
    """Линия связи с наконечником"""

    def __init__(self, source: UMLCard, target: UMLCard,
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

        self.setPen(QPen(QColor("#666666"), 2))
        self.setFlags(QGraphicsLineItem.GraphicsItemFlag.ItemIsSelectable)

        # Создаем наконечник
        self.arrow_head = ArrowHead(QPointF(1, 0), connection_type)
        self.arrow_head.setParentItem(self)

        self.update_position()

        source.signals.position_changed.connect(self.update_position)
        target.signals.position_changed.connect(self.update_position)
        source.signals.about_to_delete.connect(self.on_card_deleted)
        target.signals.about_to_delete.connect(self.on_card_deleted)

    def update_position(self):
        """Обновляет позицию линии и наконечника"""
        if self.source is None or self.target is None:
            return

        p1 = self.source.get_anchor_point(self.source_anchor)
        p2 = self.target.get_anchor_point(self.target_anchor)

        # Получаем направление для наконечника (от источника к цели)
        direction = p2 - p1

        # Если линия слишком короткая, не рисуем наконечник
        if direction.manhattanLength() < 20:
            self.arrow_head.setVisible(False)
            self.setLine(QLineF(p1, p2))
            return

        self.arrow_head.setVisible(True)

        # Для разных типов связей наконечник может быть на разном конце
        if self.connection_type in [ConnectionType.INHERITANCE,
                                    ConnectionType.COMPOSITION,
                                    ConnectionType.AGGREGATION]:
            # Наследование и композиция - наконечник у цели (родительский класс)
            arrow_direction = direction
            # Отодвигаем линию, чтобы наконечник не перекрывался с карточкой
            line_length = math.sqrt(direction.x()**2 + direction.y()**2)
            if line_length > 12:
                offset = 12
                p2_adjusted = p2 - (direction / line_length) * offset
                self.setLine(QLineF(p1, p2_adjusted))
                self.arrow_head.set_direction(arrow_direction)
                self.arrow_head.setPos(p2)
            else:
                self.setLine(QLineF(p1, p2))
                self.arrow_head.setPos(p2)
        else:
            # Ассоциация - наконечник на обоих концах? обычно только на целевом
            arrow_direction = direction
            line_length = math.sqrt(direction.x()**2 + direction.y()**2)
            if line_length > 12:
                offset = 12
                p2_adjusted = p2 - (direction / line_length) * offset
                self.setLine(QLineF(p1, p2_adjusted))
                self.arrow_head.set_direction(arrow_direction)
                self.arrow_head.setPos(p2)
            else:
                self.setLine(QLineF(p1, p2))
                self.arrow_head.setPos(p2)

    def set_connection_type(self, connection_type: ConnectionType):
        """Изменяет тип связи"""
        self.connection_type = connection_type
        self.arrow_head.connection_type = connection_type
        self.arrow_head._update_shape()
        self.update_position()

    def set_selected(self, selected):
        """Устанавливает выделение"""
        self._is_selected = selected
        color = QColor("#DC143C") if selected else QColor("#666666")
        width = 3 if selected else 2
        self.setPen(QPen(color, width))
        self.arrow_head.setPen(QPen(color, width))
        self.signals.selected_changed.emit(self, selected)

    def is_selected(self):
        return self._is_selected

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.set_selected(not self._is_selected)
        event.accept()

    def on_card_deleted(self, card):
        if self.source == card or self.target == card:
            self.signals.about_to_delete.emit(self)

    def to_dict(self):
        return {
            "id": self.id,
            "source_id": self.source.id,
            "target_id": self.target.id,
            "source_anchor": self.source_anchor,
            "target_anchor": self.target_anchor,
            "connection_type": self.connection_type.value
        }


class ConnectionPropertiesDialog(QDialog):
    """Диалог для выбора типа связи"""

    def __init__(self, connection: ConnectionLine, parent=None):
        super().__init__(parent)
        self.connection = connection
        self.setWindowTitle("Connection Properties")
        self.setMinimumWidth(300)

        layout = QVBoxLayout()

        # Тип связи
        layout.addWidget(QLabel("Connection Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItem("Association", ConnectionType.ASSOCIATION.value)
        self.type_combo.addItem("Inheritance", ConnectionType.INHERITANCE.value)
        self.type_combo.addItem("Composition", ConnectionType.COMPOSITION.value)
        self.type_combo.addItem("Aggregation", ConnectionType.AGGREGATION.value)

        # Устанавливаем текущее значение
        current_type = connection.connection_type.value
        index = self.type_combo.findData(current_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)

        layout.addWidget(self.type_combo)

        # Кнопки OK/Cancel
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_connection_type(self) -> ConnectionType:
        """Возвращает выбранный тип связи"""
        value = self.type_combo.currentData()
        for ct in ConnectionType:
            if ct.value == value:
                return ct
        return ConnectionType.ASSOCIATION


class DiagramScene(QGraphicsScene):
    """Сцена диаграммы"""

    connection_created = pyqtSignal(object)
    connection_deleted = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundBrush(QBrush(QColor("#fafafa")))
        self.setSceneRect(-5000, -5000, 10000, 10000)
        self.temp_line = None
        self.connection_source = None
        self.source_anchor = None
        self.connection_active = False

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        pen = QPen(QColor("#e0e0e0"), 0.5)
        painter.setPen(pen)

        left = int(rect.left()) - (int(rect.left()) % 50)
        top = int(rect.top()) - (int(rect.top()) % 50)
        right = int(rect.right())
        bottom = int(rect.bottom())

        x = left
        while x <= right:
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
            x += 50

        y = top
        while y <= bottom:
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)
            y += 50

    def start_connection(self, card: UMLCard, anchor: str):
        self.connection_source = card
        self.source_anchor = anchor
        self.connection_active = True

        pos = card.get_anchor_point(anchor)
        self.temp_line = QGraphicsLineItem(pos.x(), pos.y(), pos.x(), pos.y())
        self.temp_line.setPen(QPen(QColor("#FF6B6B"), 2, Qt.PenStyle.DashLine))
        self.temp_line.setZValue(999)
        self.addItem(self.temp_line)

    def update_temp_line(self, pos: QPointF):
        if self.connection_active and self.temp_line and self.connection_source:
            source_pos = self.connection_source.get_anchor_point(self.source_anchor)
            self.temp_line.setLine(QLineF(source_pos, pos))

    def finish_connection(self, target_card: UMLCard, target_anchor: str):
        if not self.connection_active:
            return None

        if self.temp_line:
            self.removeItem(self.temp_line)
            self.temp_line = None

        line = None
        if self.connection_source and target_card and self.connection_source != target_card:
            # Показываем диалог выбора типа связи
            temp_line = ConnectionLine(self.connection_source, target_card,
                                       self.source_anchor, target_anchor,
                                       ConnectionType.ASSOCIATION)
            dialog = ConnectionPropertiesDialog(temp_line)
            if dialog.exec():
                conn_type = dialog.get_connection_type()
                line = ConnectionLine(self.connection_source, target_card,
                                      self.source_anchor, target_anchor,
                                      conn_type)
                self.addItem(line)
                self.connection_created.emit(line)

        self.connection_source = None
        self.source_anchor = None
        self.connection_active = False

        return line

    def cancel_connection(self):
        if self.temp_line:
            self.removeItem(self.temp_line)
            self.temp_line = None
        self.connection_source = None
        self.source_anchor = None
        self.connection_active = False

    def delete_connection(self, connection):
        if connection in self.items():
            self.removeItem(connection)
            self.connection_deleted.emit(connection)

    def clear_all_connections(self):
        connections = [item for item in self.items() if isinstance(item, ConnectionLine)]
        for conn in connections:
            self.removeItem(conn)
            self.connection_deleted.emit(conn)


class DiagramView(QGraphicsView):
    """Вид диаграммы"""

    def __init__(self, scene: DiagramScene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.scale_factor = 1.15

    def wheelEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                self.scale(self.scale_factor, self.scale_factor)
            else:
                self.scale(1 / self.scale_factor, 1 / self.scale_factor)
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.pos())
            if item is None:
                self.scene().clearSelection()
                for line in self.find_connections():
                    line.set_selected(False)
                self.scene().cancel_connection()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        scene = self.scene()
        if hasattr(scene, 'temp_line') and scene.temp_line:
            pos = self.mapToScene(event.pos())
            scene.update_temp_line(pos)
        super().mouseMoveEvent(event)

    def find_connections(self):
        connections = []
        for item in self.scene().items():
            if isinstance(item, ConnectionLine):
                connections.append(item)
        return connections


class EditClassDialog(QDialog):
    """Диалог редактирования класса"""

    def __init__(self, card: UMLCard, parent=None):
        super().__init__(parent)
        self.card = card
        self.setWindowTitle(f"Edit Class: {card.name}")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Class Name:"))
        self.name_edit = QLineEdit(card.name)
        layout.addWidget(self.name_edit)

        layout.addWidget(QLabel("Attributes:"))
        self.attrs_list = QListWidget()
        for attr in card.attributes:
            self.attrs_list.addItem(attr)
        layout.addWidget(self.attrs_list)

        attr_buttons = QHBoxLayout()
        add_attr = QPushButton("Add")
        add_attr.clicked.connect(self.add_attribute)
        remove_attr = QPushButton("Remove")
        remove_attr.clicked.connect(self.remove_attribute)
        attr_buttons.addWidget(add_attr)
        attr_buttons.addWidget(remove_attr)
        layout.addLayout(attr_buttons)

        layout.addWidget(QLabel("Methods:"))
        self.methods_list = QListWidget()
        for method in card.methods:
            self.methods_list.addItem(method)
        layout.addWidget(self.methods_list)

        method_buttons = QHBoxLayout()
        add_method = QPushButton("Add")
        add_method.clicked.connect(self.add_method)
        remove_method = QPushButton("Remove")
        remove_method.clicked.connect(self.remove_method)
        method_buttons.addWidget(add_method)
        method_buttons.addWidget(remove_method)
        layout.addLayout(method_buttons)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def add_attribute(self):
        text, ok = QInputDialog.getText(self, "Add Attribute",
                                        "Attribute (e.g., +name: str):")
        if ok and text:
            self.attrs_list.addItem(text)

    def remove_attribute(self):
        current = self.attrs_list.currentRow()
        if current >= 0:
            self.attrs_list.takeItem(current)

    def add_method(self):
        text, ok = QInputDialog.getText(self, "Add Method",
                                        "Method (e.g., +getName(): str):")
        if ok and text:
            self.methods_list.addItem(text)

    def remove_method(self):
        current = self.methods_list.currentRow()
        if current >= 0:
            self.methods_list.takeItem(current)

    def get_data(self):
        attributes = [self.attrs_list.item(i).text()
                      for i in range(self.attrs_list.count())]
        methods = [self.methods_list.item(i).text()
                   for i in range(self.methods_list.count())]
        return self.name_edit.text(), attributes, methods


class DiagramEditor(QMainWindow):
    """Главное окно редактора"""

    def __init__(self):
        super().__init__()
        self.cards = []
        self.connections = []

        self.setWindowTitle("LogicCraft UML Architect")
        self.setGeometry(100, 100, 1200, 800)

        self._create_ui()

    def _create_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)

        toolbar = self.addToolBar("Main")
        toolbar.setMovable(False)

        add_action = QAction("➕ Add Class", self)
        add_action.triggered.connect(self.add_card)
        toolbar.addAction(add_action)

        save_action = QAction("💾 Save", self)
        save_action.triggered.connect(self.save_diagram)
        toolbar.addAction(save_action)

        load_action = QAction("📂 Load", self)
        load_action.triggered.connect(self.load_diagram)
        toolbar.addAction(load_action)

        clear_action = QAction("🗑️ Clear All", self)
        clear_action.triggered.connect(self.clear_all)
        toolbar.addAction(clear_action)

        edit_action = QAction("✏️ Edit Selected", self)
        edit_action.triggered.connect(self.edit_selected_card)
        toolbar.addAction(edit_action)

        delete_action = QAction("❌ Delete Selected", self)
        delete_action.triggered.connect(self.delete_selected)
        toolbar.addAction(delete_action)

        edit_conn_action = QAction("🔗 Edit Connection", self)
        edit_conn_action.triggered.connect(self.edit_selected_connection)
        toolbar.addAction(edit_conn_action)

        toolbar.addSeparator()

        self.status_label = QLabel("Cards: 0 | Connections: 0 | Drag red dots to create connections")
        toolbar.addWidget(self.status_label)

        self.scene = DiagramScene()
        self.view = DiagramView(self.scene)
        layout.addWidget(self.view)

        self.scene.connection_created.connect(self.add_connection)
        self.scene.connection_deleted.connect(self.remove_connection)

    def add_card(self):
        x = random.randint(50, 500)
        y = random.randint(50, 400)

        card = UMLCard(f"Class{len(self.cards)}", x, y)
        card.signals.selected_changed.connect(self.on_card_selected)
        card.signals.position_changed.connect(self.on_card_moved)
        card.signals.anchor_moved.connect(self.on_anchor_drag_start)
        card.signals.about_to_delete.connect(self.on_card_deleted)

        self.scene.addItem(card)
        self.cards.append(card)
        self.update_status()

    def delete_selected(self):
        selected_cards = [c for c in self.cards if c.isSelected()]
        for card in selected_cards:
            self.delete_card(card)

        selected_connections = [c for c in self.connections if c.is_selected()]
        for conn in selected_connections:
            self.scene.delete_connection(conn)

        self.update_status()

    def delete_card(self, card: UMLCard):
        if card in self.cards:
            card.signals.about_to_delete.emit(card)
            self.scene.removeItem(card)
            self.cards.remove(card)

    def on_card_deleted(self, card: UMLCard):
        connections_to_delete = [c for c in self.connections
                                 if c.source == card or c.target == card]
        for conn in connections_to_delete:
            self.scene.delete_connection(conn)

    def add_connection(self, connection: ConnectionLine):
        self.connections.append(connection)
        connection.signals.about_to_delete.connect(self.remove_connection)
        self.update_status()

    def remove_connection(self, connection: ConnectionLine):
        if connection in self.connections:
            self.connections.remove(connection)
            self.update_status()

    def on_anchor_drag_start(self, card: UMLCard, anchor: str):
        self.scene.start_connection(card, anchor)

    def edit_selected_card(self):
        selected = [c for c in self.cards if c.isSelected()]
        if selected:
            card = selected[0]
            dialog = EditClassDialog(card, self)
            if dialog.exec():
                name, attributes, methods = dialog.get_data()
                card.name = name
                card.attributes = attributes
                card.methods = methods
                card.update_content()

    def edit_selected_connection(self):
        """Редактирует выделенную связь"""
        selected = [c for c in self.connections if c.is_selected()]
        if selected:
            connection = selected[0]
            dialog = ConnectionPropertiesDialog(connection, self)
            if dialog.exec():
                new_type = dialog.get_connection_type()
                connection.set_connection_type(new_type)
                connection.update_position()

    def on_card_selected(self, card: UMLCard, selected: bool):
        if selected:
            for c in self.cards:
                if c != card and c.isSelected():
                    c.setSelected(False)
            for conn in self.connections:
                if conn.is_selected():
                    conn.set_selected(False)

    def on_card_moved(self, card: UMLCard):
        for conn in self.connections:
            if conn.source == card or conn.target == card:
                conn.update_position()

    def save_diagram(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Diagram", "", "JSON Files (*.json)"
        )
        if filepath:
            try:
                data = {
                    "cards": [c.to_dict() for c in self.cards],
                    "connections": [c.to_dict() for c in self.connections]
                }
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                QMessageBox.information(self, "Success", f"Saved to {filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save: {e}")

    def load_diagram(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Load Diagram", "", "JSON Files (*.json)"
        )
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.clear_all()

                card_map = {}
                for card_data in data["cards"]:
                    card = UMLCard(
                        card_data["name"],
                        card_data["x"],
                        card_data["y"],
                        attributes=card_data["attributes"],
                        methods=card_data["methods"],
                        card_id=card_data["id"]
                    )
                    card.signals.selected_changed.connect(self.on_card_selected)
                    card.signals.position_changed.connect(self.on_card_moved)
                    card.signals.anchor_moved.connect(self.on_anchor_drag_start)
                    card.signals.about_to_delete.connect(self.on_card_deleted)
                    self.scene.addItem(card)
                    self.cards.append(card)
                    card_map[card.id] = card

                for conn_data in data["connections"]:
                    source = card_map.get(conn_data["source_id"])
                    target = card_map.get(conn_data["target_id"])
                    if source and target:
                        conn_type = ConnectionType(conn_data.get("connection_type", "association"))
                        conn = ConnectionLine(
                            source, target,
                            conn_data.get("source_anchor", "right"),
                            conn_data.get("target_anchor", "left"),
                            conn_type,
                            conn_data["id"]
                        )
                        self.scene.addItem(conn)
                        self.connections.append(conn)
                        conn.signals.about_to_delete.connect(self.remove_connection)

                self.update_status()
                QMessageBox.information(self, "Success", "Diagram loaded")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load: {e}")

    def clear_all(self):
        self.scene.clear_all_connections()
        self.scene.clear()
        self.cards.clear()
        self.connections.clear()
        self.update_status()

    def update_status(self):
        self.status_label.setText(f"Cards: {len(self.cards)} | Connections: {len(self.connections)} | Drag red dots to create connections")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    editor = DiagramEditor()
    editor.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()