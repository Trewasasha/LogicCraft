"""Сцена диаграммы"""
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsLineItem
from PyQt6.QtCore import Qt, QPointF, QLineF, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QPen, QPainter

from ..theme import SceneStyle

class DiagramScene(QGraphicsScene):
    """Сцена для отображения UML диаграммы с сеткой и поддержкой связей"""

    connection_ready = pyqtSignal(str, str, str, str)
    card_moved = pyqtSignal(str, float, float)
    actor_renamed = pyqtSignal(str, str)      # actor_id, new_name
    scenario_renamed = pyqtSignal(str, str)   # scenario_id, new_name

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
        
        # Показываем точки привязки у всех потенциальных целей
        self._show_all_anchors(except_card=source_card)

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
        
        # Скрываем точки привязки у всех элементов
        self._hide_all_anchors()

    def cancel_connection(self):
        """Отмена тяги"""
        if self.temp_line:
            self.removeItem(self.temp_line)
            self.temp_line = None
        self.connection_source = None
        self.source_anchor = None
        self.connection_active = False
        
        # Скрываем точки привязки у всех элементов
        self._hide_all_anchors()

    def on_card_moved(self, card):
        """Snap to grid + групповое перемещение (UMLCard, ActorWidget, ScenarioWidget)"""
        from ..widgets.uml_card import UMLCard
        from ..widgets.actor_widget import ActorWidget
        from ..widgets.scenario_widget import ScenarioWidget
        grid = SceneStyle.GRID_STEP

        # Если выделено несколько — двигаем все вместе
        selected_items = [
            item for item in self.selectedItems()
            if isinstance(item, (UMLCard, ActorWidget, ScenarioWidget))
        ]
        targets = selected_items if len(selected_items) > 1 else [card]

        for c in targets:
            x = round(c.pos().x() / grid) * grid
            y = round(c.pos().y() / grid) * grid
            if c.pos().x() != x or c.pos().y() != y:
                c.setPos(x, y)
            # card_moved используется только для UMLCard (контроллер обновляет модель)
            # UC-элементы обновляют модель через move_finished → update_uc_actor/scenario
            if isinstance(c, UMLCard):
                self.card_moved.emit(c.id, c.pos().x(), c.pos().y())

    def on_card_name_changed(self, card_id: str, old_name: str, new_name: str):
        """Обработка изменения имени карточки через inline редактирование"""
        # Эмитим сигнал для контроллера
        # Контроллер должен обновить модель
        pass  # Пока просто заглушка, логика в контроллере

    def highlight_related_cards(self, card_id: str, card_map: dict, connection_map: dict):
        """Подсветка связанных классов при выборе"""
        # Находим все связи для выбранной карточки
        related_cards = set()
        related_connections = []
        
        for conn_id, conn in connection_map.items():
            try:
                if conn.scene() is None:  # Объект удалён
                    continue
                if conn.source.id == card_id:
                    related_cards.add(conn.target.id)
                    related_connections.append(conn)
                elif conn.target.id == card_id:
                    related_cards.add(conn.source.id)
                    related_connections.append(conn)
            except (RuntimeError, AttributeError):
                # Объект был удалён или повреждён
                continue
        
        # Затемняем все карточки
        for cid, card in card_map.items():
            try:
                if card.scene() is None:  # Объект удалён
                    continue
                if cid == card_id:
                    # Выбранная карточка - оставляем как есть
                    card.setOpacity(1.0)
                elif cid in related_cards:
                    # Связанные карточки - полная яркость
                    card.setOpacity(1.0)
                else:
                    # Несвязанные карточки - затемняем
                    card.setOpacity(0.3)
            except RuntimeError:
                # Объект был удалён
                continue
        
        # Подсвечиваем связи
        for conn in connection_map.values():
            try:
                if conn.scene() is None:  # Объект удалён
                    continue
                if conn in related_connections:
                    conn.setOpacity(1.0)
                    # Делаем линию толще
                    pen = conn.pen()
                    pen.setWidth(3)
                    conn.setPen(pen)
                else:
                    conn.setOpacity(0.2)
            except RuntimeError:
                # Объект был удалён
                continue
    
    def clear_highlights(self, card_map: dict, connection_map: dict):
        """Снять подсветку со всех элементов"""
        for card in card_map.values():
            try:
                if card.scene() is not None:  # Проверяем, что объект ещё существует
                    card.setOpacity(1.0)
            except RuntimeError:
                # Объект был удалён
                pass
        
        for conn in connection_map.values():
            try:
                if conn.scene() is not None:  # Проверяем, что объект ещё существует
                    conn.setOpacity(1.0)
                    # Восстанавливаем обычную толщину линии
                    pen = conn.pen()
                    pen.setWidth(2)
                    conn.setPen(pen)
            except RuntimeError:
                # Объект был удалён
                pass
    
    def _show_all_anchors(self, except_card=None):
        """Показать точки привязки у всех элементов (кроме источника)"""
        from ..widgets.uml_card import UMLCard
        from ..widgets.actor_widget import ActorWidget
        from ..widgets.scenario_widget import ScenarioWidget
        
        for item in self.items():
            if isinstance(item, (UMLCard, ActorWidget, ScenarioWidget)):
                if item != except_card and hasattr(item, 'anchors'):
                    for anchor in item.anchors.values():
                        anchor.setVisible(True)
    
    def _hide_all_anchors(self):
        """Скрыть точки привязки у всех невыделенных элементов"""
        from ..widgets.uml_card import UMLCard
        from ..widgets.actor_widget import ActorWidget
        from ..widgets.scenario_widget import ScenarioWidget
        
        for item in self.items():
            if isinstance(item, (UMLCard, ActorWidget, ScenarioWidget)):
                if hasattr(item, 'anchors') and not item.isSelected():
                    for anchor in item.anchors.values():
                        anchor.setVisible(False)
