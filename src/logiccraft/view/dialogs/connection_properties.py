"""Диалог свойств связи"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QDialogButtonBox
)
from enum import Enum


class ConnectionType(Enum):
    """Типы связей"""
    ASSOCIATION = "association"
    INHERITANCE = "inheritance"
    COMPOSITION = "composition"
    AGGREGATION = "aggregation"


class ConnectionPropertiesDialog(QDialog):
    """Диалог для выбора типа связи"""

    def __init__(self, connection, parent=None):
        super().__init__(parent)
        self.connection = connection
        self.setWindowTitle("Connection Properties")
        self.setMinimumWidth(300)

        self._setup_ui()

    def _setup_ui(self):
        """Настройка UI диалога"""
        layout = QVBoxLayout()

        # Тип связи
        layout.addWidget(QLabel("Connection Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItem("Association", ConnectionType.ASSOCIATION.value)
        self.type_combo.addItem("Inheritance", ConnectionType.INHERITANCE.value)
        self.type_combo.addItem("Composition", ConnectionType.COMPOSITION.value)
        self.type_combo.addItem("Aggregation", ConnectionType.AGGREGATION.value)

        # Устанавливаем текущее значение
        # connection.type может быть либо строкой, либо объектом ConnectionType
        current_type = self.connection.type
        if hasattr(current_type, 'value'):
            # Если это объект ConnectionType
            current_value = current_type.value
        else:
            # Если это строка
            current_value = current_type

        index = self.type_combo.findData(current_value)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)

        layout.addWidget(self.type_combo)

        # Кнопки OK/Cancel
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_connection_type(self) -> ConnectionType:
        """Возвращает выбранный тип связи"""
        value = self.type_combo.currentData()
        for ct in ConnectionType:
            if ct.value == value:
                return ct
        return ConnectionType.ASSOCIATION