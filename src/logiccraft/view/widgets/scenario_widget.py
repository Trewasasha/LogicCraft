"""Виджет сценария Use Case диаграммы — овал"""
import uuid
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PyQt6.QtCore import Qt, QPointF, QRectF, QObject, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont

from .anchor_point import AnchorPoint


class ScenarioSignals(QObject):
    position_changed = pyqtSignal()
    move_finished = pyqtSignal(str, float, float)
    delete_requested = pyqtSignal(str)


class ScenarioWidget(QGraphicsItem):
    """Сценарий Use Case — овал с текстом внутри"""

    DEFAULT_W = 160
    DEFAULT_H = 60
    ANCHOR_SIZE = 8

    def __init__(self, name: str, x: float = 0, y: float = 0,
                 scenario_id: str = None,
                 width: float = None, height: float = None):
        super().__init__()
        self.id = scenario_id or str(uuid.uuid4())
        self.name = name
        self.setPos(x, y)
        self._is_selected = False
        self._w = width or self.DEFAULT_W
        self._h = height or self.DEFAULT_H

        self.signals = ScenarioSignals()

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)

        # Текстовая метка внутри овала
        self._label = QGraphicsTextItem(self)
        self._label.setFont(QFont("Inter", 10, QFont.Weight.Medium))
        self._label.setDefaultTextColor(QColor("#1F1F1F"))
        self._label.setTextWidth(self._w - 20)
        self._label.setPlainText(name)
        self._update_label_pos()

        # Точки привязки
        self.anchors: dict[str, AnchorPoint] = {}
        self._create_anchors()

    # ── Геометрия ──────────────────────────────────────────────────────────────

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self._w, self._h)

    # ── Отрисовка ──────────────────────────────────────────────────────────────

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Тень
        shadow_color = QColor(124, 58, 237, 20)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(shadow_color))
        painter.drawEllipse(QRectF(2, 3, self._w, self._h))

        # Фон овала
        bg_color = QColor("#F3EEFF") if self._is_selected else QColor("#FFFFFF")
        border_color = QColor("#7C3AED") if self._is_selected else QColor("#9B72F5")
        border_w = 2.0 if self._is_selected else 1.5

        painter.setPen(QPen(border_color, border_w))
        painter.setBrush(QBrush(bg_color))
        painter.drawEllipse(QRectF(0, 0, self._w, self._h))

    # ── Вспомогательные ────────────────────────────────────────────────────────

    def _update_label_pos(self):
        """Центрируем текст внутри овала"""
        self._label.setTextWidth(self._w - 20)
        lh = self._label.boundingRect().height()
        self._label.setPos(10, (self._h - lh) / 2)

    def _create_anchors(self):
        for name in ("top", "bottom", "left", "right"):
            anchor = AnchorPoint(self, name, self.ANCHOR_SIZE)
            anchor.setParentItem(self)
            anchor.setVisible(False)
            self.anchors[name] = anchor
        self._update_anchor_positions()

    def _update_anchor_positions(self):
        self.anchors["top"].setPos(self._w / 2, 0)
        self.anchors["bottom"].setPos(self._w / 2, self._h)
        self.anchors["left"].setPos(0, self._h / 2)
        self.anchors["right"].setPos(self._w, self._h / 2)

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
        # Не управляем видимостью anchors здесь - это делает сцена
        # для anchor in self.anchors.values():
        #     anchor.setVisible(selected)
        self.update()

    def isSelected(self) -> bool:
        return self._is_selected
    
    def hoverEnterEvent(self, event):
        """Показать точки привязки при наведении"""
        for anchor in self.anchors.values():
            anchor.setVisible(True)
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Скрыть точки привязки при уходе курсора (если не выделен)"""
        if not self._is_selected:
            for anchor in self.anchors.values():
                anchor.setVisible(False)
        super().hoverLeaveEvent(event)

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
            parent, "Переименовать сценарий", "Имя:", text=self.name
        )
        if ok and new_name.strip():
            self.update_name(new_name.strip())
            if scene and hasattr(scene, 'scenario_renamed'):
                scene.scenario_renamed.emit(self.id, new_name.strip())
        event.accept()

    def contextMenuEvent(self, event):
        from PyQt6.QtWidgets import QMenu, QInputDialog
        menu = QMenu()
        rename_action = menu.addAction("Переименовать")
        menu.addSeparator()
        delete_action = menu.addAction("Удалить сценарий")

        action = menu.exec(event.screenPos())
        if action == rename_action:
            scene = self.scene()
            view = scene.views()[0] if scene and scene.views() else None
            parent = view.window() if view else None
            new_name, ok = QInputDialog.getText(
                parent, "Переименовать сценарий", "Имя:", text=self.name
            )
            if ok and new_name.strip():
                self.update_name(new_name.strip())
                if scene and hasattr(scene, 'scenario_renamed'):
                    scene.scenario_renamed.emit(self.id, new_name.strip())
        elif action == delete_action:
            self.signals.delete_requested.emit(self.id)
