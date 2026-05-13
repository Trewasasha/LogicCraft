"""Inline редактор для быстрого редактирования текста"""
from PyQt6.QtWidgets import QGraphicsTextItem, QGraphicsItem
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QTextCursor, QColor, QFont


class InlineEditorSignals(QObject):
    """Сигналы для inline редактора"""
    editing_finished = pyqtSignal(str)  # new_text
    editing_cancelled = pyqtSignal()


class InlineEditor(QGraphicsTextItem):
    """Inline редактор текста на сцене"""
    
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.signals = InlineEditorSignals()
        self._original_text = text
        
        # Настройка редактора
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)
        
        # Стиль
        self.setDefaultTextColor(QColor("#1F1F1F"))
        font = QFont("Inter", 13)
        font.setBold(True)
        self.setFont(font)
        
        # Выделяем весь текст
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        self.setTextCursor(cursor)
        
        # Устанавливаем фокус
        self.setFocus()
    
    def keyPressEvent(self, event):
        """Обработка клавиш"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Enter - сохранить
            self._finish_editing()
            event.accept()
        elif event.key() == Qt.Key.Key_Escape:
            # Escape - отменить
            self._cancel_editing()
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def focusOutEvent(self, event):
        """При потере фокуса - сохранить изменения"""
        super().focusOutEvent(event)
        self._finish_editing()
    
    def _finish_editing(self):
        """Завершить редактирование и сохранить"""
        new_text = self.toPlainText().strip()
        if new_text and new_text != self._original_text:
            self.signals.editing_finished.emit(new_text)
        else:
            self.signals.editing_cancelled.emit()
    
    def _cancel_editing(self):
        """Отменить редактирование"""
        self.signals.editing_cancelled.emit()
