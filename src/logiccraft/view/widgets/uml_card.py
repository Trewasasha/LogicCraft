"""Карточка UML класса"""
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem
from PyQt6.QtCore import Qt, QPointF, pyqtSignal, QObject
from PyQt6.QtGui import QBrush, QColor, QPen, QFont
import uuid
from typing import List, Optional

from .anchor_point import AnchorPoint


class CardSignals(QObject):
    """Сигналы для карточки"""
    position_changed = pyqtSignal()
    about_to_delete = pyqtSignal(object)


class UMLCard(QGraphicsRectItem):
    """Карточка класса UML с поддержкой drag & drop"""

    # Константы для точек привязки
    ANCHOR_TOP = "top"
    ANCHOR_BOTTOM = "bottom"
    ANCHOR_LEFT = "left"
    ANCHOR_RIGHT = "right"

    def __init__(self, name: str, x: float = 0, y: float = 0,
                 width: float = 160, height: float = 100,
                 attributes: List[str] = None, methods: List[str] = None,
                 card_id: str = None):
        super().__init__(0, 0, width, height)
        self.setPos(x, y)

        self.id = card_id or str(uuid.uuid4())
        self.name = name
        self.attributes = attributes or []
        self.methods = methods or []

        self.anchors = {}
        self._anchor_size = 8
        self._is_selected = False

        # Добавляем сигналы
        self.signals = CardSignals()

        # Настройка внешнего вида
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
        """Создает визуальные элементы карточки"""
        # Фон заголовка
        self.header_bg = QGraphicsRectItem(0, 0, self.rect().width(), 30, self)
        self.header_bg.setBrush(QBrush(QColor("#4169E1")))
        self.header_bg.setPen(QPen(Qt.PenStyle.NoPen))

        # Текст заголовка
        self.header_text = QGraphicsTextItem(self.name, self)
        self.header_text.setDefaultTextColor(QColor("white"))
        self.header_text.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        # Секция атрибутов
        self.attrs_text = QGraphicsTextItem("", self)
        self.attrs_text.setFont(QFont("Menlo", 9))
        self.attrs_text.setDefaultTextColor(QColor("#2c3e50"))

        # Секция методов
        self.methods_text = QGraphicsTextItem("", self)
        self.methods_text.setFont(QFont("Menlo", 9))
        self.methods_text.setDefaultTextColor(QColor("#27ae60"))

        # Разделители
        self.divider1 = QGraphicsRectItem(0, 32, self.rect().width(), 1, self)
        self.divider1.setBrush(QBrush(QColor("#4169E1")))
        self.divider1.setPen(QPen(Qt.PenStyle.NoPen))

        self.divider2 = QGraphicsRectItem(0, 0, self.rect().width(), 1, self)
        self.divider2.setBrush(QBrush(QColor("#4169E1")))
        self.divider2.setPen(QPen(Qt.PenStyle.NoPen))

    def _create_anchors(self):
        """Создает точки привязки"""
        for name in [self.ANCHOR_TOP, self.ANCHOR_BOTTOM,
                     self.ANCHOR_LEFT, self.ANCHOR_RIGHT]:
            anchor = AnchorPoint(self, name, self._anchor_size)
            anchor.setParentItem(self)
            self.anchors[name] = anchor

    def _update_anchor_positions(self):
        """Обновляет позиции точек привязки"""
        if not self.anchors:
            return

        r = self.rect()
        w, h = r.width(), r.height()

        self.anchors[self.ANCHOR_TOP].setPos(w / 2, 0)
        self.anchors[self.ANCHOR_BOTTOM].setPos(w / 2, h)
        self.anchors[self.ANCHOR_LEFT].setPos(0, h / 2)
        self.anchors[self.ANCHOR_RIGHT].setPos(w, h / 2)

    def update_content(self):
        """Обновляет содержимое карточки"""
        # Вычисляем новую высоту
        n_attrs = len(self.attributes) if self.attributes else 1
        n_methods = len(self.methods) if self.methods else 1

        new_height = 35 + (n_attrs * 18) + 10 + (n_methods * 18)
        new_height = max(100, new_height)
        width = self.rect().width()

        self.setRect(0, 0, width, new_height)
        self.header_bg.setRect(0, 0, width, 30)

        # Обновляем текст заголовка
        self.header_text.setPlainText(self.name)
        tw = self.header_text.boundingRect().width()
        self.header_text.setPos((width - tw) / 2, 5)

        # Обновляем атрибуты
        attr_text = "\n".join(self.attributes) if self.attributes else ""
        self.attrs_text.setPlainText(attr_text)
        self.attrs_text.setPos(5, 35)

        # Обновляем методы
        attr_h = self.attrs_text.boundingRect().height()
        method_text = "\n".join(self.methods) if self.methods else ""
        self.methods_text.setPlainText(method_text)
        self.methods_text.setPos(5, 35 + attr_h + 5)

        # Обновляем разделители
        if self.methods:
            self.divider2.setRect(0, 35 + attr_h + 2, width, 1)
            self.divider2.show()
        else:
            self.divider2.hide()

        self._update_anchor_positions()

    def get_anchor_point(self, anchor_name: str) -> QPointF:
        """Возвращает позицию точки привязки в координатах сцены"""
        if anchor_name in self.anchors:
            return self.anchors[anchor_name].scenePos()
        return self.scenePos()

    def itemChange(self, change, value):
        """Обработка изменений позиции"""
        if change == QGraphicsRectItem.GraphicsItemChange.ItemPositionHasChanged:
            # Эмитим сигнал об изменении позиции
            self.signals.position_changed.emit()
            # Уведомляем сцену об изменении позиции
            scene = self.scene()
            if scene and hasattr(scene, 'on_card_moved'):
                scene.on_card_moved(self)
        return super().itemChange(change, value)

    def setSelected(self, selected):
        """Устанавливает состояние выделения"""
        super().setSelected(selected)
        self._is_selected = selected

        # Меняем цвет рамки
        pen_color = QColor("#DC143C") if selected else QColor("#4169E1")
        self.setPen(QPen(pen_color, 3 if selected else 2))

        # Показываем/скрываем точки привязки
        for anchor in self.anchors.values():
            anchor.setVisible(selected)

    def isSelected(self) -> bool:
        """Возвращает состояние выделения"""
        return self._is_selected

    def to_dict(self) -> dict:
        """Сериализация в словарь"""
        return {
            "id": self.id,
            "name": self.name,
            "x": self.pos().x(),
            "y": self.pos().y(),
            "attributes": self.attributes,
            "methods": self.methods
        }