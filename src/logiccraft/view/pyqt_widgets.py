"""PyQt6 виджеты для UML редактора"""

from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QGraphicsTextItem, QGraphicsLineItem, QGraphicsItem,
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QToolBar, QMainWindow, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal, QLineF
from PyQt6.QtGui import (
    QBrush, QColor, QPen, QFont, QPainterPath,
    QPainter, QLinearGradient
)
import uuid
import json


class UMLCard(QGraphicsRectItem):
    """Карточка класса UML с поддержкой drag & drop"""

    selected_changed = pyqtSignal(object, bool)
    position_changed = pyqtSignal(object)

    def __init__(self, name: str, x: float = 0, y: float = 0,
                 width: float = 160, height: float = 100,
                 attributes: list = None, methods: list = None,
                 card_id: str = None):
        super().__init__(x, y, width, height)

        self.id = card_id or str(uuid.uuid4())
        self.name = name
        self.attributes = attributes or []
        self.methods = methods or []
        self._is_selected = False

        # Настройка внешнего вида
        self.setBrush(QBrush(QColor("#f5f5dc")))
        self.setPen(QPen(QColor("#4169E1"), 2))
        self.setFlags(
            QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        # Создаем заголовок
        self._create_header()

        # Создаем секции атрибутов и методов
        self._create_sections()

        # Устанавливаем начальные позиции
        self.update_content()

    def _create_header(self):
        """Создает заголовок карточки"""
        rect = self.rect()

        # Фон заголовка
        self.header_bg = QGraphicsRectItem(rect.x(), rect.y(),
                                           rect.width(), 30, self)
        self.header_bg.setBrush(QBrush(QColor("#4169E1")))
        self.header_bg.setPen(QPen(Qt.PenStyle.NoPen))

        # Текст заголовка
        self.header_text = QGraphicsTextItem(self.name, self)
        self.header_text.setDefaultTextColor(QColor("white"))
        self.header_text.setFont(QFont("Arial", 10, QFont.Weight.Bold))

    def _create_sections(self):
        """Создает секции атрибутов и методов"""
        rect = self.rect()
        self.attr_items = []
        self.method_items = []

        # Атрибуты
        self.attrs_text = QGraphicsTextItem("", self)
        self.attrs_text.setFont(QFont("Courier", 9))
        self.attrs_text.setPos(rect.x() + 5, rect.y() + 35)

        # Методы
        self.methods_text = QGraphicsTextItem("", self)
        self.methods_text.setFont(QFont("Courier", 9))

        # Разделители
        self.divider1 = QGraphicsRectItem(rect.x(), rect.y() + 32,
                                          rect.width(), 1, self)
        self.divider1.setBrush(QBrush(QColor("#4169E1")))
        self.divider1.setPen(QPen(Qt.PenStyle.NoPen))

        self.divider2 = QGraphicsRectItem(rect.x(), 0, rect.width(), 1, self)
        self.divider2.setBrush(QBrush(QColor("#4169E1")))
        self.divider2.setPen(QPen(Qt.PenStyle.NoPen))

    def update_content(self):
        """Обновляет содержимое карточки"""
        rect = self.rect()

        # Обновляем заголовок
        self.header_text.setPlainText(self.name)
        text_width = self.header_text.boundingRect().width()
        self.header_text.setPos(
            rect.x() + rect.width() / 2 - text_width / 2,
            rect.y() + 7
        )

        # Обновляем атрибуты
        attr_text = "\n".join(self.attributes) if self.attributes else ""
        self.attrs_text.setPlainText(attr_text)

        # Обновляем методы
        method_y = rect.y() + 35 + (len(self.attributes) * 15) + 10
        self.methods_text.setPos(rect.x() + 5, method_y)
        method_text = "\n".join(self.methods) if self.methods else ""
        self.methods_text.setPlainText(method_text)

        # Обновляем разделители
        if self.methods:
            self.divider2.setRect(rect.x(), method_y - 5, rect.width(), 1)
            self.divider2.show()
        else:
            self.divider2.hide()

        # Обновляем размер карточки
        total_height = 35 + (len(self.attributes) * 15) + 10 + (len(self.methods) * 15)
        total_height = max(100, total_height)
        self.setRect(rect.x(), rect.y(), rect.width(), total_height)

        # Обновляем фон заголовка
        self.header_bg.setRect(rect.x(), rect.y(), rect.width(), 30)

    def itemChange(self, change, value):
        """Обработка изменений позиции"""
        if change == QGraphicsRectItem.GraphicsItemChange.ItemPositionChange:
            self.position_changed.emit(self)
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        """Обработка нажатия мыши"""
        super().mousePressEvent(event)
        self.setSelected(not self.isSelected())

    def setSelected(self, selected):
        """Устанавливает состояние выделения"""
        super().setSelected(selected)
        self._is_selected = selected
        color = QColor("#DC143C") if selected else QColor("#4169E1")
        width = 3 if selected else 2
        self.setPen(QPen(color, width))
        self.selected_changed.emit(self, selected)

    def isSelected(self):
        """Возвращает состояние выделения"""
        return self._is_selected

    def get_center(self):
        """Возвращает центр карточки"""
        rect = self.rect()
        return QPointF(rect.x() + rect.width() / 2,
                       rect.y() + rect.height() / 2)

    def get_anchor_point(self, position):
        """Возвращает точку привязки"""
        rect = self.rect()
        if position == "top":
            return QPointF(rect.x() + rect.width() / 2, rect.y())
        elif position == "bottom":
            return QPointF(rect.x() + rect.width() / 2, rect.y() + rect.height())
        elif position == "left":
            return QPointF(rect.x(), rect.y() + rect.height() / 2)
        elif position == "right":
            return QPointF(rect.x() + rect.width(), rect.y() + rect.height() / 2)
        return self.get_center()

    def to_dict(self):
        """Сериализация в словарь"""
        return {
            "id": self.id,
            "name": self.name,
            "x": self.x(),
            "y": self.y(),
            "attributes": self.attributes,
            "methods": self.methods
        }


class ConnectionLine(QGraphicsLineItem):
    """Линия связи между карточками"""

    selected_changed = pyqtSignal(object, bool)

    def __init__(self, source: UMLCard, target: UMLCard,
                 connection_id: str = None):
        super().__init__()

        self.id = connection_id or str(uuid.uuid4())
        self.source = source
        self.target = target
        self.source_pos = "right"
        self.target_pos = "left"
        self._is_selected = False

        # Настройка внешнего вида
        self.setPen(QPen(QColor("#666666"), 2))
        self.setFlags(QGraphicsLineItem.GraphicsItemFlag.ItemIsSelectable)

        # Обновляем позицию
        self.update_position()

        # Подключаем сигналы движения карточек
        source.position_changed.connect(self.update_position)
        target.position_changed.connect(self.update_position)

    def update_position(self):
        """Обновляет позицию линии"""
        p1 = self.source.get_anchor_point(self.source_pos)
        p2 = self.target.get_anchor_point(self.target_pos)
        self.setLine(QLineF(p1, p2))

    def set_selected(self, selected):
        """Устанавливает состояние выделения"""
        self._is_selected = selected
        color = QColor("#DC143C") if selected else QColor("#666666")
        width = 3 if selected else 2
        self.setPen(QPen(color, width))
        self.selected_changed.emit(self, selected)

    def is_selected(self):
        """Возвращает состояние выделения"""
        return self._is_selected

    def mousePressEvent(self, event):
        """Обработка нажатия мыши"""
        super().mousePressEvent(event)
        self.set_selected(not self._is_selected)
        event.accept()

    def to_dict(self):
        """Сериализация в словарь"""
        return {
            "id": self.id,
            "source_id": self.source.id,
            "target_id": self.target.id,
            "source_pos": self.source_pos,
            "target_pos": self.target_pos
        }


class UMLGraphicsScene(QGraphicsScene):
    """Сцена для отображения UML диаграммы"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundBrush(QBrush(QColor("#fafafa")))
        self.setSceneRect(-5000, -5000, 10000, 10000)


class UMLGraphicsView(QGraphicsView):
    """Вид для отображения сцены с поддержкой масштабирования"""

    def __init__(self, scene: UMLGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Настройки масштабирования
        self.scale_factor = 1.15

    def wheelEvent(self, event):
        """Обработка колесика мыши для масштабирования"""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                self.scale(self.scale_factor, self.scale_factor)
            else:
                self.scale(1 / self.scale_factor, 1 / self.scale_factor)
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        """Обработка нажатия мыши для снятия выделения"""
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.pos())
            if item is None:
                self.scene().clearSelection()
                for line in self.find_connections():
                    line.set_selected(False)
        super().mousePressEvent(event)

    def find_connections(self):
        """Находит все линии связи на сцене"""
        connections = []
        for item in self.scene().items():
            if isinstance(item, ConnectionLine):
                connections.append(item)
        return connections