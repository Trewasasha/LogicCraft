"""Сервис для управления историей изменений (Undo/Redo)"""
import copy
from typing import Any, Optional, List
from PyQt6.QtCore import QObject, pyqtSignal


class HistoryService(QObject):
    """
    Сервис для отслеживания изменений состояния диаграммы.
    Реализует паттерн Command через стек состояний.
    """

    # Сигналы для обновления UI
    history_changed = pyqtSignal()  # Emit when undo/redo availability changes
    state_restored = pyqtSignal(object)  # Emit when state is restored (for views to update)

    def __init__(self, max_history: int = 50):
        """
        Инициализация сервиса истории.
        
        Args:
            max_history: Максимальное количество состояний в истории
        """
        super().__init__()
        self._stack: List[dict] = []
        self._current_index: int = -1
        self._max_history = max_history
        self._is_restoring = False  # Flag to prevent recording during restore

    def push_state(self, state: dict) -> None:
        """
        Добавить новое состояние в историю.
        
        Args:
            state: Состояние диаграммы для сохранения
        """
        if self._is_restoring:
            return  # Don't record states during undo/redo operations

        # Удаляем все состояния после текущего (очищаем redo стек)
        if self._current_index < len(self._stack) - 1:
            self._stack = self._stack[:self._current_index + 1]

        # Делаем глубокую копию состояния для предотвращения мутаций
        state_copy = copy.deepcopy(state)
        
        # Добавляем новое состояние
        self._stack.append(state_copy)
        self._current_index += 1

        # Ограничиваем размер истории
        if len(self._stack) > self._max_history:
            self._stack.pop(0)
            self._current_index -= 1

        self.history_changed.emit()

    def undo(self) -> Optional[dict]:
        """
        Отменить последнее действие.
        
        Returns:
            Предыдущее состояние или None, если отмена невозможна
        """
        if not self.can_undo():
            return None

        self._is_restoring = True
        self._current_index -= 1
        state = copy.deepcopy(self._stack[self._current_index])
        self._is_restoring = False

        self.history_changed.emit()
        self.state_restored.emit(state)
        
        return state

    def redo(self) -> Optional[dict]:
        """
        Повторить отмененное действие.
        
        Returns:
            Следующее состояние или None, если повтор невозможен
        """
        if not self.can_redo():
            return None

        self._is_restoring = True
        self._current_index += 1
        state = copy.deepcopy(self._stack[self._current_index])
        self._is_restoring = False

        self.history_changed.emit()
        self.state_restored.emit(state)
        
        return state

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
        self._stack.clear()
        self._current_index = -1
        self.history_changed.emit()

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

    def get_current_state(self) -> Optional[dict]:
        """
        Получить текущее состояние без изменения индекса.
        
        Returns:
            Текущее состояние или None
        """
        if 0 <= self._current_index < len(self._stack):
            return copy.deepcopy(self._stack[self._current_index])
        return None

    def has_history(self) -> bool:
        """
        Проверить, есть ли сохраненные состояния.
        
        Returns:
            True если в истории есть хотя бы одно состояние
        """
        return len(self._stack) > 0
