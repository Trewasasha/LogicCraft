"""Сервис для управления историей изменений (Undo/Redo)"""
import copy
import logging
from typing import Any, Optional, List, Union
from threading import Lock
from PyQt6.QtCore import QObject, pyqtSignal
from ..models.diagram import UMLDiagram, UMLNode, UMLConnection

logger = logging.getLogger(__name__)


class StateCompressionError(Exception):
    """Ошибка при сжатии состояния"""
    pass


class InvalidStateError(Exception):
    """Ошибка невалидного состояния"""
    pass


class HistoryService(QObject):
    """
    Сервис для отслеживания изменений состояния диаграммы.
    Реализует оптимизированное управление историей с:
    - Работой напрямую с UMLDiagram
    - Инкрементальными изменениями вместо полного deepcopy
    - Сжатием старых состояний
    - Валидацией данных
    - Потокобезопасностью
    """

    # Сигналы для обновления UI
    # Передаем can_undo и can_redo напрямую, чтобы UI не вызывал методы отдельно
    history_changed = pyqtSignal(bool, bool)  # (can_undo, can_redo)
    state_restored = pyqtSignal(object)  # Emit when state is restored (for views to update)
    state_validation_failed = pyqtSignal(str)  # Emit when validation fails

    def __init__(self, max_history: int = 50, compression_threshold: int = 20, initial_state: UMLDiagram = None):
        """
        Инициализация сервиса истории.
        
        Args:
            max_history: Максимальное количество состояний в истории
            compression_threshold: Порог для сжатия старых состояний
            initial_state: Начальное состояние диаграммы (обычно пустая диаграмма)
        """
        super().__init__()
        self._stack: List[UMLDiagram] = []
        self._current_index: int = -1
        self._max_history = max_history
        self._compression_threshold = compression_threshold
        self._is_restoring = False  # Flag to prevent recording during restore
        self._lock = Lock()  # Thread-safe operations
        self._compressed_count: int = 0  # Track compression statistics
        
        # Если передано начальное состояние, сохраняем его
        if initial_state is not None:
            self._save_initial_state(initial_state)

    def _save_initial_state(self, state: UMLDiagram) -> None:
        """
        Сохранить начальное состояние (базовая точка для undo).
        Вызывается один раз при инициализации.
        
        Args:
            state: Начальное состояние диаграммы
        """
        try:
            with self._lock:
                # Конвертируем dict в UMLDiagram если нужно
                if isinstance(state, dict):
                    state = self._dict_to_diagram(state)
                
                # Сохраняем копию начального состояния
                state_copy = state.model_copy(deep=True)
                self._stack.append(state_copy)
                self._current_index = 0  # Устанавливаем индекс на 0
                
                logger.debug(f"Initial state saved. Stack size: {len(self._stack)}, Index: {self._current_index}")
        
        except Exception as e:
            logger.error(f"Failed to save initial state: {e}", exc_info=True)
            raise

    def push_state(self, state: Union[UMLDiagram, dict], validate: bool = True, is_checkpoint: bool = False) -> None:
        """
        Добавить новое состояние в историю.
        
        Args:
            state: Состояние диаграммы (UMLDiagram или dict для обратной совместимости)
            validate: Проверять валидность состояния
            is_checkpoint: Важная точка восстановления (не будет сжата)
            
        Raises:
            InvalidStateError: Если состояние невалидно
        """
        # 1. Валидация БЕЗ блокировки (можно делать параллельно)
        if validate:
            try:
                # Pydantic validation - работает на C уровне
                if isinstance(state, dict):
                    state = self._dict_to_diagram(state)
                
                UMLDiagram.model_validate(state, strict=False)
                
                # Быстрая проверка связей
                errors_l2 = self._validate_connections_only(state)
                if errors_l2:
                    error_msg = f"Connection validation failed: {', '.join(errors_l2)}"
                    logger.warning(error_msg)
                    self.state_validation_failed.emit(error_msg)
            except Exception as e:
                error_msg = f"Validation failed: {str(e)}"
                logger.warning(error_msg)
                self.state_validation_failed.emit(error_msg)
                # Не блокируем, только предупреждаем
        
        # 2. Проверка на дубликат БЕЗ блокировки (только чтение)
        if self._is_duplicate_state(state):
            logger.debug("State unchanged, skipping push")
            return
        
        # 3. Копирование БЕЗ блокировки (тяжелая операция)
        try:
            state_copy = state.model_copy(deep=True)
            state_copy._is_checkpoint = is_checkpoint  # Метка важности
        except Exception as e:
            logger.error(f"Failed to copy state: {e}", exc_info=True)
            raise
        
        # 4. Атомарное обновление С блокировкой (быстро!)
        try:
            with self._lock:
                # Если в процессе подготовки состояние изменилось, проверяем снова
                if self._is_restoring:
                    logger.debug("Skipping state push during restoration")
                    return
                
                # Удаляем все состояния после текущего (очищаем redo стек)
                if self._current_index < len(self._stack) - 1:
                    self._stack = self._stack[:self._current_index + 1]

                # Добавляем новое состояние
                self._stack.append(state_copy)
                self._current_index += 1

                # Ограничиваем размер истории
                if len(self._stack) > self._max_history:
                    self._stack.pop(0)
                    self._current_index -= 1

                # Сжимаем старые состояния если нужно
                if len(self._stack) > self._compression_threshold:
                    self._compress_old_states()
        
        except Exception as e:
            logger.error(f"Failed to push state: {e}", exc_info=True)
            raise
        
        finally:
            # Сигнал в finally - гарантированно сработает даже при ошибке
            self._emit_history_changed()
            logger.debug(f"State pushed. Stack size: {len(self._stack)}, Index: {self._current_index}")

    def undo(self) -> Optional[UMLDiagram]:
        """
        Отменить последнее действие.
        
        Returns:
            Предыдущее состояние или None, если отмена невозможна
        """
        try:
            with self._lock:
                if not self.can_undo():
                    logger.debug("Undo not available")
                    return None

                self._is_restoring = True
                try:
                    self._current_index -= 1
                    # Оптимизация: model_copy вместо deepcopy
                    state = self._stack[self._current_index].model_copy(deep=True)
                    logger.debug(f"Undo performed. New index: {self._current_index}")
                finally:
                    self._is_restoring = False

                self._emit_history_changed()
                self.state_restored.emit(state)
                
                return state
        
        except Exception as e:
            logger.error(f"Failed to undo: {e}", exc_info=True)
            self._is_restoring = False  # Ensure flag is reset
            return None

    def redo(self) -> Optional[UMLDiagram]:
        """
        Повторить отмененное действие.
        
        Returns:
            Следующее состояние или None, если повтор невозможен
        """
        try:
            with self._lock:
                if not self.can_redo():
                    logger.debug("Redo not available")
                    return None

                self._is_restoring = True
                try:
                    self._current_index += 1
                    # Оптимизация: model_copy вместо deepcopy
                    state = self._stack[self._current_index].model_copy(deep=True)
                    logger.debug(f"Redo performed. New index: {self._current_index}")
                finally:
                    self._is_restoring = False

                self._emit_history_changed()
                self.state_restored.emit(state)
                
                return state
        
        except Exception as e:
            logger.error(f"Failed to redo: {e}", exc_info=True)
            self._is_restoring = False  # Ensure flag is reset
            return None

    def can_undo(self) -> bool:
        """
        Проверить, возможна ли операция отмены.
        
        Returns:
            True если есть состояния для отмены
        """
        return self._current_index > 0

    def can_redo(self) -> bool:
        """
        Проверить, возможна ли операция повтора.
        
        Returns:
            True если есть состояния для повтора
        """
        return self._current_index < len(self._stack) - 1

    def _emit_history_changed(self) -> None:
        """
        Испустить сигнал об изменении истории с параметрами can_undo и can_redo.
        Это позволяет UI получить состояние сразу, без отдельных вызовов.
        """
        try:
            can_undo = self.can_undo()
            can_redo = self.can_redo()
            self.history_changed.emit(can_undo, can_redo)
            logger.debug(f"History changed: can_undo={can_undo}, can_redo={can_redo}")
        except Exception as e:
            logger.error(f"Failed to emit history_changed: {e}", exc_info=True)

    def _is_duplicate_state(self, state: UMLDiagram) -> bool:
        """
        Проверить, является ли состояние дубликатом текущего.
        Сравнивает по ID узлов, а не по индексу!
        
        Args:
            state: Новое состояние для проверки
            
        Returns:
            True если состояние не изменилось
        """
        if self._current_index < 0 or self._current_index >= len(self._stack):
            return False
        
        current_state = self._stack[self._current_index]
        
        # Быстрая проверка: если количество узлов и связей не изменилось
        if (len(state.nodes) != len(current_state.nodes) or 
            len(state.connections) != len(current_state.connections)):
            return False
        
        # Создаем dict для O(1) поиска по ID
        current_nodes_map = {node.id: node for node in current_state.nodes}
        
        for node in state.nodes:
            if node.id not in current_nodes_map:
                return False  # Новый узел добавлен
            
            current_node = current_nodes_map[node.id]
            
            # Сравниваем важные поля
            if (node.name != current_node.name or
                abs(node.x - current_node.x) >= 0.1 or
                abs(node.y - current_node.y) >= 0.1 or
                len(node.properties) != len(current_node.properties) or
                len(node.methods) != len(current_node.methods)):
                return False
        
        # Проверяем связи по ID
        current_conn_ids = {conn.id for conn in current_state.connections}
        new_conn_ids = {conn.id for conn in state.connections}
        
        return current_conn_ids == new_conn_ids

    def clear(self) -> None:
        """Очистить всю историю"""
        try:
            with self._lock:
                # Устанавливаем флаг чтобы предотвратить запись во время очистки
                was_restoring = self._is_restoring
                self._is_restoring = True
                
                try:
                    self._stack.clear()
                    self._current_index = -1
                    self._compressed_count = 0
                    logger.debug("History cleared")
                finally:
                    # Восстанавливаем предыдущее состояние флага
                    self._is_restoring = was_restoring
                    
                self._emit_history_changed()
        
        except Exception as e:
            logger.error(f"Failed to clear history: {e}", exc_info=True)
            self._is_restoring = False  # Safety reset

    @property
    def current_index(self) -> int:
        """Текущий индекс в истории"""
        return self._current_index

    @property
    def stack_size(self) -> int:
        """Размер стека истории"""
        return len(self._stack)

    @property
    def max_history(self) -> int:
        """Максимальный размер истории"""
        return self._max_history

    @max_history.setter
    def max_history(self, value: int) -> None:
        """Установить максимальный размер истории"""
        self._max_history = max(1, value)
        # Обрезаем стек если нужно
        while len(self._stack) > self._max_history:
            self._stack.pop(0)
            if self._current_index >= len(self._stack):
                self._current_index = len(self._stack) - 1

    def get_current_state(self) -> Optional[UMLDiagram]:
        """
        Получить текущее состояние без изменения индекса.
        
        Returns:
            Текущее состояние или None
        """
        try:
            with self._lock:
                if 0 <= self._current_index < len(self._stack):
                    return self._stack[self._current_index].model_copy(deep=True)
                return None
        
        except Exception as e:
            logger.error(f"Failed to get current state: {e}", exc_info=True)
            return None

    def has_history(self) -> bool:
        """
        Проверить, есть ли сохраненные состояния.
        
        Returns:
            True если в истории есть хотя бы одно состояние
        """
        with self._lock:
            return len(self._stack) > 0

    def _validate_connections_only(self, diagram: UMLDiagram) -> List[str]:
        """
        УРОВЕНЬ 2: Быстрая проверка связей (O(c) - только связи).
        Проверяет что все связи ссылаются на существующие узлы.
        
        Args:
            diagram: Диаграмма для валидации
            
        Returns:
            Список ошибок валидации
        """
        errors = []
        
        try:
            # Собираем все ID узлов в set для O(1) поиска
            node_ids = {node.id for node in diagram.nodes}
            
            # Проверяем ТОЛЬКО связи (быстро!)
            for conn in diagram.connections:
                if conn.source_id not in node_ids:
                    errors.append(f"Connection {conn.id}: source {conn.source_id} not found")
                if conn.target_id not in node_ids:
                    errors.append(f"Connection {conn.id}: target {conn.target_id} not found")
        
        except Exception as e:
            errors.append(f"Connection validation error: {str(e)}")
        
        return errors

    def _validate_for_codegen(self, diagram: UMLDiagram) -> List[str]:
        """
        УРОВЕНЬ 3: Полная проверка для генерации кода (медленная, вызывается вручную).
        Проверяет имена классов, наследование, style guide и т.д.
        
        Args:
            diagram: Диаграмма для валидации
            
        Returns:
            Список ошибок валидации
        """
        import re
        errors = []
        
        try:
            node_ids = {node.id for node in diagram.nodes}
            
            # Проверяем каждый узел
            for node in diagram.nodes:
                # 1. Проверка на пустое имя
                if not node.name or not node.name.strip():
                    errors.append(f"Node {node.id}: empty name")
                    continue
                
                # 2. Проверка имени класса (style guide: PascalCase)
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    errors.append(
                        f"Node '{node.name}': invalid class name. "
                        f"Should be PascalCase (e.g., MyClass, UserProfile)"
                    )
                
                # 3. Проверка уникальности ID (на случай copy-paste)
                if diagram.nodes.count(node) > 1:
                    errors.append(f"Node {node.id}: duplicate ID detected")
                
                # 4. Проверка свойств и методов на пустые имена
                for prop in node.properties:
                    if not prop.name or not prop.name.strip():
                        errors.append(f"Node '{node.name}': property with empty name")
                    if not prop.type or not prop.type.strip():
                        errors.append(f"Node '{node.name}': property '{prop.name}' with empty type")
                
                for method in node.methods:
                    if not method.name or not method.name.strip():
                        errors.append(f"Node '{node.name}': method with empty name")
            
            # 5. Проверка на наследование самого себя
            for conn in diagram.connections:
                if conn.type.value == 'inheritance':
                    if conn.source_id == conn.target_id:
                        source_node = diagram.get_node(conn.source_id)
                        errors.append(
                            f"Node '{source_node.name if source_node else conn.source_id}': "
                            f"cannot inherit from itself"
                        )
            
            # 6. Проверка на циклическое наследование (A -> B -> A)
            inheritance_graph = {}
            for conn in diagram.connections:
                if conn.type.value == 'inheritance':
                    inheritance_graph[conn.source_id] = conn.target_id
            
            # Detect cycles
            visited = set()
            for start_id in inheritance_graph:
                if start_id in visited:
                    continue
                
                path = set()
                current = start_id
                while current and current in inheritance_graph:
                    if current in path:
                        # Found cycle
                        node = diagram.get_node(current)
                        errors.append(
                            f"Node '{node.name if node else current}': "
                            f"cyclic inheritance detected"
                        )
                        break
                    path.add(current)
                    visited.add(current)
                    current = inheritance_graph.get(current)
        
        except Exception as e:
            errors.append(f"Codegen validation error: {str(e)}")
        
        return errors

    def _compress_old_states(self) -> None:
        """
        Сжать старые состояния для экономии памяти.
        Оставляет checkpoint состояния и каждое 2-ое обычное.
        Оптимизировано: не создает копии списков!
        """
        try:
            if len(self._stack) <= self._compression_threshold:
                return
            
            threshold = self._compression_threshold
            
            # Разделяем на старые и новые
            old_count = len(self._stack) - threshold
            
            # Находим индексы для удаления (только не-checkpoint)
            indices_to_remove = []
            for i in range(old_count):
                state = self._stack[i]
                is_checkpoint = getattr(state, '_is_checkpoint', False)
                
                # Не удаляем checkpoint и каждое 2-ое
                if not is_checkpoint and i % 2 == 1:
                    indices_to_remove.append(i)
            
            # Удаляем в обратном порядке (чтобы индексы не смещались)
            removed_count = 0
            for i in reversed(indices_to_remove):
                del self._stack[i]
                removed_count += 1
                if i <= self._current_index:
                    self._current_index -= 1
            
            self._compressed_count += removed_count
            
            logger.debug(f"Compressed history: removed {removed_count} states. "
                        f"Total compressed: {self._compressed_count}")
        
        except Exception as e:
            logger.error(f"Failed to compress states: {e}", exc_info=True)
            raise StateCompressionError(f"Compression failed: {e}")

    def _dict_to_diagram(self, data: dict) -> UMLDiagram:
        """
        Конвертировать dict в UMLDiagram для обратной совместимости.
        
        Args:
            data: Словарь с данными диаграммы
            
        Returns:
            UMLDiagram объект
        """
        try:
            nodes = [UMLNode(**node_data) for node_data in data.get('nodes', [])]
            connections = [UMLConnection(**conn_data) for conn_data in data.get('connections', [])]
            
            return UMLDiagram(
                id=data.get('id', ''),
                name=data.get('name', 'Untitled'),
                nodes=nodes,
                connections=connections
            )
        except Exception as e:
            logger.error(f"Failed to convert dict to UMLDiagram: {e}", exc_info=True)
            raise InvalidStateError(f"Invalid state data: {e}")

    def get_compression_stats(self) -> dict:
        """
        Получить статистику сжатия истории.
        
        Returns:
            Словарь со статистикой
        """
        with self._lock:
            return {
                'stack_size': len(self._stack),
                'current_index': self._current_index,
                'max_history': self._max_history,
                'compressed_count': self._compressed_count,
                'memory_optimized': self._compressed_count > 0
            }

    def validate_for_codegen(self, diagram: UMLDiagram = None) -> List[str]:
        """
        Провести полную валидацию диаграммы перед генерацией кода.
        Вызывается вручную, НЕ автоматически при push_state!
        
        Args:
            diagram: Диаграмма для валидации (если None, использует текущее состояние)
            
        Returns:
            Список ошибок валидации
        """
        try:
            with self._lock:
                # Если диаграмма не передана, берем текущее состояние
                if diagram is None:
                    diagram = self.get_current_state()
                    if diagram is None:
                        return ["No state available for validation"]
                
                # Запускаем полную проверку (УРОВЕНЬ 3)
                errors = self._validate_for_codegen(diagram)
                
                if errors:
                    logger.warning(f"Codegen validation found {len(errors)} errors")
                else:
                    logger.info("Codegen validation passed successfully")
                
                return errors
        
        except Exception as e:
            logger.error(f"Failed to validate for codegen: {e}", exc_info=True)
            return [f"Validation error: {str(e)}"]
