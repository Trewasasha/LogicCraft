"""Виджет актёра Use Case диаграммы — человечек"""
import uuid
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PyQt6.QtCore import Qt, QPointF, QRectF, QObject, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont

from .anchor_point import AnchorPoint
from ..theme import CardStyle, AnchorStyle


class ActorSignals(QObject):
    position_changed = pyqtSignal()
    move_finished = pyqtSignal(str, float, float)
    delete_requested = pyqtSignal(str)


class ActorWidget(QGraphicsItem):
    """Актёр — стилизованный человечек с именем"""

    # Размеры фигуры
    HEAD_R = 12       # радиус головы
    BODY_H = 28       # высота туловища
    ARM_W = 22        # полуширина рук
    LEG_H = 22        # высота ног
    LABEL_GAP = 6     # отступ от ног до текста

    # Полная высота фигуры (без текста)
    FIGURE_H = HEAD_R * 2 + BODY_H + LEG_H
    FIGURE_W = ARM_W * 2

    ANCHOR_SIZE = 8

    def __init__(self, name: str, x: float = 0, y: float = 0,
                 actor_id: str = None):
        super().__init__()
        self.id = actor_id or str(uuid.uuid4())
        self.name = name
        self.setPos(x, y)
        self._is_selected = False

        self.signals = ActorSignals()

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)

        # Текстовая метка
        self._label = QGraphicsTextItem(self)
        self._label.setFont(QFont("Inter", 10, QFont.Weight.Medium))
        self._label.setDefaultTextColor(QColor("#1F1F1F"))
        self._label.setPlainText(name)
        self._update_label_pos()

        # Точки привязки
        self.anchors: dict[str, AnchorPoint] = {}
        self._create_anchors()

    # ── Геометрия ──────────────────────────────────────────────────────────────

    def boundingRect(self) -> QRectF:
        lw = self._label.boundingRect().width()
        w = max(self.FIGURE_W + 20, lw + 10)
        label_h = self._label.boundingRect().height()
        h = self.FIGURE_H + self.LABEL_GAP + label_h + 10
        return QRectF(-w / 2, -10, w, h)

    def _figure_top(self) -> float:
        """Y-координата верхней точки головы (в локальных координатах)"""
        return 0.0

    def _figure_center_x(self) -> float:
        return 0.0

    # ── Отрисовка ──────────────────────────────────────────────────────────────

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = QColor("#7C3AED") if self._is_selected else QColor("#4B5563")
        pen = QPen(color, 2.0)
        painter.setPen(pen)
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))

        cx = self._figure_center_x()
        top = self._figure_top()

        # Голова
        head_cx = cx
        head_cy = top + self.HEAD_R
        painter.drawEllipse(QPointF(head_cx, head_cy), self.HEAD_R, self.HEAD_R)

        # Туловище
        body_top = top + self.HEAD_R * 2
        body_bottom = body_top + self.BODY_H
        painter.drawLine(QPointF(cx, body_top), QPointF(cx, body_bottom))

        # Руки
        arm_y = body_top + self.BODY_H * 0.35
        painter.drawLine(QPointF(cx - self.ARM_W, arm_y), QPointF(cx + self.ARM_W, arm_y))

        # Ноги
        painter.drawLine(QPointF(cx, body_bottom), QPointF(cx - self.ARM_W * 0.8, body_bottom + self.LEG_H))
        painter.drawLine(QPointF(cx, body_bottom), QPointF(cx + self.ARM_W * 0.8, body_bottom + self.LEG_H))

        # Выделение — пунктирный прямоугольник
        if self._is_selected:
            sel_pen = QPen(QColor("#7C3AED"), 1.5, Qt.PenStyle.DashLine)
            painter.setPen(sel_pen)
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            painter.drawRoundedRect(self.boundingRect().adjusted(2, 2, -2, -2), 6, 6)

    # ── Вспомогательные ────────────────────────────────────────────────────────

    def _update_label_pos(self):
        lw = self._label.boundingRect().width()
        label_y = self.FIGURE_H + self.LABEL_GAP
        self._label.setPos(-lw / 2, label_y)

    def _create_anchors(self):
        for name in ("top", "bottom", "left", "right"):
            anchor = AnchorPoint(self, name, self.ANCHOR_SIZE)
            anchor.setParentItem(self)
            anchor.setVisible(False)
            self.anchors[name] = anchor
        self._update_anchor_positions()

    def _update_anchor_positions(self):
        cx = self._figure_center_x()
        top = self._figure_top()
        fig_h = self.FIGURE_H
        fig_w = self.FIGURE_W

        self.anchors["top"].setPos(cx, top)
        self.anchors["bottom"].setPos(cx, top + fig_h)
        self.anchors["left"].setPos(cx - fig_w / 2, top + fig_h / 2)
        self.anchors["right"].setPos(cx + fig_w / 2, top + fig_h / 2)

    def get_anchor_point(self, anchor_name: str) -> QPointF:
        if anchor_name in self.anchors:
            return self.anchors[anchor_name].scenePos()
        return self.scenePos()

    def update_name(self, name: str):
        self.name = name
        self._label.setPlainText(name)
        self._update_label_pos()
        self.update()

    # ── Qt события ─────────────────────────────────────────────────────────────

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.signals.position_changed.emit()
            scene = self.scene()
            if scene and hasattr(scene, 'on_card_moved'):
                scene.on_card_moved(self)
        return super().itemChange(change, value)

    def setSelected(self, selected: bool):
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
        """Двойной клик — переименование"""
        from PyQt6.QtWidgets import QInputDialog
        scene = self.scene()
        view = scene.views()[0] if scene and scene.views() else None
        parent = view.window() if view else None
        new_name, ok = QInputDialog.getText(
            parent, "Переименовать актёра", "Имя:", text=self.name
        )
        if ok and new_name.strip():
            self.update_name(new_name.strip())
            # Уведомляем контроллер
            if scene and hasattr(scene, 'actor_renamed'):
                scene.actor_renamed.emit(self.id, new_name.strip())
        event.accept()

    def contextMenuEvent(self, event):
        from PyQt6.QtWidgets import QMenu
        menu = QMenu()
        rename_action = menu.addAction("✏  Переименовать")
        menu.addSeparator()
        delete_action = menu.addAction("🗑  Удалить актёра")

        action = menu.exec(event.screenPos())
        if action == rename_action:
            self.mouseDoubleClickEvent(event)
        elif action == delete_action:
            self.signals.delete_requested.emit(self.id)
