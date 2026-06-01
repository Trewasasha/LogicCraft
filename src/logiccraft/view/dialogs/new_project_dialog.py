"""Одностраничный диалог создания нового проекта"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QRadioButton, QCheckBox, QGroupBox,
    QFileDialog, QButtonGroup, QGridLayout, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QFont
from pathlib import Path

from logiccraft.utils.icon_manager import icon_manager


class DiagramTypeButton(QPushButton):
    """Компактная кнопка выбора типа диаграммы"""

    def __init__(self, diagram_type: str, label: str, is_available: bool = True):
        super().__init__()
        self.diagram_type = diagram_type
        self.is_available = is_available
        self.setCheckable(True)
        self.setFixedSize(80, 90)

        if is_available:
            self.setObjectName("DiagramTypeButton")
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setObjectName("DiagramTypeButtonDisabled")
            self.setCursor(Qt.CursorShape.ForbiddenCursor)
            self.setEnabled(False)

        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(8, 8, 8, 8)

        # Название
        name_label = QLabel(label)
        name_label.setObjectName("DiagramTypeLabel")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setWordWrap(True)
        layout.addWidget(name_label)


class NewProjectDialog(QDialog):
    """Одностраничный диалог создания проекта"""

    project_created = pyqtSignal(dict)  # project_config

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создание нового проекта")
        self.setFixedSize(700, 750)
        self.setModal(True)
        self.setObjectName("NewProjectDialog")

        self.diagram_type_group = QButtonGroup(self)
        self._setup_ui()
        self._set_defaults()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Заголовок
        title = QLabel("Создание нового проекта")
        title.setObjectName("NewProjectDialogTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Скролл-область
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setObjectName("NewProjectScrollArea")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        scroll_layout.setContentsMargins(0, 0, 10, 0)

        # ─── Основная информация ───
        info_group = QGroupBox("Основная информация")
        info_group.setObjectName("ProjectGroupBox")
        info_layout = QVBoxLayout()
        info_layout.setSpacing(12)

        # Название проекта
        name_layout = QHBoxLayout()
        name_label = QLabel("Название проекта: *")
        name_label.setObjectName("ProjectFieldLabel")
        name_label.setFixedWidth(140)
        self.name_input = QLineEdit()
        self.name_input.setObjectName("ProjectInput")
        self.name_input.setPlaceholderText("MyProject")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        info_layout.addLayout(name_layout)

        # Путь сохранения
        path_layout = QHBoxLayout()
        path_label = QLabel("Сохранить в:")
        path_label.setObjectName("ProjectFieldLabel")
        path_label.setFixedWidth(140)
        self.path_input = QLineEdit()
        self.path_input.setObjectName("ProjectInput")
        self.path_input.setPlaceholderText("~/Documents/LogicCraft")
        browse_btn = QPushButton()
        browse_btn.setIcon(icon_manager.get_icon("folder"))
        browse_btn.setObjectName("BrowseButton")
        browse_btn.setFixedSize(36, 36)
        browse_btn.clicked.connect(self._browse_path)
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_btn)
        info_layout.addLayout(path_layout)

        # Автор
        author_layout = QHBoxLayout()
        author_label = QLabel("Автор:")
        author_label.setObjectName("ProjectFieldLabel")
        author_label.setFixedWidth(140)
        self.author_input = QLineEdit()
        self.author_input.setObjectName("ProjectInput")
        self.author_input.setPlaceholderText("Ваше имя")
        author_layout.addWidget(author_label)
        author_layout.addWidget(self.author_input)
        info_layout.addLayout(author_layout)

        info_group.setLayout(info_layout)
        scroll_layout.addWidget(info_group)

        # ─── Тип диаграммы ───
        diagram_group = QGroupBox("Тип диаграммы")
        diagram_group.setObjectName("ProjectGroupBox")
        diagram_layout = QVBoxLayout()
        diagram_layout.setSpacing(10)

        # Сетка кнопок типов
        types_grid = QGridLayout()
        types_grid.setSpacing(10)

        diagram_types = [
            ("class", "Классы", True),
            ("use_case", "Use Case", True),
            ("sequence", "Sequence", False),
            ("package", "Package", False),
            ("activity", "Activity", False),
            ("state", "State", False),
        ]

        row, col = 0, 0
        for dtype, label, available in diagram_types:
            btn = DiagramTypeButton(dtype, label, available)
            self.diagram_type_group.addButton(btn)
            types_grid.addWidget(btn, row, col)
            col += 1
            if col >= 4:
                col = 0
                row += 1

        diagram_layout.addLayout(types_grid)
        diagram_group.setLayout(diagram_layout)
        scroll_layout.addWidget(diagram_group)

        # ─── Настройки кода ───
        code_group = QGroupBox("Настройки генерации кода")
        code_group.setObjectName("ProjectGroupBox")
        code_layout = QVBoxLayout()
        code_layout.setSpacing(12)

        # Язык программирования
        lang_layout = QHBoxLayout()
        lang_label = QLabel("Язык:")
        lang_label.setObjectName("ProjectFieldLabel")
        lang_label.setFixedWidth(140)
        self.language_combo = QComboBox()
        self.language_combo.setObjectName("ProjectComboBox")
        self.language_combo.addItems(["Python 3.x", "Java 11+"])
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.language_combo)
        code_layout.addLayout(lang_layout)

        # Архитектурный шаблон
        arch_layout = QHBoxLayout()
        arch_label = QLabel("Архитектура:")
        arch_label.setObjectName("ProjectFieldLabel")
        arch_label.setFixedWidth(140)
        self.architecture_combo = QComboBox()
        self.architecture_combo.setObjectName("ProjectComboBox")
        self.architecture_combo.addItems(["Simple", "MVC", "Clean Architecture", "Layered"])
        arch_layout.addWidget(arch_label)
        arch_layout.addWidget(self.architecture_combo)
        code_layout.addLayout(arch_layout)

        # Стиль кода
        style_layout = QHBoxLayout()
        style_label = QLabel("Стиль кода:")
        style_label.setObjectName("ProjectFieldLabel")
        style_label.setFixedWidth(140)
        self.snake_case_radio = QRadioButton("snake_case")
        self.snake_case_radio.setObjectName("ProjectRadio")
        self.camel_case_radio = QRadioButton("camelCase")
        self.camel_case_radio.setObjectName("ProjectRadio")
        self.snake_case_radio.setChecked(True)
        style_layout.addWidget(style_label)
        style_layout.addWidget(self.snake_case_radio)
        style_layout.addWidget(self.camel_case_radio)
        style_layout.addStretch()
        code_layout.addLayout(style_layout)

        # Дополнительные опции
        options_layout = QHBoxLayout()
        options_label = QLabel("Дополнительно:")
        options_label.setObjectName("ProjectFieldLabel")
        options_label.setFixedWidth(140)

        options_col = QVBoxLayout()
        options_col.setSpacing(6)

        self.docstrings_check = QCheckBox("Генерировать docstrings")
        self.docstrings_check.setObjectName("ProjectCheckBox")
        self.docstrings_check.setChecked(True)

        self.type_hints_check = QCheckBox("Добавить type hints")
        self.type_hints_check.setObjectName("ProjectCheckBox")
        self.type_hints_check.setChecked(True)

        self.git_init_check = QCheckBox("Создать Git репозиторий")
        self.git_init_check.setObjectName("ProjectCheckBox")

        self.gitignore_check = QCheckBox("Добавить .gitignore")
        self.gitignore_check.setObjectName("ProjectCheckBox")

        options_col.addWidget(self.docstrings_check)
        options_col.addWidget(self.type_hints_check)
        options_col.addWidget(self.git_init_check)
        options_col.addWidget(self.gitignore_check)

        options_layout.addWidget(options_label)
        options_layout.addLayout(options_col)
        options_layout.addStretch()
        code_layout.addLayout(options_layout)

        code_group.setLayout(code_layout)
        scroll_layout.addWidget(code_group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("SecondaryButton")
        cancel_btn.setFixedHeight(40)
        cancel_btn.setMinimumWidth(120)
        cancel_btn.clicked.connect(self.reject)

        create_btn = QPushButton("Создать проект")
        create_btn.setObjectName("PrimaryButton")
        create_btn.setFixedHeight(40)
        create_btn.setMinimumWidth(140)
        create_btn.clicked.connect(self._create_project)

        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(create_btn)

        main_layout.addLayout(buttons_layout)

    def _set_defaults(self):
        """Установить значения по умолчанию"""
        # Путь по умолчанию
        default_path = Path.home() / "Documents" / "LogicCraft"
        self.path_input.setText(str(default_path))

        # Выбрать первый доступный тип диаграммы
        for btn in self.diagram_type_group.buttons():
            if btn.isEnabled():
                btn.setChecked(True)
                break

    def _browse_path(self):
        """Выбрать путь сохранения"""
        path = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку для проекта",
            str(Path.home())
        )
        if path:
            self.path_input.setText(path)

    def _create_project(self):
        """Создать проект с выбранными настройками"""
        # Валидация
        name = self.name_input.text().strip()
        if not name:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", "Введите название проекта")
            return

        path = self.path_input.text().strip()
        if not path:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", "Выберите путь сохранения")
            return

        # Получить выбранный тип диаграммы
        diagram_type = None
        for btn in self.diagram_type_group.buttons():
            if btn.isChecked():
                diagram_type = btn.diagram_type
                break

        if not diagram_type:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", "Выберите тип диаграммы")
            return

        # Собрать конфигурацию проекта
        config = {
            "name": name,
            "path": path,
            "author": self.author_input.text().strip(),
            "diagram_type": diagram_type,
            "language": self.language_combo.currentText(),
            "architecture": self.architecture_combo.currentText(),
            "code_style": "snake_case" if self.snake_case_radio.isChecked() else "camelCase",
            "docstrings": self.docstrings_check.isChecked(),
            "type_hints": self.type_hints_check.isChecked(),
            "git_init": self.git_init_check.isChecked(),
            "gitignore": self.gitignore_check.isChecked(),
        }

        self.project_created.emit(config)
        self.accept()

    def get_project_config(self) -> dict:
        """Получить конфигурацию проекта"""
        return {
            "name": self.name_input.text().strip(),
            "path": self.path_input.text().strip(),
            "author": self.author_input.text().strip(),
            "diagram_type": next((btn.diagram_type for btn in self.diagram_type_group.buttons() if btn.isChecked()), "class"),
            "language": self.language_combo.currentText(),
            "architecture": self.architecture_combo.currentText(),
            "code_style": "snake_case" if self.snake_case_radio.isChecked() else "camelCase",
            "docstrings": self.docstrings_check.isChecked(),
            "type_hints": self.type_hints_check.isChecked(),
            "git_init": self.git_init_check.isChecked(),
            "gitignore": self.gitignore_check.isChecked(),
        }
