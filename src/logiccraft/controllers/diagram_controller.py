"""
LogicCraft: UML Architect
Главный контроллер диаграммы - Полная сборка
"""
import logging
from PyQt6.QtCore import QObject, pyqtSignal
from typing import List, Dict, Optional, Any

from ..models.diagram import UMLDiagram, UMLNode, UMLConnection, NodeType
from ..models.diagram import UseCaseActor, UseCaseScenario, UseCaseConnection, ConnectionType
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

    # Use Case сигналы
    uc_actor_added = pyqtSignal(object)       # UseCaseActor
    uc_actor_removed = pyqtSignal(str)
    uc_scenario_added = pyqtSignal(object)    # UseCaseScenario
    uc_scenario_removed = pyqtSignal(str)
    uc_connection_added = pyqtSignal(object)  # UseCaseConnection
    uc_connection_removed = pyqtSignal(str)

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

    def update_connection_properties(self, connection_id: str,
                                     new_type: str = None,
                                     multiplicity: str = None,
                                     name: str = None) -> bool:
        """Обновить тип, множественность и имя связи"""
        try:
            conn = self.manager.get_connection_by_id(connection_id)
            if not conn:
                return False
            if new_type is not None:
                self.manager.update_connection_type(connection_id, new_type)
            if multiplicity is not None:
                conn.multiplicity = multiplicity
            if name is not None:
                conn.name = name
            self.connection_updated.emit(connection_id)
            self._save_state()
            return True
        except Exception as e:
            self.error_occurred.emit(f"Ошибка обновления связи: {e}")
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

    def duplicate_card(self, card_id: str, offset_x: float = 30, offset_y: float = 30) -> Optional[UMLNode]:
        """Дублировать карточку со смещением"""
        try:
            source = self.manager.get_node_by_id(card_id)
            if not source:
                return None
            node = self.manager.add_node(
                source.x + offset_x,
                source.y + offset_y,
                name=source.name + "_copy",
                node_type=source.node_type
            )
            # Копируем атрибуты и методы
            from ..models.diagram import UMLProperty, UMLMethod
            node.properties = [p.model_copy() for p in source.properties]
            node.methods = [m.model_copy() for m in source.methods]
            node.enum_literals = [l.model_copy() for l in source.enum_literals]
            node.is_abstract = source.is_abstract
            self.card_added.emit(node)
            self._save_state()
            self.status_changed.emit(f"Класс {node.name} дублирован")
            return node
        except Exception as e:
            self.error_occurred.emit(f"Ошибка дублирования: {e}")
            return None

    def copy_selected(self, card_ids: list,
                      actor_ids: list = None,
                      scenario_ids: list = None) -> None:
        """Сохранить выбранные элементы в буфер копирования"""
        self._clipboard = []
        self._clipboard_uc_actors = []
        self._clipboard_uc_scenarios = []

        for card_id in card_ids:
            node = self.manager.get_node_by_id(card_id)
            if node:
                self._clipboard.append(node.model_copy(deep=True))

        for actor_id in (actor_ids or []):
            actor = next((a for a in self.manager.diagram.uc_actors if a.id == actor_id), None)
            if actor:
                self._clipboard_uc_actors.append(actor.model_copy(deep=True))

        for scenario_id in (scenario_ids or []):
            scenario = next((s for s in self.manager.diagram.uc_scenarios if s.id == scenario_id), None)
            if scenario:
                self._clipboard_uc_scenarios.append(scenario.model_copy(deep=True))

    def paste_clipboard(self) -> list:
        """Вставить элементы из буфера"""
        new_nodes = []

        # Вставка обычных классов
        for source in getattr(self, '_clipboard', []):
            node = self.manager.add_node(
                source.x + 40,
                source.y + 40,
                name=source.name + "_copy",
                node_type=source.node_type
            )
            node.properties = [p.model_copy() for p in source.properties]
            node.methods = [m.model_copy() for m in source.methods]
            node.enum_literals = [l.model_copy() for l in source.enum_literals]
            node.is_abstract = source.is_abstract
            self.card_added.emit(node)
            new_nodes.append(node)

        # Вставка UC-актёров
        for source in getattr(self, '_clipboard_uc_actors', []):
            actor = self.add_uc_actor(source.x + 40, source.y + 40,
                                      name=source.name + "_copy")
            if actor:
                new_nodes.append(actor)

        # Вставка UC-сценариев
        for source in getattr(self, '_clipboard_uc_scenarios', []):
            scenario = self.add_uc_scenario(source.x + 40, source.y + 40,
                                            name=source.name + "_copy")
            if scenario:
                new_nodes.append(scenario)

        if new_nodes:
            self._save_state()
            self.status_changed.emit(f"Вставлено {len(new_nodes)} элементов")
        return new_nodes

    def select_all(self) -> list:
        """Вернуть все ID карточек для выделения"""
        return [node.id for node in self.manager.diagram.nodes]

    # --- USE CASE ОПЕРАЦИИ ---

    def add_uc_actor(self, x: float, y: float, name: str = None) -> Optional[UseCaseActor]:
        """Добавить актёра Use Case"""
        try:
            if name is None:
                n = len(self.manager.diagram.uc_actors) + 1
                name = f"Актёр{n}"
            actor = UseCaseActor(name=name, x=x, y=y)
            self.manager.diagram.uc_actors.append(actor)
            self.uc_actor_added.emit(actor)
            self._save_state()
            self.status_changed.emit(f"Актёр «{name}» добавлен")
            return actor
        except Exception as e:
            self.error_occurred.emit(f"Ошибка добавления актёра: {e}")
            return None

    def remove_uc_actor(self, actor_id: str) -> bool:
        """Удалить актёра и его связи"""
        try:
            diagram = self.manager.diagram
            # Удаляем связи актёра
            diagram.uc_connections = [
                c for c in diagram.uc_connections
                if c.source_id != actor_id and c.target_id != actor_id
            ]
            before = len(diagram.uc_actors)
            diagram.uc_actors = [a for a in diagram.uc_actors if a.id != actor_id]
            if len(diagram.uc_actors) < before:
                self.uc_actor_removed.emit(actor_id)
                self._save_state()
                return True
            return False
        except Exception as e:
            self.error_occurred.emit(f"Ошибка удаления актёра: {e}")
            return False

    def update_uc_actor(self, actor_id: str, name: str = None,
                        x: float = None, y: float = None) -> bool:
        """Обновить актёра"""
        for actor in self.manager.diagram.uc_actors:
            if actor.id == actor_id:
                if name is not None:
                    actor.name = name
                if x is not None:
                    actor.x = x
                if y is not None:
                    actor.y = y
                return True
        return False

    def add_uc_scenario(self, x: float, y: float, name: str = None) -> Optional[UseCaseScenario]:
        """Добавить сценарий Use Case"""
        try:
            if name is None:
                n = len(self.manager.diagram.uc_scenarios) + 1
                name = f"Сценарий{n}"
            scenario = UseCaseScenario(name=name, x=x, y=y)
            self.manager.diagram.uc_scenarios.append(scenario)
            self.uc_scenario_added.emit(scenario)
            self._save_state()
            self.status_changed.emit(f"Сценарий «{name}» добавлен")
            return scenario
        except Exception as e:
            self.error_occurred.emit(f"Ошибка добавления сценария: {e}")
            return None

    def remove_uc_scenario(self, scenario_id: str) -> bool:
        """Удалить сценарий и его связи"""
        try:
            diagram = self.manager.diagram
            diagram.uc_connections = [
                c for c in diagram.uc_connections
                if c.source_id != scenario_id and c.target_id != scenario_id
            ]
            before = len(diagram.uc_scenarios)
            diagram.uc_scenarios = [s for s in diagram.uc_scenarios if s.id != scenario_id]
            if len(diagram.uc_scenarios) < before:
                self.uc_scenario_removed.emit(scenario_id)
                self._save_state()
                return True
            return False
        except Exception as e:
            self.error_occurred.emit(f"Ошибка удаления сценария: {e}")
            return False

    def update_uc_scenario(self, scenario_id: str, name: str = None,
                           x: float = None, y: float = None) -> bool:
        """Обновить сценарий"""
        for scenario in self.manager.diagram.uc_scenarios:
            if scenario.id == scenario_id:
                if name is not None:
                    scenario.name = name
                if x is not None:
                    scenario.x = x
                if y is not None:
                    scenario.y = y
                return True
        return False

    def add_uc_connection(self, source_id: str, target_id: str,
                          conn_type: str = "uc_association",
                          source_anchor: str = "right",
                          target_anchor: str = "left") -> Optional[UseCaseConnection]:
        """Добавить связь Use Case"""
        try:
            conn = UseCaseConnection(
                source_id=source_id,
                target_id=target_id,
                type=ConnectionType(conn_type),
                source_anchor=source_anchor,
                target_anchor=target_anchor
            )
            self.manager.diagram.uc_connections.append(conn)
            self.uc_connection_added.emit(conn)
            self._save_state()
            return conn
        except Exception as e:
            self.error_occurred.emit(f"Ошибка создания UC-связи: {e}")
            return None

    def remove_uc_connection(self, conn_id: str) -> bool:
        """Удалить связь Use Case"""
        diagram = self.manager.diagram
        before = len(diagram.uc_connections)
        diagram.uc_connections = [c for c in diagram.uc_connections if c.id != conn_id]
        if len(diagram.uc_connections) < before:
            self.uc_connection_removed.emit(conn_id)
            self._save_state()
            return True
        return False

    def validate_diagram(self) -> list:
        """Валидация диаграммы — возвращает список предупреждений"""
        warnings = []
        diagram = self.manager.diagram

        # Дублирующиеся имена классов
        names = [n.name for n in diagram.nodes]
        duplicates = {n for n in names if names.count(n) > 1}
        for name in duplicates:
            warnings.append(f"⚠️ Дублирующееся имя класса: «{name}»")

        # Классы без атрибутов и методов
        for node in diagram.nodes:
            if not node.properties and not node.methods and node.node_type.value == 'class':
                warnings.append(f"ℹ️ Класс «{node.name}» не имеет атрибутов и методов")

        # Интерфейс без методов
        for node in diagram.nodes:
            if node.node_type.value == 'interface' and not node.methods:
                warnings.append(f"⚠️ Интерфейс «{node.name}» не имеет методов")

        # Циклические зависимости наследования
        inheritance = {}
        for node in diagram.nodes:
            inheritance[node.id] = []
        for conn in diagram.connections:
            if conn.type.value == 'inheritance':
                inheritance[conn.source_id].append(conn.target_id)

        def has_cycle(node_id, visited, path):
            if node_id in path:
                return True
            if node_id in visited:
                return False
            visited.add(node_id)
            path.add(node_id)
            for child in inheritance.get(node_id, []):
                if has_cycle(child, visited, path):
                    return True
            path.discard(node_id)
            return False

        visited = set()
        for node in diagram.nodes:
            if has_cycle(node.id, visited, set()):
                warnings.append(f"❌ Циклическое наследование обнаружено в «{node.name}»")
                break

        # Связи к несуществующим узлам
        node_ids = {n.id for n in diagram.nodes}
        for conn in diagram.connections:
            if conn.source_id not in node_ids or conn.target_id not in node_ids:
                warnings.append(f"❌ Связь ссылается на несуществующий класс")

        return warnings
        """Сохранить диаграмму в файл"""
        return self.manager.save_to_file(filepath)

    def load_diagram(self, filepath: str) -> bool:
        """Загрузить диаграмму из файла"""
        result = self.manager.load_from_file(filepath)
        if result:
            self.diagram_loaded.emit()
        return result
