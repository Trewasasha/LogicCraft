"""
LogicCraft: UML Architect
Главный контроллер диаграммы - Полная сборка
"""
import logging
from PyQt6.QtCore import QObject, pyqtSignal
from typing import List, Dict, Optional, Any

from ..models.diagram import UMLDiagram, UMLNode, UMLConnection, NodeType
from ..models.diagram_manager import DiagramManager
from ..models.engine import DiagramEngine
from ..services.code_generator import CodeGenerator
from ..services.history_service import HistoryService

logger = logging.getLogger(__name__)

class DiagramController(QObject):
    """Контроллер, связывающий бизнес-логику (Manager) и интерфейс (View)"""

    # --- СИГНАЛЫ ---
    card_added = pyqtSignal(object)
    card_removed = pyqtSignal(str)
    card_updated = pyqtSignal(object)

    connection_added = pyqtSignal(object)
    connection_removed = pyqtSignal(str)
    connection_updated = pyqtSignal(str)

    diagram_cleared = pyqtSignal()
    diagram_loaded = pyqtSignal()

    status_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    undo_redo_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.manager = DiagramManager()
        self.engine = DiagramEngine()
        self.code_generator = CodeGenerator()

        # Инициализация истории (снимков состояния)
        self.history = HistoryService(initial_state=self.manager.diagram)

        # Маппинг для связи ID модели с объектами View
        self.card_map: Dict[str, Any] = {}
        self.connection_map: Dict[str, Any] = {}

        # Подключение внутренних сигналов истории
        self.history.state_restored.connect(self._on_state_restored)
        self.history.history_changed.connect(self._on_history_changed)

    # --- УПРАВЛЕНИЕ ИСТОРИЕЙ (Proxy) ---

    def undo(self) -> bool:
        return bool(self.history.undo())

    def redo(self) -> bool:
        return bool(self.history.redo())

    def can_undo(self) -> bool:
        return self.history.can_undo()

    def can_redo(self) -> bool:
        return self.history.can_redo()

    def _save_state(self):
        """Создает точку восстановления в HistoryService"""
        self.history.push_state(self.manager.diagram)

    # --- ОПЕРАЦИИ С КАРТОЧКАМИ ---

    def add_card(self, x: float, y: float, name: str = None, node_type: NodeType = NodeType.CLASS) -> Optional[UMLNode]:
        try:
            node = self.manager.add_node(x, y, name, node_type)
            self.card_added.emit(node)
            self._save_state()
            self.status_changed.emit(f"Класс {node.name} добавлен")
            return node
        except Exception as e:
            self.error_occurred.emit(f"Ошибка добавления: {e}")
            return None

    def update_card(self, card_id: str, name: str = None,
                    x: float = None, y: float = None,
                    attributes: List[str] = None,
                    methods: List[str] = None,
                    node_type=None) -> bool:
        """Обновление данных и позиции карточки"""
        try:
            prop_objs = [self._parse_attribute_string(a) for a in attributes] if attributes is not None else None
            method_objs = [self._parse_method_string(m) for m in methods] if methods is not None else None

            success = self.manager.update_node(
                card_id, name, x, y,
                properties=prop_objs,
                methods=method_objs,
                node_type=node_type
            )

            if success:
                node = self.manager.get_node_by_id(card_id)
                self.card_updated.emit(node)
                return True
            return False
        except Exception as e:
            logger.error(f"Update card error: {e}")
            return False

    def on_card_move_finished(self, card_id: str, x: float, y: float):
        """Вызывается по завершению перетаскивания (mouseRelease)"""
        if self.update_card(card_id, x=x, y=y):
            self._save_state()

    def edit_card(self, card_id: str, name: str,
                  attributes: List[str], methods: List[str],
                  node_type=None) -> bool:
        """Редактирование содержимого карточки с сохранением в историю"""
        kwargs = {}
        if node_type is not None:
            kwargs['node_type'] = node_type
        if self.update_card(card_id, name, attributes=attributes, methods=methods, **kwargs):
            self._save_state()
            return True
        return False

    def remove_card(self, card_id: str) -> bool:
        try:
            # Сначала удаляем все связи этого узла
            conns = self.manager.get_connections_for_node(card_id)
            for c in conns:
                self.manager.remove_connection(c.id)
                self.connection_removed.emit(c.id)

            if self.manager.remove_node(card_id):
                self.card_removed.emit(card_id)
                self._save_state()
                self.status_changed.emit("Класс удален")
                return True
            return False
        except Exception as e:
            self.error_occurred.emit(f"Ошибка удаления: {e}")
            return False

    # --- ОПЕРАЦИИ СО СВЯЗЯМИ ---

    def add_connection(self, source_id: str, target_id: str, connection_type: str,
                       source_anchor: str = "right", target_anchor: str = "left") -> Optional[UMLConnection]:
        try:
            conn = self.manager.add_connection(source_id, target_id, connection_type, source_anchor, target_anchor)
            if conn:
                self.connection_added.emit(conn)
                self._save_state()
                return conn
            return None
        except Exception as e:
            self.error_occurred.emit(f"Ошибка создания связи: {e}")
            return None

    def update_connection_type(self, connection_id: str, new_type: str) -> bool:
        """Смена типа (ассоциация, наследование и т.д.)"""
        try:
            if self.manager.update_connection_type(connection_id, new_type):
                self.connection_updated.emit(connection_id)
                self._save_state()
                return True
            return False
        except Exception as e:
            self.error_occurred.emit(f"Ошибка обновления типа: {e}")
            return False

    def get_connection_model(self, connection_id: str) -> Optional[UMLConnection]:
        """Возвращает данные связи по ID (нужно для перерисовки)"""
        for conn in self.manager.diagram.connections:
            if conn.id == connection_id:
                return conn
        return None

    def remove_connection(self, connection_id: str) -> bool:
        if self.manager.remove_connection(connection_id):
            self.connection_removed.emit(connection_id)
            self._save_state()
            return True
        return False

    # --- ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ (Парсинг строк) ---

    def _parse_attribute_string(self, s: str) -> Dict:
        visibility = "public"
        s = s.strip()
        if s.startswith("+"): visibility = "public"; s = s[1:]
        elif s.startswith("-"): visibility = "private"; s = s[1:]
        elif s.startswith("#"): visibility = "protected"; s = s[1:]

        if ":" in s:
            name, t = s.split(":", 1)
            return {"name": name.strip(), "type": t.strip(), "visibility": visibility}
        return {"name": s.strip(), "type": "Any", "visibility": visibility}

    def _parse_method_string(self, s: str) -> Dict:
        name = s.replace("()", "").strip()
        return {"name": name, "return_type": "void", "visibility": "public"}

    # --- СИСТЕМНЫЕ СОБЫТИЯ ---

    def _on_state_restored(self, diagram: UMLDiagram):
        """Срабатывает при Undo/Redo"""
        self.manager.diagram = diagram.model_copy(deep=True)
        self.card_map.clear()
        self.connection_map.clear()
        self.diagram_loaded.emit()

    def _on_history_changed(self, cu, cr):
        self.undo_redo_changed.emit()

    def register_card_view(self, nid, w): self.card_map[nid] = w
    def register_connection_view(self, cid, w): self.connection_map[cid] = w

    def clear_diagram(self):
        self.manager.clear()
        self.card_map.clear()
        self.connection_map.clear()
        self.diagram_cleared.emit()
        self._save_state()
