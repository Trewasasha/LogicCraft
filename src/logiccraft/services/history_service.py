"""
LogicCraft: UML Architect
Сервис управления историей (Undo/Redo)
"""
import logging
from typing import Optional, List, Union, Tuple
from threading import Lock
from PyQt6.QtCore import QObject, pyqtSignal
from ..models.diagram import UMLDiagram

# Настройка логирования для отладки
logger = logging.getLogger(__name__)

class HistoryService(QObject):
    """
    Сервис для управления снимками состояния диаграммы.
    Реализует оптимизированное хранение, фильтрацию микродвижений
    и валидацию графа на циклы наследования.
    """

    # Сигналы для связи с Controller и UI
    history_changed = pyqtSignal(bool, bool)  # (can_undo, can_redo)
    state_restored = pyqtSignal(object)       # Передает UMLDiagram во View
    validation_failed = pyqtSignal(str)       # Сообщение об ошибке в структуре

    def __init__(self, max_history: int = 50, initial_state: UMLDiagram = None):
        super().__init__()
        self._stack: List[UMLDiagram] = []
        self._current_index: int = -1
        self._max_history = max_history
        self._lock = Lock()
        self._is_restoring = False  # Флаг, блокирующий запись во время Undo/Redo

        # Сохраняем начальное состояние как точку невозврата
        if initial_state:
            self.push_state(initial_state)

    def push_state(self, state: Union[UMLDiagram, dict]) -> None:
        """
        Добавляет новое состояние в историю.
        Автоматически игнорирует дубликаты и микродвижения (< 0.5px).
        """
        if self._is_restoring:
            return

        # Преобразование dict в модель если нужно
        if isinstance(state, dict):
            try:
                state = UMLDiagram.model_validate(state)
            except Exception as e:
                logger.error(f"History: Validation error: {e}")
                return

        # 1. Проверка на дубликат или микро-сдвиг (Deadzone)
        is_dup, reason = self._check_duplicate(state)
        if is_dup:
            logger.debug(f"History: Push skipped. Reason: {reason}")
            return

        # 2. Создание глубокой копии (вне лока для производительности)
        new_snapshot = state.model_copy(deep=True)

        # 3. Атомарная запись в стек
        with self._lock:
            # Отрезаем ветку Redo, если новое действие сделано после отмены
            if self._current_index < len(self._stack) - 1:
                logger.info(f"History: Redo branch pruned ({len(self._stack) - 1 - self._current_index} states)")
                self._stack = self._stack[:self._current_index + 1]

            self._stack.append(new_snapshot)
            self._current_index += 1

            # Ограничение размера стека
            if len(self._stack) > self._max_history:
                self._stack.pop(0)
                self._current_index -= 1

        logger.info(f"History: State #{self._current_index} saved. Stack size: {len(self._stack)}")
        self._emit_status()

    def undo(self) -> Optional[UMLDiagram]:
        """Откат к предыдущему состоянию"""
        with self._lock:
            if not self.can_undo():
                logger.debug("History: Undo not available")
                return None

            self._is_restoring = True
            try:
                self._current_index -= 1
                state = self._stack[self._current_index].model_copy(deep=True)
            finally:
                self._is_restoring = False

        logger.info(f"History: Undo performed. New index: {self._current_index}")
        self.state_restored.emit(state)
        self._emit_status()
        return state

    def redo(self) -> Optional[UMLDiagram]:
        """Возврат к отмененному состоянию"""
        with self._lock:
            if not self.can_redo():
                logger.debug("History: Redo not available")
                return None

            self._is_restoring = True
            try:
                self._current_index += 1
                state = self._stack[self._current_index].model_copy(deep=True)
            finally:
                self._is_restoring = False

        logger.info(f"History: Redo performed. New index: {self._current_index}")
        self.state_restored.emit(state)
        self._emit_status()
        return state

    def can_undo(self) -> bool:
        """Можно отменить, если индекс больше нуля (есть куда падать)"""
        return self._current_index > 0

    def can_redo(self) -> bool:
        """Можно повторить, если мы не в конце стека"""
        return self._current_index < len(self._stack) - 1

    def validate_for_codegen(self, diagram: UMLDiagram) -> List[str]:
        """
        L3 Валидация: Полная проверка графа перед генерацией кода.
        Ищет циклы наследования (Floyd's cycle-finding algorithm).
        """
        errors = []
        node_ids = {n.id for n in diagram.nodes}

        # 1. Проверка битых связей
        for conn in diagram.connections:
            if conn.source_id not in node_ids or conn.target_id not in node_ids:
                errors.append(f"Broken connection detected: {conn.id}")

        # 2. Поиск циклов (Черепаха и Заяц)
        inheritance_map = {
            c.source_id: c.target_id
            for c in diagram.connections if c.type.value == "inheritance"
        }

        for start_id in inheritance_map:
            slow = start_id
            fast = start_id
            while fast in inheritance_map and inheritance_map[fast] in inheritance_map:
                slow = inheritance_map[slow]
                fast = inheritance_map[inheritance_map[fast]]
                if slow == fast:
                    node = diagram.get_node(slow)
                    msg = f"Cycle detected in inheritance starting from: {node.name if node else slow}"
                    errors.append(msg)
                    self.validation_failed.emit(msg)
                    break

        return errors

    def _check_duplicate(self, state: UMLDiagram) -> Tuple[bool, str]:
        """
        Интеллектуальное сравнение состояний для предотвращения забивания памяти.
        """
        if self._current_index == -1:
            return False, "Initial push"

        current = self._stack[self._current_index]

        # Базовая проверка количества (включая UC-элементы)
        if len(state.nodes) != len(current.nodes) or \
                len(state.connections) != len(current.connections) or \
                len(state.uc_actors) != len(current.uc_actors) or \
                len(state.uc_scenarios) != len(current.uc_scenarios) or \
                len(state.uc_connections) != len(current.uc_connections):
            return False, "Structure changed"

        # Проверка узлов (позиции и контент)
        curr_nodes = {n.id: n for n in current.nodes}
        for node in state.nodes:
            cn = curr_nodes.get(node.id)
            if not cn: return False, "Node ID changed"

            # Deadzone: игнорируем сдвиги меньше 0.5px
            if abs(node.x - cn.x) > 0.5 or abs(node.y - cn.y) > 0.5:
                return False, f"Movement: {node.name} moved significantly"

            if node.name != cn.name or node.properties != cn.properties:
                return False, "Data inside node changed"

        # Проверка связей
        curr_conns = {c.id: c for c in current.connections}
        for conn in state.connections:
            cc = curr_conns.get(conn.id)
            if not cc or conn.type != cc.type or \
                    conn.source_anchor != cc.source_anchor:
                return False, "Connection attributes changed"

        # Проверка UC-актёров
        curr_actors = {a.id: a for a in current.uc_actors}
        for actor in state.uc_actors:
            ca = curr_actors.get(actor.id)
            if not ca: return False, "UC Actor ID changed"
            if abs(actor.x - ca.x) > 0.5 or abs(actor.y - ca.y) > 0.5:
                return False, f"UC Actor moved: {actor.name}"
            if actor.name != ca.name:
                return False, "UC Actor name changed"

        # Проверка UC-сценариев
        curr_scenarios = {s.id: s for s in current.uc_scenarios}
        for scenario in state.uc_scenarios:
            cs = curr_scenarios.get(scenario.id)
            if not cs: return False, "UC Scenario ID changed"
            if abs(scenario.x - cs.x) > 0.5 or abs(scenario.y - cs.y) > 0.5:
                return False, f"UC Scenario moved: {scenario.name}"
            if scenario.name != cs.name:
                return False, "UC Scenario name changed"

        # Проверка UC-связей
        curr_uc_conns = {c.id: c for c in current.uc_connections}
        for uc_conn in state.uc_connections:
            cc = curr_uc_conns.get(uc_conn.id)
            if not cc or uc_conn.type != cc.type:
                return False, "UC Connection changed"

        return True, "No significant changes detected"

    def _emit_status(self):
        """Информирует UI о доступности кнопок Undo/Redo"""
        self.history_changed.emit(self.can_undo(), self.can_redo())

    def clear(self):
        """Полная очистка стека"""
        with self._lock:
            self._stack.clear()
            self._current_index = -1
        self._emit_status()
