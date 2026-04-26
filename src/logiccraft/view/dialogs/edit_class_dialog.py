"""Диалог редактирования класса"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QPushButton, QInputDialog, QDialogButtonBox,
    QComboBox, QCheckBox, QStackedWidget, QWidget
)
from PyQt6.QtCore import Qt
from ..theme import DialogStyle
from ...models.diagram import NodeType


NODE_TYPE_LABELS = {
    NodeType.CLASS: "Класс",
    NodeType.ABSTRACT_CLASS: "Абстрактный класс",
    NodeType.INTERFACE: "Интерфейс",
    NodeType.ENUM: "Перечисление (Enum)",
}


class EditClassDialog(QDialog):
    """Диалог для редактирования класса"""

    def __init__(self, card, parent=None):
        super().__init__(parent)
        self.card = card
        self.setWindowTitle(f"Редактировать: {card.name}")
        self.setMinimumWidth(440)
        self.setMinimumHeight(540)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Имя
        layout.addWidget(QLabel("Название:"))
        self.name_edit = QLineEdit(self.card.name)
        layout.addWidget(self.name_edit)

        # Тип узла
        layout.addWidget(QLabel("Тип:"))
        self.type_combo = QComboBox()
        for node_type, label in NODE_TYPE_LABELS.items():
            self.type_combo.addItem(label, node_type)

        # Устанавливаем текущий тип
        current_type = getattr(self.card, 'node_type', NodeType.CLASS)
        if isinstance(current_type, str):
            current_type = NodeType(current_type)
        for i in range(self.type_combo.count()):
            if self.type_combo.itemData(i) == current_type:
                self.type_combo.setCurrentIndex(i)
                break
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        layout.addWidget(self.type_combo)

        # Стек: разные секции для разных типов
        self.stack = QStackedWidget()

        # Страница 0: CLASS / ABSTRACT_CLASS / INTERFACE — атрибуты + методы
        members_page = QWidget()
        members_layout = QVBoxLayout(members_page)
        members_layout.setContentsMargins(0, 0, 0, 0)
        members_layout.setSpacing(8)

        members_layout.addWidget(QLabel("Атрибуты:"))
        self.attrs_list = QListWidget()
        self.attrs_list.setMinimumHeight(110)
        for attr in self.card.attributes:
            self.attrs_list.addItem(attr)
        members_layout.addWidget(self.attrs_list)

        attr_btns = QHBoxLayout()
        add_attr = QPushButton("+ Добавить")
        add_attr.clicked.connect(self._add_attribute)
        rm_attr = QPushButton("Удалить")
        rm_attr.clicked.connect(self._remove_attribute)
        attr_btns.addWidget(add_attr)
        attr_btns.addWidget(rm_attr)
        attr_btns.addStretch()
        members_layout.addLayout(attr_btns)

        members_layout.addWidget(QLabel("Методы:"))
        self.methods_list = QListWidget()
        self.methods_list.setMinimumHeight(110)
        for method in self.card.methods:
            self.methods_list.addItem(method)
        members_layout.addWidget(self.methods_list)

        method_btns = QHBoxLayout()
        add_method = QPushButton("+ Добавить")
        add_method.clicked.connect(self._add_method)
        rm_method = QPushButton("Удалить")
        rm_method.clicked.connect(self._remove_method)
        method_btns.addWidget(add_method)
        method_btns.addWidget(rm_method)
        method_btns.addStretch()
        members_layout.addLayout(method_btns)

        self.stack.addWidget(members_page)  # index 0

        # Страница 1: ENUM — только литералы
        enum_page = QWidget()
        enum_layout = QVBoxLayout(enum_page)
        enum_layout.setContentsMargins(0, 0, 0, 0)
        enum_layout.setSpacing(8)

        enum_layout.addWidget(QLabel("Значения (литералы):"))
        self.enum_list = QListWidget()
        self.enum_list.setMinimumHeight(200)
        # Заполняем из card.attributes (используем как хранилище строк)
        enum_attrs = getattr(self.card, 'attributes', [])
        for item in enum_attrs:
            self.enum_list.addItem(item)
        enum_layout.addWidget(self.enum_list)

        enum_btns = QHBoxLayout()
        add_enum = QPushButton("+ Добавить")
        add_enum.clicked.connect(self._add_enum_literal)
        rm_enum = QPushButton("Удалить")
        rm_enum.clicked.connect(self._remove_enum_literal)
        enum_btns.addWidget(add_enum)
        enum_btns.addWidget(rm_enum)
        enum_btns.addStretch()
        enum_layout.addLayout(enum_btns)
        enum_layout.addStretch()

        self.stack.addWidget(enum_page)  # index 1

        layout.addWidget(self.stack)

        # Кнопки OK/Cancel
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)
        self._on_type_changed()  # установить правильную страницу

    def _on_type_changed(self):
        node_type = self.type_combo.currentData()
        if node_type == NodeType.ENUM:
            self.stack.setCurrentIndex(1)
        else:
            self.stack.setCurrentIndex(0)

    def _add_attribute(self):
        text, ok = QInputDialog.getText(self, "Добавить атрибут", "Атрибут (например: +name: str):")
        if ok and text:
            self.attrs_list.addItem(text)

    def _remove_attribute(self):
        row = self.attrs_list.currentRow()
        if row >= 0:
            self.attrs_list.takeItem(row)

    def _add_method(self):
        text, ok = QInputDialog.getText(self, "Добавить метод", "Метод (например: +getName(): str):")
        if ok and text:
            self.methods_list.addItem(text)

    def _remove_method(self):
        row = self.methods_list.currentRow()
        if row >= 0:
            self.methods_list.takeItem(row)

    def _add_enum_literal(self):
        text, ok = QInputDialog.getText(self, "Добавить значение", "Значение (например: RED или RED = 1):")
        if ok and text:
            self.enum_list.addItem(text)

    def _remove_enum_literal(self):
        row = self.enum_list.currentRow()
        if row >= 0:
            self.enum_list.takeItem(row)

    def get_data(self):
        """Возвращает (name, attributes, methods, node_type)"""
        node_type = self.type_combo.currentData()

        if node_type == NodeType.ENUM:
            attributes = [self.enum_list.item(i).text() for i in range(self.enum_list.count())]
            methods = []
        else:
            attributes = [self.attrs_list.item(i).text() for i in range(self.attrs_list.count())]
            methods = [self.methods_list.item(i).text() for i in range(self.methods_list.count())]

        return self.name_edit.text(), attributes, methods, node_type
