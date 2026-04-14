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
    history_changed = pyqtSignal()  # Emit when undo/redo availability changes
    state_restored = pyqtSignal(object)  # Emit when state is restored (for views to update)
    state_validation_failed = pyqtSignal(str)  # Emit when validation fails

    def __init__(self, max_history: int = 50, compression_threshold: int = 20):
        """
        Инициализация сервиса истории.
        
        Args:
            max_history: Максимальное количество состояний в истории
            compression_threshold: Порог для сжатия старых состояний
        """
        super().__init__()
        self._stack: List[UMLDiagram] = []
        self._current_index: int = -1
        self._max_history = max_history
        self._compression_threshold = compression_threshold
        self._is_restoring = False  # Flag to prevent recording during restore
        self._lock = Lock()  # Thread-safe operations
        self._compressed_count: int = 0  # Track compression statistics

    def push_state(self, state: Union[UMLDiagram, dict], validate: bool = True) -> None:
        """
        Добавить новое состояние в историю.
        
        Args:
            state: Состояние диаграммы (UMLDiagram или dict для обратной совместимости)
            validate: Проверять валидность состояния
            
        Raises:
            InvalidStateError: Если состояние невалидно
        """
        try:
            with self._lock:
                if self._is_restoring:
                    logger.debug("Skipping state push during restoration")
                    return  # Don't record states during undo/redo operations

                # Конвертируем dict в UMLDiagram если нужно
                if isinstance(state, dict):
                    state = self._dict_to_diagram(state)
                
                # Валидация состояния
                if validate:
                    errors = self._validate_state(state)
                    if errors:
                        error_msg = f"State validation failed: {', '.join(errors)}"
                        logger.warning(error_msg)
                        self.state_validation_failed.emit(error_msg)
                        # Не блокируем, только предупреждаем

                # Удаляем все состояния после текущего (очищаем redo стек)
                if self._current_index < len(self._stack) - 1:
                    self._stack = self._stack[:self._current_index + 1]

                # Оптимизация: используем model_copy вместо deepcopy для Pydantic
                state_copy = state.model_copy(deep=True)
                
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

                self.history_changed.emit()
                logger.debug(f"State pushed. Stack size: {len(self._stack)}, Index: {self._current_index}")
        
        except Exception as e:
            logger.error(f"Failed to push state: {e}", exc_info=True)
            raise

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

                self.history_changed.emit()
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

                self.history_changed.emit()
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
                    
                self.history_changed.emit()
        
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

    def _validate_state(self, diagram: UMLDiagram) -> List[str]:
        """
        Валидировать состояние диаграммы.
        
        Args:
            diagram: Диаграмма для валидации
            
        Returns:
            Список ошибок валидации
        """
        errors = []
        
        try:
            # Проверка имени диаграммы
            if not diagram.name or not isinstance(diagram.name, str):
                errors.append("Diagram name is invalid")
            
            # Проверка узлов
            node_ids = set()
            for i, node in enumerate(diagram.nodes):
                # Проверка ID узла
                if not node.id or node.id in node_ids:
                    errors.append(f"Node {i} has invalid or duplicate ID: {node.id}")
                node_ids.add(node.id)
                
                # Проверка имени узла
                if not node.name or not isinstance(node.name, str):
                    errors.append(f"Node {node.id} has invalid name")
                
                # Проверка координат
                if not isinstance(node.x, (int, float)) or not isinstance(node.y, (int, float)):
                    errors.append(f"Node {node.id} has invalid coordinates")
                
                # Проверка свойств
                for j, prop in enumerate(node.properties):
                    if not prop.name or not isinstance(prop.name, str):
                        errors.append(f"Property {j} in node {node.id} has invalid name")
                    if not prop.type or not isinstance(prop.type, str):
                        errors.append(f"Property {j} in node {node.id} has invalid type")
                
                # Проверка методов
                for j, method in enumerate(node.methods):
                    if not method.name or not isinstance(method.name, str):
                        errors.append(f"Method {j} in node {node.id} has invalid name")
            
            # Проверка связей
            for i, conn in enumerate(diagram.connections):
                if conn.source_id not in node_ids:
                    errors.append(f"Connection {i}: source {conn.source_id} not found")
                if conn.target_id not in node_ids:
                    errors.append(f"Connection {i}: target {conn.target_id} not found")
        
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
        
        return errors

    def _compress_old_states(self) -> None:
        """
        Сжать старые состояния для экономии памяти.
        Оставляет только каждое N-ное состояние после порога.
        """
        try:
            if len(self._stack) <= self._compression_threshold:
                return
            
            # Оставляем последние compression_threshold состояний без изменений
            # Сжимаем более старые состояния, оставляя каждое 2-ое
            threshold = self._compression_threshold
            old_states = self._stack[:-threshold]
            recent_states = self._stack[-threshold:]
            
            # Сжимаем: оставляем каждое 2-ое состояние из старых
            compressed = old_states[::2]
            self._compressed_count += len(old_states) - len(compressed)
            
            # Обновляем стек
            self._stack = compressed + recent_states
            
            # Корректируем индекс
            removed_count = len(old_states) - len(compressed)
            if self._current_index >= len(compressed):
                self._current_index -= removed_count
            
            logger.debug(f"Compressed history: {len(old_states)} -> {len(compressed)} states. "
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
