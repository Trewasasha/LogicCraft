"""Диалог управления шаблонами кода"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QListWidget, QListWidgetItem,
    QGroupBox, QSplitter, QMessageBox, QInputDialog,
    QFileDialog, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Dict, Optional
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class TemplateManagerDialog(QDialog):
    """Диалог для управления пользовательскими шаблонами кода"""
    
    templates_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.templates_dir = Path.home() / ".logiccraft" / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_template = None
        self.templates = self._load_templates()
        
        self.setWindowTitle("📝 Управление шаблонами кода")
        self.setModal(True)
        self.resize(1000, 700)
        
        self._setup_ui()
        self._load_template_list()
    
    def _setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        
        # Заголовок
        header = QLabel("Создавайте и редактируйте пользовательские шаблоны для генерации кода")
        header.setStyleSheet("font-size: 12px; color: #666; padding: 5px;")
        layout.addWidget(header)
        
        # Основная область
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая панель - список шаблонов
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        templates_label = QLabel("📚 Шаблоны:")
        templates_label.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(templates_label)
        
        self.templates_list = QListWidget()
        self.templates_list.itemClicked.connect(self._on_template_selected)
        left_layout.addWidget(self.templates_list)
        
        # Кнопки управления шаблонами
        buttons_layout = QHBoxLayout()
        
        self.new_button = QPushButton("➕ Новый")
        self.new_button.clicked.connect(self._on_new_template)
        buttons_layout.addWidget(self.new_button)
        
        self.delete_button = QPushButton("🗑️ Удалить")
        self.delete_button.clicked.connect(self._on_delete_template)
        self.delete_button.setEnabled(False)
        buttons_layout.addWidget(self.delete_button)
        
        left_layout.addLayout(buttons_layout)
        
        splitter.addWidget(left_panel)
        
        # Правая панель - редактор шаблона
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Информация о шаблоне
        info_group = QGroupBox("ℹ️ Информация о шаблоне")
        info_layout = QVBoxLayout(info_group)
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Название:"))
        self.name_label = QLabel("—")
        self.name_label.setStyleSheet("font-weight: bold;")
        name_layout.addWidget(self.name_label)
        name_layout.addStretch()
        info_layout.addLayout(name_layout)
        
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Язык:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(["python", "java"])
        self.language_combo.currentTextChanged.connect(self._on_language_changed)
        lang_layout.addWidget(self.language_combo)
        lang_layout.addStretch()
        info_layout.addLayout(lang_layout)
        
        right_layout.addWidget(info_group)
        
        # Редактор шаблона
        editor_group = QGroupBox("✏️ Редактор шаблона (Jinja2)")
        editor_layout = QVBoxLayout(editor_group)
        
        # Подсказка
        hint = QLabel("💡 Доступные переменные: {{ diagram_name }}, {% for node in nodes %}, {{ node.name }}, {{ node.properties }}, {{ node.methods }}")
        hint.setStyleSheet("color: #2196F3; font-size: 10px; padding: 5px;")
        hint.setWordWrap(True)
        editor_layout.addWidget(hint)
        
        self.template_editor = QTextEdit()
        self.template_editor.setPlaceholderText("Введите шаблон Jinja2...")
        
        # Моноширинный шрифт
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.template_editor.setFont(font)
        
        editor_layout.addWidget(self.template_editor)
        
        right_layout.addWidget(editor_group)
        
        # Кнопки сохранения
        save_layout = QHBoxLayout()
        
        self.save_button = QPushButton("💾 Сохранить")
        self.save_button.clicked.connect(self._on_save_template)
        self.save_button.setEnabled(False)
        save_layout.addWidget(self.save_button)
        
        self.import_button = QPushButton("📥 Импорт")
        self.import_button.clicked.connect(self._on_import_template)
        save_layout.addWidget(self.import_button)
        
        self.export_button = QPushButton("📤 Экспорт")
        self.export_button.clicked.connect(self._on_export_template)
        self.export_button.setEnabled(False)
        save_layout.addWidget(self.export_button)
        
        save_layout.addStretch()
        right_layout.addLayout(save_layout)
        
        splitter.addWidget(right_panel)
        splitter.setSizes([250, 750])
        
        layout.addWidget(splitter)
        
        # Кнопка закрытия
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        
        self.close_button = QPushButton("✅ Закрыть")
        self.close_button.clicked.connect(self.accept)
        close_layout.addWidget(self.close_button)
        
        layout.addLayout(close_layout)
    
    def _load_templates(self) -> Dict:
        """Загрузить пользовательские шаблоны"""
        templates = {}
        
        if not self.templates_dir.exists():
            return templates
        
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                    templates[template_file.stem] = template_data
            except Exception as e:
                logger.error(f"Error loading template {template_file}: {e}")
        
        return templates
    
    def _load_template_list(self):
        """Загрузить список шаблонов в UI"""
        self.templates_list.clear()
        
        # Добавляем встроенные шаблоны (только для просмотра)
        builtin_item = QListWidgetItem("📦 Встроенные шаблоны")
        builtin_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        builtin_item.setBackground(Qt.GlobalColor.lightGray)
        self.templates_list.addItem(builtin_item)
        
        builtin_templates = ["python_class.j2", "java_class.j2"]
        for template in builtin_templates:
            item = QListWidgetItem(f"  • {template}")
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item.setData(Qt.ItemDataRole.UserRole, {"type": "builtin", "name": template})
            self.templates_list.addItem(item)
        
        # Добавляем пользовательские шаблоны
        if self.templates:
            custom_item = QListWidgetItem("👤 Пользовательские шаблоны")
            custom_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            custom_item.setBackground(Qt.GlobalColor.lightGray)
            self.templates_list.addItem(custom_item)
            
            for name, data in self.templates.items():
                lang_icon = {"python": "🐍", "java": "☕"}.get(data.get("language", ""), "💻")
                item = QListWidgetItem(f"  {lang_icon} {name}")
                item.setData(Qt.ItemDataRole.UserRole, {"type": "custom", "name": name})
                self.templates_list.addItem(item)
    
    def _on_template_selected(self, item: QListWidgetItem):
        """Обработка выбора шаблона"""
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        if data["type"] == "builtin":
            QMessageBox.information(
                self, 
                "Встроенный шаблон",
                f"Шаблон «{data['name']}» является встроенным и не может быть изменён.\n\n"
                "Создайте новый пользовательский шаблон для кастомизации."
            )
            return
        
        # Загружаем пользовательский шаблон
        template_name = data["name"]
        if template_name in self.templates:
            self.current_template = template_name
            template_data = self.templates[template_name]
            
            self.name_label.setText(template_name)
            self.language_combo.setCurrentText(template_data.get("language", "python"))
            self.template_editor.setPlainText(template_data.get("content", ""))
            
            self.save_button.setEnabled(True)
            self.export_button.setEnabled(True)
            self.delete_button.setEnabled(True)
    
    def _on_new_template(self):
        """Создать новый шаблон"""
        name, ok = QInputDialog.getText(
            self,
            "Новый шаблон",
            "Введите название шаблона:"
        )
        
        if not ok or not name:
            return
        
        if name in self.templates:
            QMessageBox.warning(self, "Ошибка", "Шаблон с таким именем уже существует")
            return
        
        # Создаём базовый шаблон
        self.templates[name] = {
            "language": "python",
            "content": "# Шаблон для {{ diagram_name }}\n\n{% for node in nodes %}\nclass {{ node.name }}:\n    pass\n{% endfor %}"
        }
        
        self._load_template_list()
        self.current_template = name
        
        # Выбираем новый шаблон
        for i in range(self.templates_list.count()):
            item = self.templates_list.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            if data and data.get("name") == name:
                self.templates_list.setCurrentItem(item)
                self._on_template_selected(item)
                break
    
    def _on_delete_template(self):
        """Удалить шаблон"""
        if not self.current_template:
            return
        
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить шаблон «{self.current_template}»?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Удаляем файл
            template_file = self.templates_dir / f"{self.current_template}.json"
            if template_file.exists():
                template_file.unlink()
            
            # Удаляем из словаря
            del self.templates[self.current_template]
            
            self.current_template = None
            self._load_template_list()
            self.template_editor.clear()
            self.name_label.setText("—")
            self.save_button.setEnabled(False)
            self.export_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            
            self.templates_changed.emit()
    
    def _on_save_template(self):
        """Сохранить шаблон"""
        if not self.current_template:
            return
        
        content = self.template_editor.toPlainText()
        language = self.language_combo.currentText()
        
        self.templates[self.current_template] = {
            "language": language,
            "content": content
        }
        
        # Сохраняем в файл
        template_file = self.templates_dir / f"{self.current_template}.json"
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(self.templates[self.current_template], f, indent=2, ensure_ascii=False)
        
        QMessageBox.information(self, "Успех", "Шаблон сохранён")
        self.templates_changed.emit()
        self._load_template_list()
    
    def _on_language_changed(self, language: str):
        """Обработка изменения языка"""
        if self.current_template:
            self.templates[self.current_template]["language"] = language
    
    def _on_import_template(self):
        """Импорт шаблона из файла"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Импорт шаблона",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            name = Path(filepath).stem
            
            if name in self.templates:
                reply = QMessageBox.question(
                    self,
                    "Подтверждение",
                    f"Шаблон «{name}» уже существует. Перезаписать?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            self.templates[name] = template_data
            
            # Сохраняем
            template_file = self.templates_dir / f"{name}.json"
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)
            
            self._load_template_list()
            QMessageBox.information(self, "Успех", f"Шаблон «{name}» импортирован")
            self.templates_changed.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка импорта:\n{str(e)}")
    
    def _on_export_template(self):
        """Экспорт шаблона в файл"""
        if not self.current_template:
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Экспорт шаблона",
            f"{self.current_template}.json",
            "JSON Files (*.json)"
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.templates[self.current_template], f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(self, "Успех", f"Шаблон экспортирован:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка экспорта:\n{str(e)}")
