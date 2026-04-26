"""Диалог свойств связи"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QDialogButtonBox, QLineEdit, QFormLayout, QGroupBox
)
from PyQt6.QtCore import Qt
from logiccraft.models.diagram import ConnectionType


CONNECTION_TYPE_LABELS = [
    ("→  Ассоциация",    "association"),
    ("▷  Наследование",  "inheritance"),
    ("◆  Композиция",    "composition"),
    ("◇  Агрегация",     "aggregation"),
    ("⇢  Зависимость",   "dependency"),
    ("⇒  Реализация",    "realization"),
]

MULTIPLICITY_PRESETS = [
    "", "1", "0..1", "0..*", "1..*", "*", "1..1", "n", "m..n"
]


class ConnectionPropertiesDialog(QDialog):
    """Диалог для редактирования свойств связи"""

    def __init__(self, connection, parent=None):
        super().__init__(parent)
        self.connection = connection
        self.setWindowTitle("Свойства связи")
        self.setMinimumWidth(360)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- Тип связи ---
        type_group = QGroupBox("Тип связи")
        type_layout = QVBoxLayout(type_group)
        self.type_combo = QComboBox()
        for label, value in CONNECTION_TYPE_LABELS:
            self.type_combo.addItem(label, value)

        current_type = self.connection.type
        current_value = current_type.value if hasattr(current_type, 'value') else str(current_type)
        idx = self.type_combo.findData(current_value)
        if idx >= 0:
            self.type_combo.setCurrentIndex(idx)
        type_layout.addWidget(self.type_combo)
        layout.addWidget(type_group)

        # --- Множественность ---
        mult_group = QGroupBox("Множественность")
        mult_layout = QFormLayout(mult_group)
        mult_layout.setSpacing(8)

        self.source_mult = QComboBox()
        self.source_mult.setEditable(True)
        for p in MULTIPLICITY_PRESETS:
            self.source_mult.addItem(p)

        self.target_mult = QComboBox()
        self.target_mult.setEditable(True)
        for p in MULTIPLICITY_PRESETS:
            self.target_mult.addItem(p)

        # Заполняем текущие значения
        current_mult = getattr(self.connection, 'multiplicity', None) or ""
        parts = current_mult.split("..") if ".." in current_mult else [current_mult, ""]
        # Если multiplicity хранится как "source:target"
        if ":" in current_mult:
            src_m, tgt_m = current_mult.split(":", 1)
        else:
            src_m, tgt_m = "", current_mult

        self.source_mult.setCurrentText(src_m)
        self.target_mult.setCurrentText(tgt_m)

        mult_layout.addRow("Источник:", self.source_mult)
        mult_layout.addRow("Цель:", self.target_mult)
        layout.addWidget(mult_group)

        # --- Имя связи ---
        name_group = QGroupBox("Имя связи (необязательно)")
        name_layout = QVBoxLayout(name_group)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Например: использует, содержит...")
        current_name = getattr(self.connection, 'name', None) or ""
        self.name_edit.setText(current_name)
        name_layout.addWidget(self.name_edit)
        layout.addWidget(name_group)

        # --- Кнопки ---
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_connection_type(self) -> ConnectionType:
        value = self.type_combo.currentData()
        try:
            return ConnectionType(value)
        except ValueError:
            return ConnectionType.association

    def get_multiplicity(self) -> str:
        """Возвращает множественность в формате 'source:target'"""
        src = self.source_mult.currentText().strip()
        tgt = self.target_mult.currentText().strip()
        if src or tgt:
            return f"{src}:{tgt}"
        return ""

    def get_name(self) -> str:
        return self.name_edit.text().strip()
