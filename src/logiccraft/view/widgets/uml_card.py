"""Карточка UML класса"""
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem
from PyQt6.QtCore import Qt, QPointF, pyqtSignal, QObject, QRectF
from PyQt6.QtGui import QBrush, QColor, QPen, QFont, QPainter, QPainterPath
import uuid
from typing import List, Optional

from .anchor_point import AnchorPoint
from ..theme import CardStyle


class CardSignals(QObject):
    """Сигналы для карточки"""
    position_changed = pyqtSignal()
    move_finished = pyqtSignal(str, float, float)  # card_id, x, y
    edit_requested = pyqtSignal(str)  # card_id
    delete_requested = pyqtSignal(str)  # card_id
    about_to_delete = pyqtSignal(object)


class UMLCard(QGraphicsRectItem):
    """Карточка класса UML с поддержкой drag & drop"""

    # Константы для точек привязки
    ANCHOR_TOP = "top"
    ANCHOR_BOTTOM = "bottom"
    ANCHOR_LEFT = "left"
    ANCHOR_RIGHT = "right"

    HEADER_HEIGHT = 36
    RADIUS = 12

    def __init__(self, name: str, x: float = 0, y: float = 0,
                 width: float = 180, height: float = 100,
                 attributes: List[str] = None, methods: List[str] = None,
                 card_id: str = None, node_type=None):
        super().__init__(0, 0, width, height)
        self.setPos(x, y)

        self.id = card_id or str(uuid.uuid4())
        self.name = name
        self.attributes = attributes or []
        self.methods = methods or []
        self.node_type = node_type or "class"

        self.anchors = {}
        self._anchor_size = 8
        self._is_selected = False

        self.signals = CardSignals()

        # Прозрачный фон базового rect — рисуем сами в paint()
        self.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setFlags(
            QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)  # Включаем hover события

        self._create_elements()
        self._create_anchors()
        self.update_content()

    def paint(self, painter: QPainter, option, widget=None):
        """Кастомная отрисовка с скруглёнными углами"""
        r = self.rect()
        radius = self.RADIUS
        h = self.HEADER_HEIGHT

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Тень
        shadow_color = QColor(124, 58, 237, 25)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(shadow_color))
        painter.drawRoundedRect(r.adjusted(2, 3, 2, 3), radius, radius)

        # Основной фон карточки (белый)
        border_color = QColor(CardStyle.SELECTED_BORDER) if self._is_selected else QColor(CardStyle.BORDER)
        border_width = CardStyle.SELECTED_BORDER_WIDTH if self._is_selected else CardStyle.BORDER_WIDTH
        painter.setPen(QPen(border_color, border_width))
        painter.setBrush(QBrush(QColor(CardStyle.BACKGROUND)))
        painter.drawRoundedRect(r, radius, radius)

        # Определяем цвет заголовка по типу узла
        node_type = getattr(self, 'node_type', 'class')
        if hasattr(node_type, 'value'):
            node_type = node_type.value

        if node_type == 'interface':
            header_color = QColor("#9B72F5")  # Светло-фиолетовый для интерфейсов
        elif node_type == 'enum':
            header_color = QColor("#10B981")  # Зелёный для enum
        elif node_type == 'abstract_class':
            header_color = QColor("#8B5CF6")  # Средне-фиолетовый для абстрактных
        else:
            header_color = QColor(CardStyle.HEADER_BG)  # Стандартный фиолетовый

        # Заголовок — цветной прямоугольник с скруглением только сверху
        header_path = QPainterPath()
        header_path.moveTo(r.left() + radius, r.top())
        header_path.lineTo(r.right() - radius, r.top())
        header_path.arcTo(r.right() - radius * 2, r.top(), radius * 2, radius * 2, 90, -90)
        header_path.lineTo(r.right(), r.top() + h)
        header_path.lineTo(r.left(), r.top() + h)
        header_path.arcTo(r.left(), r.top(), radius * 2, radius * 2, 180, -90)
        header_path.closeSubpath()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(header_color))
        painter.drawPath(header_path)

    def _create_elements(self):
        """Создает визуальные элементы карточки"""
        # Иконка + текст заголовка
        self.header_text = QGraphicsTextItem(self)
        self.header_text.setDefaultTextColor(QColor(CardStyle.HEADER_TEXT))
        self.header_text.setFont(CardStyle.HEADER_FONT)

        # Секция атрибутов
        self.attrs_text = QGraphicsTextItem("", self)
        self.attrs_text.setFont(CardStyle.ATTRS_FONT)
        self.attrs_text.setDefaultTextColor(QColor(CardStyle.ATTRS_TEXT))

        # Секция методов
        self.methods_text = QGraphicsTextItem("", self)
        self.methods_text.setFont(CardStyle.METHODS_FONT)
        self.methods_text.setDefaultTextColor(QColor(CardStyle.METHODS_TEXT))

        # Разделитель между атрибутами и методами
        self.divider2 = QGraphicsRectItem(0, 0, self.rect().width(), 1, self)
        self.divider2.setBrush(QBrush(QColor(CardStyle.DIVIDER)))
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
        n_attrs = len(self.attributes) if self.attributes else 1
        n_methods = len(self.methods) if self.methods else 1

        new_height = self.HEADER_HEIGHT + 8 + (n_attrs * 20) + 10 + (n_methods * 20) + 8
        new_height = max(110, new_height)
        width = self.rect().width()

        self.setRect(0, 0, width, new_height)

        # Определяем тип узла
        node_type = getattr(self, 'node_type', 'class')
        if hasattr(node_type, 'value'):
            node_type = node_type.value

        # Визуальное отличие по типу
        if node_type == 'interface':
            stereotype = '«interface»'
            icon = '◇'
            name_style = 'font-style:italic; font-weight:bold;'
        elif node_type == 'enum':
            stereotype = '«enumeration»'
            icon = '≡'
            name_style = 'font-weight:bold;'
        elif node_type == 'abstract_class':
            stereotype = '«abstract»'
            icon = '△'
            name_style = 'font-style:italic; font-weight:bold;'
        else:
            stereotype = ''
            icon = '⬡'
            name_style = 'font-weight:bold;'

        # Формируем HTML заголовка
        if stereotype:
            header_html = (
                f'<div style="text-align:center;">'
                f'<div style="font-size:9px; color:rgba(255,255,255,200); margin-bottom:2px;">'
                f'{stereotype}</div>'
                f'<div style="font-size:13px; {name_style}">'
                f'{icon} {self.name}</div>'
                f'</div>'
            )
        else:
            header_html = (
                f'<div style="text-align:center; font-size:13px; {name_style}">'
                f'{icon} {self.name}</div>'
            )

        self.header_text.setHtml(header_html)
        tw = self.header_text.boundingRect().width()
        th = self.header_text.boundingRect().height()
        self.header_text.setPos((width - tw) / 2, (self.HEADER_HEIGHT - th) / 2)

        # Атрибуты
        attr_text = "\n".join(self.attributes) if self.attributes else ""
        self.attrs_text.setPlainText(attr_text)
        self.attrs_text.setPos(12, self.HEADER_HEIGHT + 8)

        # Разделитель
        attr_h = self.attrs_text.boundingRect().height() if self.attributes else 0
        divider_y = self.HEADER_HEIGHT + 8 + attr_h + 4

        if self.methods:
            self.divider2.setRect(12, divider_y, width - 24, 1)
            self.divider2.show()
        else:
            self.divider2.hide()

        # Методы
        method_text = "\n".join(self.methods) if self.methods else ""
        self.methods_text.setPlainText(method_text)
        self.methods_text.setPos(12, divider_y + 6)

        self._update_anchor_positions()
        self.update()

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
        for anchor in self.anchors.values():
            anchor.setVisible(selected)
        self.update()

    def isSelected(self) -> bool:
        return self._is_selected

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.signals.move_finished.emit(self.id, self.pos().x(), self.pos().y())

    def mouseDoubleClickEvent(self, event):
        """Обработка двойного клика - открывает диалог редактирования"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.signals.edit_requested.emit(self.id)
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def hoverEnterEvent(self, event):
        """При наведении курсора показываем подсказку"""
        self.setToolTip("Двойной клик для редактирования")
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """При уходе курсора"""
        super().hoverLeaveEvent(event)

    def contextMenuEvent(self, event):
        """Контекстное меню по правому клику"""
        from PyQt6.QtWidgets import QMenu

        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #E5E0F8;
                border-radius: 12px;
                padding: 6px 0px;
                min-width: 200px;
            }
            QMenu::item {
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 500;
                color: #1F1F1F;
                border-radius: 6px;
                margin: 1px 6px;
            }
            QMenu::item:selected {
                background-color: #F3EEFF;
                color: #7C3AED;
            }
            QMenu::separator {
                height: 1px;
                background-color: #E5E0F8;
                margin: 4px 12px;
            }
        """)

        edit_action = menu.addAction("✏  Редактировать класс")
        menu.addSeparator()
        conn_action = menu.addAction("🔗  Изменить связи")
        menu.addSeparator()
        delete_action = menu.addAction("🗑  Удалить класс")
        # Красный цвет для удаления
        delete_action.setData("delete")

        action = menu.exec(event.screenPos())

        if action == edit_action:
            self.signals.edit_requested.emit(self.id)
        elif action == delete_action:
            self.signals.delete_requested.emit(self.id)

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