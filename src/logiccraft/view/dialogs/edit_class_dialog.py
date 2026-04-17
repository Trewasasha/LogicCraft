"""Диалог редактирования класса"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QPushButton, QInputDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt


class EditClassDialog(QDialog):
    """Диалог для редактирования класса"""

    def __init__(self, card, parent=None):
        super().__init__(parent)
        self.card = card
        self.setWindowTitle(f"Edit Class: {card.name}")
        self.setMinimumWidth(400)

        self._setup_ui()

    def _setup_ui(self):
        """Настройка UI диалога"""
        layout = QVBoxLayout()

        # Имя класса
        layout.addWidget(QLabel("Class Name:"))
        self.name_edit = QLineEdit(self.card.name)
        layout.addWidget(self.name_edit)

        # Атрибуты
        layout.addWidget(QLabel("Attributes:"))
        self.attrs_list = QListWidget()
        for attr in self.card.attributes:
            self.attrs_list.addItem(attr)
        layout.addWidget(self.attrs_list)

        # Кнопки для атрибутов
        attr_buttons = QHBoxLayout()
        add_attr = QPushButton("Add")
        add_attr.clicked.connect(self._add_attribute)
        remove_attr = QPushButton("Remove")
        remove_attr.clicked.connect(self._remove_attribute)
        attr_buttons.addWidget(add_attr)
        attr_buttons.addWidget(remove_attr)
        layout.addLayout(attr_buttons)

        # Методы
        layout.addWidget(QLabel("Methods:"))
        self.methods_list = QListWidget()
        for method in self.card.methods:
            self.methods_list.addItem(method)
        layout.addWidget(self.methods_list)

        # Кнопки для методов
        method_buttons = QHBoxLayout()
        add_method = QPushButton("Add")
        add_method.clicked.connect(self._add_method)
        remove_method = QPushButton("Remove")
        remove_method.clicked.connect(self._remove_method)
        method_buttons.addWidget(add_method)
        method_buttons.addWidget(remove_method)
        layout.addLayout(method_buttons)

        # Кнопки OK/Cancel
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def _add_attribute(self):
        """Добавить атрибут"""
        text, ok = QInputDialog.getText(
            self, "Add Attribute",
            "Attribute (e.g., +name: str):"
        )
        if ok and text:
            self.attrs_list.addItem(text)

    def _remove_attribute(self):
        """Удалить атрибут"""
        current = self.attrs_list.currentRow()
        if current >= 0:
            self.attrs_list.takeItem(current)

    def _add_method(self):
        """Добавить метод"""
        text, ok = QInputDialog.getText(
            self, "Add Method",
            "Method (e.g., +getName(): str):"
        )
        if ok and text:
            self.methods_list.addItem(text)

    def _remove_method(self):
        """Удалить метод"""
        current = self.methods_list.currentRow()
        if current >= 0:
            self.methods_list.takeItem(current)

    def get_data(self):
        """Получить данные из диалога"""
        attributes = [
            self.attrs_list.item(i).text()
            for i in range(self.attrs_list.count())
        ]
        methods = [
            self.methods_list.item(i).text()
            for i in range(self.methods_list.count())
        ]
        return self.name_edit.text(), attributes, methods