"""Диалог генерации кода"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QTextEdit, QTabWidget, QWidget, QSplitter,
    QGroupBox, QCheckBox, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor
import re
from typing import Dict, Optional
from ...services.code_generator import CodeGenerator
from ...models.diagram import UMLDiagram


class CodeSyntaxHighlighter(QSyntaxHighlighter):
    """Подсветка синтаксиса для кода"""
    
    def __init__(self, language: str, parent=None):
        super().__init__(parent)
        self.language = language
        self._setup_highlighting_rules()
    
    def _setup_highlighting_rules(self):
        """Настройка правил подсветки"""
        self.highlighting_rules = []
        
        # Ключевые слова
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))  # Синий
        keyword_format.setFontWeight(QFont.Weight.Bold)
        
        if self.language == "python":
            keywords = ["class", "def", "import", "from", "if", "else", "elif", "for", "while", "try", "except", "finally", "with", "as", "return", "yield", "pass", "break", "continue", "and", "or", "not", "in", "is", "None", "True", "False"]
        elif self.language == "java":
            keywords = ["class", "public", "private", "protected", "static", "final", "abstract", "interface", "extends", "implements", "import", "package", "if", "else", "for", "while", "do", "switch", "case", "default", "try", "catch", "finally", "throw", "throws", "return", "break", "continue", "new", "this", "super", "null", "true", "false"]
        else:
            keywords = []
        
        for keyword in keywords:
            pattern = f"\\b{keyword}\\b"
            self.highlighting_rules.append((re.compile(pattern), keyword_format))
        
        # Строки
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))  # Оранжевый
        self.highlighting_rules.append((re.compile(r'".*?"'), string_format))
        self.highlighting_rules.append((re.compile(r"'.*?'"), string_format))
        
        # Комментарии
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))  # Зеленый
        comment_format.setFontItalic(True)
        
        if self.language == "python":
            self.highlighting_rules.append((re.compile(r'#.*'), comment_format))
        elif self.language == "java":
            self.highlighting_rules.append((re.compile(r'//.*'), comment_format))
            self.highlighting_rules.append((re.compile(r'/\*.*?\*/'), comment_format))
    
    def highlightBlock(self, text):
        """Применить подсветку к блоку текста"""
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)


class CodeGenerationDialog(QDialog):
    """Диалог для генерации и предпросмотра кода"""
    
    def __init__(self, diagram: UMLDiagram, parent=None):
        super().__init__(parent)
        self.diagram = diagram
        self.generator = CodeGenerator()
        self.generated_files = {}
        
        self.setWindowTitle("🚀 Генерация кода")
        self.setModal(True)
        self.resize(900, 700)
        
        self._setup_ui()
        self._connect_signals()
        self._generate_initial_code()
    
    def _setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        
        # Верхняя панель с настройками
        settings_group = QGroupBox("⚙️ Настройки генерации")
        settings_layout = QVBoxLayout(settings_group)
        
        # Выбор языка с иконками и описаниями
        lang_label = QLabel("Выберите язык программирования:")
        lang_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        settings_layout.addWidget(lang_label)
        
        # Горизонтальный layout для языков
        lang_buttons_layout = QHBoxLayout()
        
        self.language_buttons = {}
        languages_info = {
            "python": {"icon": "🐍", "desc": "Python 3.x"},
            "java": {"icon": "☕", "desc": "Java 11+"}
        }
        
        from PyQt6.QtWidgets import QButtonGroup, QRadioButton
        self.language_button_group = QButtonGroup(self)
        
        for lang, info in languages_info.items():
            radio = QRadioButton(f"{info['icon']} {info['desc']}")
            radio.setProperty("language", lang)
            radio.setStyleSheet("""
                QRadioButton {
                    padding: 8px;
                    font-size: 11px;
                }
                QRadioButton::indicator {
                    width: 18px;
                    height: 18px;
                }
            """)
            self.language_button_group.addButton(radio)
            self.language_buttons[lang] = radio
            lang_buttons_layout.addWidget(radio)
        
        # Устанавливаем Python по умолчанию
        self.language_buttons["python"].setChecked(True)
        settings_layout.addLayout(lang_buttons_layout)
        
        # Разделитель
        from PyQt6.QtWidgets import QFrame
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        settings_layout.addWidget(line)
        
        # Опции генерации
        options_layout = QHBoxLayout()
        options_layout.addWidget(QLabel("Режим генерации:"))
        
        self.single_file_checkbox = QCheckBox("Один файл")
        self.single_file_checkbox.setChecked(True)
        self.single_file_checkbox.setToolTip("Генерировать все классы в один файл")
        options_layout.addWidget(self.single_file_checkbox)
        
        self.include_docs_checkbox = QCheckBox("Документация")
        self.include_docs_checkbox.setChecked(True)
        self.include_docs_checkbox.setToolTip("Включить docstrings/комментарии")
        options_layout.addWidget(self.include_docs_checkbox)
        
        self.include_typing_checkbox = QCheckBox("Типизация")
        self.include_typing_checkbox.setChecked(True)
        self.include_typing_checkbox.setToolTip("Включить аннотации типов (где применимо)")
        options_layout.addWidget(self.include_typing_checkbox)
        
        options_layout.addStretch()
        settings_layout.addLayout(options_layout)
        
        layout.addWidget(settings_group)
        
        # Основная область с кодом
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая панель - предпросмотр
        preview_group = QGroupBox("👀 Предпросмотр кода")
        preview_layout = QVBoxLayout(preview_group)
        
        self.code_tabs = QTabWidget()
        preview_layout.addWidget(self.code_tabs)
        
        splitter.addWidget(preview_group)
        
        # Правая панель - информация
        info_group = QGroupBox("ℹ️ Информация")
        info_layout = QVBoxLayout(info_group)
        
        self.info_text = QTextEdit()
        self.info_text.setMaximumWidth(250)
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)
        
        splitter.addWidget(info_group)
        splitter.setSizes([650, 250])
        
        layout.addWidget(splitter)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        self.templates_button = QPushButton("📝 Управление шаблонами")
        self.templates_button.clicked.connect(self._on_templates_clicked)
        
        self.export_button = QPushButton("💾 Экспорт файлов")
        self.copy_button = QPushButton("📋 Копировать код")
        self.close_button = QPushButton("❌ Закрыть")
        
        buttons_layout.addWidget(self.templates_button)
        buttons_layout.addWidget(self.export_button)
        buttons_layout.addWidget(self.copy_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_button)
        
        layout.addLayout(buttons_layout)
    
    def _connect_signals(self):
        """Подключение сигналов"""
        self.language_button_group.buttonClicked.connect(self._on_language_changed)
        self.single_file_checkbox.toggled.connect(self._on_generation_mode_changed)
        self.include_docs_checkbox.toggled.connect(self._on_generation_mode_changed)
        self.include_typing_checkbox.toggled.connect(self._on_generation_mode_changed)
        self.export_button.clicked.connect(self._on_export_clicked)
        self.copy_button.clicked.connect(self._on_copy_clicked)
        self.close_button.clicked.connect(self.accept)
    
    def _generate_initial_code(self):
        """Генерация начального кода"""
        self._generate_code()
    
    def _on_language_changed(self, button):
        """Обработка изменения языка"""
        self._generate_code()
    
    def _on_generation_mode_changed(self):
        """Обработка изменения режима генерации"""
        self._generate_code()
    
    def _generate_code(self):
        """Генерация кода"""
        # Получаем выбранный язык из radio buttons
        selected_button = self.language_button_group.checkedButton()
        if not selected_button:
            return
        
        language = selected_button.property("language")
        single_file = self.single_file_checkbox.isChecked()
        
        try:
            if single_file:
                # Генерация в один файл
                code = self.generator.generate(self.diagram, language)
                self.generated_files = {f"all_classes.{self._get_extension(language)}": code}
            else:
                # Генерация отдельных файлов
                self.generated_files = self.generator.generate_files(self.diagram, language)
            
            self._update_code_tabs(language)
            self._update_info()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка генерации кода: {str(e)}")
    
    def _get_extension(self, language: str) -> str:
        """Получить расширение файла для языка"""
        extensions = {
            "python": "py",
            "java": "java"
        }
        return extensions.get(language, "txt")
    
    def _update_code_tabs(self, language: str):
        """Обновление вкладок с кодом"""
        # Очищаем старые вкладки
        self.code_tabs.clear()
        
        # Добавляем новые вкладки
        for filename, content in self.generated_files.items():
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            
            code_edit = QTextEdit()
            code_edit.setPlainText(content)
            code_edit.setReadOnly(True)
            
            # Устанавливаем моноширинный шрифт
            font = QFont("Consolas", 10)
            font.setStyleHint(QFont.StyleHint.Monospace)
            code_edit.setFont(font)
            
            # Добавляем подсветку синтаксиса
            highlighter = CodeSyntaxHighlighter(language, code_edit.document())
            
            tab_layout.addWidget(code_edit)
            
            self.code_tabs.addTab(tab, filename)
    
    def _update_info(self):
        """Обновление информационной панели"""
        selected_button = self.language_button_group.checkedButton()
        if not selected_button:
            return
        
        language = selected_button.property("language")
        file_count = len(self.generated_files)
        total_lines = sum(content.count('\n') + 1 for content in self.generated_files.values())
        class_count = len(self.diagram.nodes)
        
        # Получаем иконку языка
        lang_icons = {
            "python": "🐍",
            "java": "☕"
        }
        lang_icon = lang_icons.get(language, "💻")
        
        info_text = f"""
📊 Статистика генерации:

{lang_icon} Язык: {language.upper()}
📁 Файлов: {file_count}
📝 Строк кода: {total_lines}
🏗️ Классов: {class_count}

⚙️ Опции:
• Документация: {'✅' if self.include_docs_checkbox.isChecked() else '❌'}
• Типизация: {'✅' if self.include_typing_checkbox.isChecked() else '❌'}

📋 Файлы:
"""
        
        for filename in self.generated_files.keys():
            lines = self.generated_files[filename].count('\n') + 1
            info_text += f"• {filename} ({lines} строк)\n"
        
        self.info_text.setPlainText(info_text)
    
    def _on_export_clicked(self):
        """Экспорт файлов"""
        if not self.generated_files:
            QMessageBox.warning(self, "Предупреждение", "Нет кода для экспорта")
            return
        
        # Выбор папки для экспорта
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Выберите папку для экспорта",
            ""
        )
        
        if not folder:
            return
        
        try:
            import os
            exported_count = 0
            
            for filename, content in self.generated_files.items():
                filepath = os.path.join(folder, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                exported_count += 1
            
            QMessageBox.information(
                self, 
                "Успех", 
                f"Экспортировано {exported_count} файлов в:\n{folder}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка экспорта: {str(e)}")
    
    def _on_copy_clicked(self):
        """Копирование кода в буфер обмена"""
        current_tab = self.code_tabs.currentIndex()
        if current_tab >= 0:
            tab_widget = self.code_tabs.widget(current_tab)
            code_edit = tab_widget.findChild(QTextEdit)
            if code_edit:
                code_edit.selectAll()
                code_edit.copy()
                QMessageBox.information(self, "Успех", "Код скопирован в буфер обмена")
    
    def _on_templates_clicked(self):
        """Открыть менеджер шаблонов"""
        from .template_manager_dialog import TemplateManagerDialog
        
        dialog = TemplateManagerDialog(self)
        dialog.templates_changed.connect(self._on_templates_changed)
        dialog.exec()
    
    def _on_templates_changed(self):
        """Обработка изменения шаблонов"""
        # Перегенерируем код с новыми шаблонами
        self._generate_code()