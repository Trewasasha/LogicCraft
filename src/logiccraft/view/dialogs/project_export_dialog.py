"""Диалог экспорта проекта с настройками генерации"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QCheckBox, QPushButton,
    QGroupBox, QFileDialog, QMessageBox, QTreeWidget, QTreeWidgetItem,
    QTabWidget, QWidget, QTextEdit, QSplitter, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from pathlib import Path
from typing import Optional

from ...models.diagram import UMLDiagram
from ...models.project_settings import ProjectSettings, CodeStyleSettings
from ...services.project_exporter import ProjectExporter


class ExportWorker(QThread):
    """Фоновый поток для экспорта"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, diagram: UMLDiagram, settings: ProjectSettings, export_path: str):
        super().__init__()
        self.diagram = diagram
        self.settings = settings
        self.export_path = export_path

    def run(self):
        try:
            self.progress.emit(10, "Создание структуры папок...")
            exporter = ProjectExporter()
            self.progress.emit(40, "Генерация кода классов...")
            result = exporter.export_project(self.diagram, self.settings, self.export_path)
            self.progress.emit(100, "Готово!")
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class ProjectExportDialog(QDialog):
    """Диалог настройки и запуска экспорта проекта"""

    LANGUAGES = ["python", "java", "javascript", "typescript", "csharp"]
    STRUCTURES = ["simple", "mvc", "layered", "clean_architecture"]
    STRUCTURE_LABELS = {
        "simple": "Simple",
        "mvc": "MVC",
        "layered": "Layered Architecture",
        "clean_architecture": "Clean Architecture",
    }
    PACKAGE_MANAGERS = {
        "python": ["pip", "poetry", "pipenv"],
        "java": ["maven", "gradle"],
        "javascript": ["npm", "yarn", "pnpm"],
        "typescript": ["npm", "yarn", "pnpm"],
        "csharp": ["nuget"],
    }
    LICENSES = ["", "MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause"]

    def __init__(self, diagram: UMLDiagram, parent=None):
        super().__init__(parent)
        self.diagram = diagram
        self.exporter = ProjectExporter()
        self._worker: Optional[ExportWorker] = None

        self.setWindowTitle("📦 Экспорт проекта")
        self.setModal(True)
        self.resize(900, 680)

        self._build_ui()
        self._connect_signals()
        self._refresh_preview()

    # ─── UI construction ────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)

        tabs = QTabWidget()
        tabs.addTab(self._tab_basic(), "⚙️ Основные")
        tabs.addTab(self._tab_codestyle(), "🎨 Стиль кода")
        tabs.addTab(self._tab_extras(), "📁 Доп. файлы")
        tabs.addTab(self._tab_preview(), "👁 Предпросмотр")
        root.addWidget(tabs)

        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_label = QLabel("")
        root.addWidget(self.progress_label)
        root.addWidget(self.progress_bar)

        # Buttons
        btn_row = QHBoxLayout()
        self.btn_export = QPushButton("🚀 Экспортировать")
        self.btn_export.setDefault(True)
        btn_cancel = QPushButton("Отмена")
        btn_row.addStretch()
        btn_row.addWidget(self.btn_export)
        btn_row.addWidget(btn_cancel)
        root.addLayout(btn_row)

        btn_cancel.clicked.connect(self.reject)
        self.btn_export.clicked.connect(self._on_export)

    def _tab_basic(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        # Project metadata
        meta = QGroupBox("Метаданные проекта")
        form = QFormLayout(meta)

        self.edit_name = QLineEdit("MyProject")
        self.edit_author = QLineEdit()
        self.edit_description = QLineEdit()
        self.edit_version = QLineEdit("1.0.0")
        self.combo_license = QComboBox()
        self.combo_license.addItems(self.LICENSES)

        form.addRow("Название *:", self.edit_name)
        form.addRow("Автор:", self.edit_author)
        form.addRow("Описание:", self.edit_description)
        form.addRow("Версия:", self.edit_version)
        form.addRow("Лицензия:", self.combo_license)
        layout.addWidget(meta)

        # Language & structure
        lang_grp = QGroupBox("Язык и архитектура")
        lang_form = QFormLayout(lang_grp)

        self.combo_language = QComboBox()
        self.combo_language.addItems(self.LANGUAGES)

        self.combo_structure = QComboBox()
        for key, label in self.STRUCTURE_LABELS.items():
            self.combo_structure.addItem(label, key)

        self.combo_pkg_manager = QComboBox()

        lang_form.addRow("Язык:", self.combo_language)
        lang_form.addRow("Структура:", self.combo_structure)
        lang_form.addRow("Пакетный менеджер:", self.combo_pkg_manager)
        layout.addWidget(lang_grp)

        # Export path
        path_grp = QGroupBox("Путь экспорта")
        path_row = QHBoxLayout(path_grp)
        self.edit_path = QLineEdit()
        self.edit_path.setPlaceholderText("Выберите папку...")
        btn_browse = QPushButton("Обзор...")
        btn_browse.clicked.connect(self._browse_path)
        path_row.addWidget(self.edit_path)
        path_row.addWidget(btn_browse)
        layout.addWidget(path_grp)

        layout.addStretch()
        self._update_pkg_managers()
        return w

    def _tab_codestyle(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)

        self.combo_indent = QComboBox()
        self.combo_indent.addItems(["4 пробела", "2 пробела", "Табуляция"])

        self.combo_naming_class = QComboBox()
        self.combo_naming_class.addItems(["PascalCase", "camelCase", "snake_case"])

        self.combo_naming_method = QComboBox()
        self.combo_naming_method.addItems(["camelCase", "snake_case", "PascalCase"])

        self.chk_constructors = QCheckBox("Генерировать конструкторы")
        self.chk_constructors.setChecked(True)
        self.chk_getters = QCheckBox("Генерировать геттеры/сеттеры")
        self.chk_docstrings = QCheckBox("Добавлять документацию (docstrings)")
        self.chk_docstrings.setChecked(True)
        self.chk_type_hints = QCheckBox("Добавлять аннотации типов")
        self.chk_type_hints.setChecked(True)

        form.addRow("Отступы:", self.combo_indent)
        form.addRow("Именование классов:", self.combo_naming_class)
        form.addRow("Именование методов:", self.combo_naming_method)
        form.addRow("", self.chk_constructors)
        form.addRow("", self.chk_getters)
        form.addRow("", self.chk_docstrings)
        form.addRow("", self.chk_type_hints)
        return w

    def _tab_extras(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        grp = QGroupBox("Дополнительные файлы")
        vbox = QVBoxLayout(grp)

        self.chk_readme = QCheckBox("README.md")
        self.chk_readme.setChecked(True)
        self.chk_gitignore = QCheckBox(".gitignore")
        self.chk_gitignore.setChecked(True)
        self.chk_tests = QCheckBox("Тестовые файлы")
        self.chk_docs = QCheckBox("Папка документации (docs/)")
        self.chk_license_file = QCheckBox("Файл лицензии (LICENSE)")
        self.chk_ci = QCheckBox("GitHub Actions CI (.github/workflows/ci.yml)")

        for chk in [self.chk_readme, self.chk_gitignore, self.chk_tests,
                    self.chk_docs, self.chk_license_file, self.chk_ci]:
            vbox.addWidget(chk)

        layout.addWidget(grp)
        layout.addStretch()
        return w

    def _tab_preview(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        self.preview_tree = QTreeWidget()
        self.preview_tree.setHeaderLabel("Структура проекта")
        self.preview_tree.setFont(QFont("Monospace", 9))

        self.preview_stats = QLabel()
        btn_refresh = QPushButton("🔄 Обновить")
        btn_refresh.clicked.connect(self._refresh_preview)

        layout.addWidget(self.preview_tree)
        layout.addWidget(self.preview_stats)
        layout.addWidget(btn_refresh)
        return w

    # ─── Signals ────────────────────────────────────────────────────────────────

    def _connect_signals(self):
        self.combo_language.currentTextChanged.connect(self._on_language_changed)
        self.combo_language.currentTextChanged.connect(self._refresh_preview)
        self.combo_structure.currentIndexChanged.connect(self._refresh_preview)
        self.chk_tests.toggled.connect(self._refresh_preview)
        self.chk_docs.toggled.connect(self._refresh_preview)
        self.chk_ci.toggled.connect(self._refresh_preview)
        self.edit_name.textChanged.connect(self._refresh_preview)

    def _on_language_changed(self, lang: str):
        self._update_pkg_managers()

    def _update_pkg_managers(self):
        lang = self.combo_language.currentText()
        self.combo_pkg_manager.clear()
        self.combo_pkg_manager.addItems(self.PACKAGE_MANAGERS.get(lang, []))

    def _browse_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку для экспорта")
        if folder:
            self.edit_path.setText(folder)

    # ─── Preview ────────────────────────────────────────────────────────────────

    def _build_settings(self) -> Optional[ProjectSettings]:
        name = self.edit_name.text().strip()
        if not name:
            return None
        lang = self.combo_language.currentText()
        struct = self.combo_structure.currentData() or "simple"
        try:
            s = ProjectSettings(
                name=name,
                language=lang,
                structure_type=struct,
                author=self.edit_author.text().strip(),
                description=self.edit_description.text().strip(),
                version=self.edit_version.text().strip() or "1.0.0",
                license=self.combo_license.currentText() or None,
                package_manager=self.combo_pkg_manager.currentText() or None,
                include_tests=self.chk_tests.isChecked(),
                include_docs=self.chk_docs.isChecked(),
                include_readme=self.chk_readme.isChecked(),
                include_gitignore=self.chk_gitignore.isChecked(),
                include_license=self.chk_license_file.isChecked(),
                include_ci=self.chk_ci.isChecked(),
                export_path=self.edit_path.text().strip(),
            )
            # Apply code style
            indent_map = {"4 пробела": ("spaces", 4), "2 пробела": ("spaces", 2), "Табуляция": ("tabs", 1)}
            itype, isize = indent_map.get(self.combo_indent.currentText(), ("spaces", 4))
            s.code_style.set_indentation(itype, isize)
            s.code_style.naming_convention["class"] = self.combo_naming_class.currentText()
            s.code_style.naming_convention["method"] = self.combo_naming_method.currentText()
            s.code_style.include_constructors = self.chk_constructors.isChecked()
            s.code_style.include_getters_setters = self.chk_getters.isChecked()
            s.code_style.include_docstrings = self.chk_docstrings.isChecked()
            s.code_style.include_type_hints = self.chk_type_hints.isChecked()
            return s
        except Exception:
            return None

    def _refresh_preview(self):
        settings = self._build_settings()
        if not settings:
            self.preview_tree.clear()
            return
        try:
            structure = self.exporter.preview_structure(settings)
            self.preview_tree.clear()
            root_item = QTreeWidgetItem([settings.name])
            self.preview_tree.addTopLevelItem(root_item)
            self._populate_tree(root_item, structure)
            root_item.setExpanded(True)

            files = self.exporter.get_flat_file_list(structure)
            self.preview_stats.setText(f"Файлов: {len(files)}")
        except Exception as e:
            self.preview_stats.setText(f"Ошибка предпросмотра: {e}")

    def _populate_tree(self, parent: QTreeWidgetItem, structure: dict):
        for name, child in structure.get("children", {}).items():
            item = QTreeWidgetItem([name])
            parent.addChild(item)
            if child.get("type") == "directory":
                self._populate_tree(item, child)

    # ─── Export ─────────────────────────────────────────────────────────────────

    def _on_export(self):
        settings = self._build_settings()
        if not settings:
            QMessageBox.warning(self, "Ошибка", "Укажите корректное название проекта.")
            return

        export_path = self.edit_path.text().strip()
        if not export_path:
            QMessageBox.warning(self, "Ошибка", "Укажите папку для экспорта.")
            return

        errors = settings.validate()
        if errors:
            QMessageBox.warning(self, "Ошибка валидации", "\n".join(errors))
            return

        # Check if diagram is empty
        if not self.diagram.nodes:
            reply = QMessageBox.question(
                self, "Пустая диаграмма",
                "Диаграмма не содержит классов. Создать только структуру проекта?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        self.btn_export.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self._worker = ExportWorker(self.diagram, settings, export_path)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_progress(self, value: int, message: str):
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)

    def _on_finished(self, result: dict):
        self.progress_bar.setVisible(False)
        self.progress_label.setText("")
        self.btn_export.setEnabled(True)
        project_path = result.get("project_path", "")
        files_count = result.get("files_created", 0)
        QMessageBox.information(
            self, "Экспорт завершён",
            f"Проект успешно создан!\n\nПуть: {project_path}\nФайлов создано: {files_count}"
        )
        self.accept()

    def _on_error(self, message: str):
        self.progress_bar.setVisible(False)
        self.progress_label.setText("")
        self.btn_export.setEnabled(True)
        QMessageBox.critical(self, "Ошибка экспорта", message)
