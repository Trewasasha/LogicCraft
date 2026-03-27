import sys
import json
import random
from pathlib import Path
from typing import List, Dict, Any, Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QToolBar, QFileDialog, QMessageBox, QGraphicsView,
    QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem,
    QGraphicsItem, QInputDialog, QListWidget, QListWidgetItem,
    QDialog, QDialogButtonBox, QLineEdit, QApplication,
    QGraphicsEllipseItem
)
from PyQt6.QtCore import Qt, QPointF, QRectF, QLineF, QObject, pyqtSignal
from PyQt6.QtGui import (
    QBrush, QColor, QPen, QFont, QPainter, QAction
)
import uuid


class CardSignals(QObject):
    """Сигналы для карточки"""
    selected_changed = pyqtSignal(object, bool)
    position_changed = pyqtSignal(object)
    anchor_moved = pyqtSignal(object, str)  # карточка, позиция
    about_to_delete = pyqtSignal(object)  # сигнал перед удалением


class AnchorPoint(QGraphicsEllipseItem):
    """Точка привязки на карточке"""

    def __init__(self, parent_card, anchor_name: str, size: int = 8):
        # Создаем круг с центром в (0,0) - позиция будет установлена через setPos
        super().__init__(-size/2, -size/2, size, size)
        self.parent_card = parent_card
        self.anchor_name = anchor_name
        self.size = size

        # Настройка внешнего вида
        self.setBrush(QBrush(QColor("#FF6B6B")))
        self.setPen(QPen(QColor("#FFFFFF"), 1.5))
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setAcceptHoverEvents(True)
        self.setZValue(1000)  # Высокий z-index
        self._drag_start = None

    def hoverEnterEvent(self, event):
        """При наведении мыши меняем цвет"""
        self.setBrush(QBrush(QColor("#FF4444")))
        self.setScale(1.2)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """При уходе мыши возвращаем цвет"""
        self.setBrush(QBrush(QColor("#FF6B6B")))
        self.setScale(1.0)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        """Начало перетаскивания точки привязки"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = self.scenePos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

            self.parent_card.signals.anchor_moved.emit(self.parent_card, self.anchor_name)
            event.accept()

    def mouseMoveEvent(self, event):
        """Перетаскивание точки привязки"""
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_start:
            # Отправляем сигнал с текущей позицией мыши
            current_pos = self.mapToScene(event.pos())
            # Обновляем временную линию через сцену
            scene = self.scene()
            if scene and hasattr(scene, 'update_temp_line'):
                scene.update_temp_line(current_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Завершение перетаскивания с улучшенным поиском точки"""
        if event.button() == Qt.MouseButton.LeftButton and self._drag_start:
            self.setCursor(Qt.CursorShape.ArrowCursor)

            # 1. Получаем позицию отпускания в координатах сцены
            end_pos = self.mapToScene(event.pos())


            search_rect = QRectF(end_pos.x() - 5, end_pos.y() - 5, 10, 10)
            items = self.scene().items(search_rect)

            target_anchor = None
            for item in items:
                # Проверяем, что это точка привязки и она не принадлежит текущей карточке
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
    """Карточка класса UML с исправленной логикой координат и привязок"""

    # Константы для ключей словаря anchors
    ANCHOR_TOP = "top"
    ANCHOR_BOTTOM = "bottom"
    ANCHOR_LEFT = "left"
    ANCHOR_RIGHT = "right"

    def __init__(self, name: str, x: float = 0, y: float = 0,
                 width: float = 160, height: float = 100,
                 attributes: list = None, methods: list = None,
                 card_id: str = None):
        # Рисуем прямоугольник от локального нуля (0, 0)
        super().__init__(0, 0, width, height)
        # Устанавливаем позицию самого графического объекта на сцене
        self.setPos(x, y)

        self.id = card_id or str(uuid.uuid4())
        self.name = name
        self.attributes = attributes or []
        self.methods = methods or []

        # 1. Инициализируем словарь и настройки
        self.anchors = {}
        self._anchor_size = 8
        self.signals = CardSignals()

        # 2. Настраиваем внешний вид
        self.setBrush(QBrush(QColor("#f5f5dc")))
        self.setPen(QPen(QColor("#4169E1"), 2))
        self.setFlags(
            QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        # 3. Создаем дочерние элементы (текст, шапку)
        self._create_elements()

        # 4. СНАЧАЛА создаем объекты точек (якорей)
        self._create_anchors()

        # 5. И ТОЛЬКО ПОТОМ обновляем контент (который расставит точки по местам)
        self.update_content()

    def _create_elements(self):
        """Создание визуальных частей карточки"""
        # Шапка
        self.header_bg = QGraphicsRectItem(0, 0, self.rect().width(), 30, self)
        self.header_bg.setBrush(QBrush(QColor("#4169E1")))
        self.header_bg.setPen(QPen(Qt.PenStyle.NoPen))

        self.header_text = QGraphicsTextItem(self.name, self)
        self.header_text.setDefaultTextColor(QColor("white"))
        self.header_text.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        self.attrs_text = QGraphicsTextItem("", self)
        self.attrs_text.setFont(QFont("Menlo", 9))

        self.methods_text = QGraphicsTextItem("", self)
        self.methods_text.setFont(QFont("Menlo", 9))

    def _create_anchors(self):
        """Создает объекты точек и помещает их в словарь"""
        for name in [self.ANCHOR_TOP, self.ANCHOR_BOTTOM, self.ANCHOR_LEFT, self.ANCHOR_RIGHT]:
            anchor = AnchorPoint(self, name, self._anchor_size)
            anchor.setParentItem(self)
            self.anchors[name] = anchor

    def _update_anchor_positions(self):
        """Расставляет точки по границам текущего прямоугольника"""
        if not self.anchors:
            return

        r = self.rect()
        w, h = r.width(), r.height()

        # Координаты задаются относительно (0,0) карточки
        self.anchors[self.ANCHOR_TOP].setPos(w / 2, 0)
        self.anchors[self.ANCHOR_BOTTOM].setPos(w / 2, h)
        self.anchors[self.ANCHOR_LEFT].setPos(0, h / 2)
        self.anchors[self.ANCHOR_RIGHT].setPos(w, h / 2)

    def update_content(self):
        """Пересчитывает размеры и положение текста"""
        # Расчет высоты на основе количества строк
        n_attrs = len(self.attributes) if self.attributes else 1
        n_methods = len(self.methods) if self.methods else 1

        new_height = 35 + (n_attrs * 18) + 10 + (n_methods * 18)
        new_height = max(100, new_height)
        width = self.rect().width()

        # Обновляем геометрию
        self.setRect(0, 0, width, new_height)
        self.header_bg.setRect(0, 0, width, 30)

        # Центрируем текст заголовка
        self.header_text.setPlainText(self.name)
        tw = self.header_text.boundingRect().width()
        self.header_text.setPos((width - tw) / 2, 5)

        # Текст атрибутов
        self.attrs_text.setPlainText("\n".join(self.attributes) if self.attributes else "")
        self.attrs_text.setPos(5, 35)

        # Текст методов
        attr_h = self.attrs_text.boundingRect().height()
        self.methods_text.setPlainText("\n".join(self.methods) if self.methods else "")
        self.methods_text.setPos(5, 35 + attr_h + 5)

        # Обновляем позиции точек привязки под новый размер
        self._update_anchor_positions()

    def get_anchor_point(self, anchor_name: str) -> QPointF:
        """Возвращает позицию точки в координатах сцены"""
        if anchor_name in self.anchors:
            return self.anchors[anchor_name].scenePos()
        return self.scenePos()

    def itemChange(self, change, value):
        """Событие перемещения карточки"""
        if change == QGraphicsRectItem.GraphicsItemChange.ItemPositionHasChanged:
            self.signals.position_changed.emit(self)
        return super().itemChange(change, value)

    def setSelected(self, selected):
        """Показ/скрытие точек при выделении"""
        super().setSelected(selected)
        # Подсвечиваем рамку
        pen_color = QColor("#DC143C") if selected else QColor("#4169E1")
        self.setPen(QPen(pen_color, 3 if selected else 2))

        # Показываем точки
        for a in self.anchors.values():
            a.setVisible(selected)

        self.signals.selected_changed.emit(self, selected)

    def to_dict(self):
        """Для сохранения в JSON"""
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


class ConnectionLine(QGraphicsLineItem):
    """Линия связи с точками привязки"""

    def __init__(self, source: UMLCard, target: UMLCard,
                 source_anchor: str = "right", target_anchor: str = "left",
                 connection_id: str = None):
        super().__init__()

        self.id = connection_id or str(uuid.uuid4())
        self.source = source
        self.target = target
        self.source_anchor = source_anchor
        self.target_anchor = target_anchor
        self._is_selected = False

        # Создаем объект для сигналов
        self.signals = ConnectionSignals()

        self.setPen(QPen(QColor("#666666"), 2))
        self.setFlags(QGraphicsLineItem.GraphicsItemFlag.ItemIsSelectable)

        self.update_position()

        # Подключаем сигналы движения карточек
        source.signals.position_changed.connect(self.update_position)
        target.signals.position_changed.connect(self.update_position)

        # Подключаем сигналы удаления карточек
        source.signals.about_to_delete.connect(self.on_card_deleted)
        target.signals.about_to_delete.connect(self.on_card_deleted)

    def update_position(self):
        """Обновляет позицию линии"""
        # Проверяем, существуют ли еще карточки
        if self.source is None or self.target is None:
            return
        p1 = self.source.get_anchor_point(self.source_anchor)
        p2 = self.target.get_anchor_point(self.target_anchor)
        self.setLine(QLineF(p1, p2))

    def set_selected(self, selected):
        """Устанавливает выделение"""
        self._is_selected = selected
        color = QColor("#DC143C") if selected else QColor("#666666")
        width = 3 if selected else 2
        self.setPen(QPen(color, width))
        self.signals.selected_changed.emit(self, selected)

    def is_selected(self):
        return self._is_selected

    def mousePressEvent(self, event):
        """Обработка нажатия"""
        super().mousePressEvent(event)
        self.set_selected(not self._is_selected)
        event.accept()

    def on_card_deleted(self, card):
        """Обработка удаления карточки"""
        if self.source == card or self.target == card:
            self.signals.about_to_delete.emit(self)

    def to_dict(self):
        """Сериализация"""
        return {
            "id": self.id,
            "source_id": self.source.id,
            "target_id": self.target.id,
            "source_anchor": self.source_anchor,
            "target_anchor": self.target_anchor
        }


class DiagramScene(QGraphicsScene):
    """Сцена диаграммы"""

    connection_created = pyqtSignal(object)  # Сигнал о создании связи
    connection_deleted = pyqtSignal(object)  # Сигнал об удалении связи

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundBrush(QBrush(QColor("#fafafa")))
        self.setSceneRect(-5000, -5000, 10000, 10000)
        self.temp_line = None
        self.connection_source = None
        self.source_anchor = None
        self.connection_active = False

    def drawBackground(self, painter, rect):
        """Рисует сетку на фоне"""
        super().drawBackground(painter, rect)

        # Рисуем сетку
        pen = QPen(QColor("#e0e0e0"), 0.5)
        painter.setPen(pen)

        left = int(rect.left()) - (int(rect.left()) % 50)
        top = int(rect.top()) - (int(rect.top()) % 50)
        right = int(rect.right())
        bottom = int(rect.bottom())

        # Рисуем вертикальные линии
        x = left
        while x <= right:
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
            x += 50

        # Рисуем горизонтальные линии
        y = top
        while y <= bottom:
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)
            y += 50

    def start_connection(self, card: UMLCard, anchor: str):
        """Начинает создание связи"""
        self.connection_source = card
        self.source_anchor = anchor
        self.connection_active = True

        # Создаем временную линию
        pos = card.get_anchor_point(anchor)
        self.temp_line = QGraphicsLineItem(pos.x(), pos.y(), pos.x(), pos.y())
        self.temp_line.setPen(QPen(QColor("#FF6B6B"), 2, Qt.PenStyle.DashLine))
        self.temp_line.setZValue(999)
        self.addItem(self.temp_line)

    def update_temp_line(self, pos: QPointF):
        """Обновляет временную линию"""
        if self.connection_active and self.temp_line and self.connection_source:
            source_pos = self.connection_source.get_anchor_point(self.source_anchor)
            self.temp_line.setLine(QLineF(source_pos, pos))

    def finish_connection(self, target_card: UMLCard, target_anchor: str):
        """Завершает создание связи"""
        if not self.connection_active:
            return None

        # Удаляем временную линию
        if self.temp_line:
            self.removeItem(self.temp_line)
            self.temp_line = None

        line = None
        if self.connection_source and target_card and self.connection_source != target_card:
            # Создаем постоянную линию
            line = ConnectionLine(self.connection_source, target_card,
                                  self.source_anchor, target_anchor)
            self.addItem(line)
            # Испускаем сигнал о создании связи
            self.connection_created.emit(line)

        # Сбрасываем состояние
        self.connection_source = None
        self.source_anchor = None
        self.connection_active = False

        return line

    def cancel_connection(self):
        """Отменяет создание связи"""
        if self.temp_line:
            self.removeItem(self.temp_line)
            self.temp_line = None
        self.connection_source = None
        self.source_anchor = None
        self.connection_active = False

    def delete_connection(self, connection):
        """Удаляет связь"""
        if connection in self.items():
            self.removeItem(connection)
            self.connection_deleted.emit(connection)

    def clear_all_connections(self):
        """Удаляет все связи"""
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
        """Масштабирование колесиком"""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                self.scale(self.scale_factor, self.scale_factor)
            else:
                self.scale(1 / self.scale_factor, 1 / self.scale_factor)
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        """Снятие выделения при клике на пустое место"""
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.pos())
            if item is None:
                self.scene().clearSelection()
                # Снимаем выделение со всех линий
                for line in self.find_connections():
                    line.set_selected(False)
                self.scene().cancel_connection()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Обновление временной линии при перетаскивании"""
        scene = self.scene()
        if hasattr(scene, 'temp_line') and scene.temp_line:
            pos = self.mapToScene(event.pos())
            scene.update_temp_line(pos)
        super().mouseMoveEvent(event)

    def find_connections(self):
        """Находит все линии"""
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

        # Имя класса
        layout.addWidget(QLabel("Class Name:"))
        self.name_edit = QLineEdit(card.name)
        layout.addWidget(self.name_edit)

        # Атрибуты
        layout.addWidget(QLabel("Attributes:"))
        self.attrs_list = QListWidget()
        for attr in card.attributes:
            self.attrs_list.addItem(attr)
        layout.addWidget(self.attrs_list)

        # Кнопки для атрибутов
        attr_buttons = QHBoxLayout()
        add_attr = QPushButton("Add")
        add_attr.clicked.connect(self.add_attribute)
        remove_attr = QPushButton("Remove")
        remove_attr.clicked.connect(self.remove_attribute)
        attr_buttons.addWidget(add_attr)
        attr_buttons.addWidget(remove_attr)
        layout.addLayout(attr_buttons)

        # Методы
        layout.addWidget(QLabel("Methods:"))
        self.methods_list = QListWidget()
        for method in card.methods:
            self.methods_list.addItem(method)
        layout.addWidget(self.methods_list)

        # Кнопки для методов
        method_buttons = QHBoxLayout()
        add_method = QPushButton("Add")
        add_method.clicked.connect(self.add_method)
        remove_method = QPushButton("Remove")
        remove_method.clicked.connect(self.remove_method)
        method_buttons.addWidget(add_method)
        method_buttons.addWidget(remove_method)
        layout.addLayout(method_buttons)

        # Кнопки OK/Cancel
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
        """Создает интерфейс"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)

        # Тулбар
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

        toolbar.addSeparator()

        self.status_label = QLabel("Cards: 0 | Connections: 0 | Drag red dots to create connections")
        toolbar.addWidget(self.status_label)

        # Сцена и вид
        self.scene = DiagramScene()
        self.view = DiagramView(self.scene)
        layout.addWidget(self.view)

        # Подключаем сигналы сцены
        self.scene.connection_created.connect(self.add_connection)
        self.scene.connection_deleted.connect(self.remove_connection)

    def add_card(self):
        """Добавляет карточку"""
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
        """Удаляет выделенные элементы"""
        # Удаляем выделенные карточки
        selected_cards = [c for c in self.cards if c.isSelected()]
        for card in selected_cards:
            self.delete_card(card)

        # Удаляем выделенные связи
        selected_connections = [c for c in self.connections if c.is_selected()]
        for conn in selected_connections:
            self.scene.delete_connection(conn)

        self.update_status()

    def delete_card(self, card: UMLCard):
        """Удаляет карточку"""
        if card in self.cards:
            # Испускаем сигнал о удалении для связей
            card.signals.about_to_delete.emit(card)
            # Удаляем из сцены
            self.scene.removeItem(card)
            self.cards.remove(card)

    def on_card_deleted(self, card: UMLCard):
        """Обработка сигнала удаления карточки"""
        # Удаляем все связи, связанные с этой карточкой
        connections_to_delete = [c for c in self.connections
                                 if c.source == card or c.target == card]
        for conn in connections_to_delete:
            self.scene.delete_connection(conn)

    def add_connection(self, connection: ConnectionLine):
        """Добавляет связь"""
        self.connections.append(connection)
        connection.signals.about_to_delete.connect(self.remove_connection)
        self.update_status()

    def remove_connection(self, connection: ConnectionLine):
        """Удаляет связь"""
        if connection in self.connections:
            self.connections.remove(connection)
            self.update_status()

    def on_anchor_drag_start(self, card: UMLCard, anchor: str):
        """Начало перетаскивания точки привязки"""
        self.scene.start_connection(card, anchor)

    def edit_selected_card(self):
        """Редактирует выбранную карточку"""
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

    def on_card_selected(self, card: UMLCard, selected: bool):
        """Обработка выбора карточки"""
        if selected:
            for c in self.cards:
                if c != card and c.isSelected():
                    c.setSelected(False)
            # Снимаем выделение со всех связей
            for conn in self.connections:
                if conn.is_selected():
                    conn.set_selected(False)

    def on_card_moved(self, card: UMLCard):
        """Обработка движения карточки"""
        for conn in self.connections:
            if conn.source == card or conn.target == card:
                conn.update_position()

    def save_diagram(self):
        """Сохраняет диаграмму"""
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
        """Загружает диаграмму"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Load Diagram", "", "JSON Files (*.json)"
        )
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.clear_all()

                # Восстанавливаем карточки
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

                # Восстанавливаем связи
                for conn_data in data["connections"]:
                    source = card_map.get(conn_data["source_id"])
                    target = card_map.get(conn_data["target_id"])
                    if source and target:
                        conn = ConnectionLine(
                            source, target,
                            conn_data.get("source_anchor", "right"),
                            conn_data.get("target_anchor", "left"),
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
        """Очищает всё"""
        self.scene.clear_all_connections()
        self.scene.clear()
        self.cards.clear()
        self.connections.clear()
        self.update_status()

    def update_status(self):
        """Обновляет статус"""
        self.status_label.setText(f"Cards: {len(self.cards)} | Connections: {len(self.connections)} | Drag red dots to create connections")


def main():
    """Запуск приложения"""
    app = QApplication(sys.argv)

    # Устанавливаем стиль
    app.setStyle("Fusion")

    # Создаем и показываем главное окно
    editor = DiagramEditor()
    editor.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()