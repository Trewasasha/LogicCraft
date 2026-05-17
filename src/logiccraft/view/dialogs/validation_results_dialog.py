"""Диалог отображения результатов валидации диаграммы"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QTreeWidget, QTreeWidgetItem,
    QTabWidget, QWidget, QGroupBox, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QColor, QFont
from typing import List, Dict


class ValidationResultsDialog(QDialog):
    """Диалог для отображения результатов валидации с категоризацией"""
    
    # Сигнал для перехода к элементу с проблемой
    navigate_to_element = pyqtSignal(str)  # element_name
    
    def __init__(self, warnings: List[str], parent=None):
        super().__init__(parent)
        self.warnings = warnings
        self.categorized_warnings = self._categorize_warnings(warnings)
        
        self.setWindowTitle("🔍 Результаты валидации диаграммы")
        self.setModal(True)
        self.resize(800, 600)
        
        self._setup_ui()
        self._populate_results()
    
    def _setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        
        # Заголовок с общей статистикой
        header = self._create_header()
        layout.addWidget(header)
        
        # Основная область с результатами
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая панель - дерево категорий
        tree_group = QGroupBox("📋 Категории проблем")
        tree_layout = QVBoxLayout(tree_group)
        
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Категория", "Количество"])
        self.tree_widget.setColumnWidth(0, 400)
        self.tree_widget.itemClicked.connect(self._on_tree_item_clicked)
        tree_layout.addWidget(self.tree_widget)
        
        splitter.addWidget(tree_group)
        
        # Правая панель - детали
        details_group = QGroupBox("📝 Детали")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        details_layout.addWidget(self.details_text)
        
        splitter.addWidget(details_group)
        splitter.setSizes([400, 400])
        
        layout.addWidget(splitter)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        self.export_button = QPushButton("💾 Экспорт отчёта")
        self.export_button.clicked.connect(self._on_export_clicked)
        
        self.close_button = QPushButton("✅ Закрыть")
        self.close_button.clicked.connect(self.accept)
        
        buttons_layout.addWidget(self.export_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_button)
        
        layout.addLayout(buttons_layout)
    
    def _create_header(self) -> QWidget:
        """Создать заголовок с общей статистикой"""
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        
        # Общий статус
        if not self.warnings:
            status_label = QLabel("✅ Диаграмма корректна! Проблем не обнаружено.")
            status_label.setStyleSheet("color: #4CAF50; font-size: 16px; font-weight: bold; padding: 10px;")
        else:
            errors = len([w for w in self.warnings if w.startswith("❌")])
            warnings = len([w for w in self.warnings if w.startswith("⚠️")])
            infos = len([w for w in self.warnings if w.startswith("ℹ️")])
            
            status_text = f"Обнаружено проблем: {len(self.warnings)}"
            if errors > 0:
                status_text += f" | ❌ Ошибок: {errors}"
            if warnings > 0:
                status_text += f" | ⚠️ Предупреждений: {warnings}"
            if infos > 0:
                status_text += f" | ℹ️ Информация: {infos}"
            
            status_label = QLabel(status_text)
            if errors > 0:
                status_label.setStyleSheet("color: #F44336; font-size: 16px; font-weight: bold; padding: 10px;")
            elif warnings > 0:
                status_label.setStyleSheet("color: #FF9800; font-size: 16px; font-weight: bold; padding: 10px;")
            else:
                status_label.setStyleSheet("color: #2196F3; font-size: 16px; font-weight: bold; padding: 10px;")
        
        header_layout.addWidget(status_label)
        
        return header_widget
    
    def _categorize_warnings(self, warnings: List[str]) -> Dict[str, List[str]]:
        """Категоризация предупреждений по типам"""
        categories = {
            "❌ Критические ошибки": [],
            "⚠️ Предупреждения": [],
            "ℹ️ Информация": [],
            "🔗 Проблемы связей": [],
            "👤 Use Case диаграммы": [],
            "🏗️ Классы и структура": []
        }
        
        for warning in warnings:
            # Определяем категорию по содержимому
            if warning.startswith("❌"):
                categories["❌ Критические ошибки"].append(warning)
            elif warning.startswith("⚠️"):
                categories["⚠️ Предупреждения"].append(warning)
            elif warning.startswith("ℹ️"):
                categories["ℹ️ Информация"].append(warning)
            
            # Дополнительная категоризация по содержимому
            if "связь" in warning.lower() or "connection" in warning.lower():
                categories["🔗 Проблемы связей"].append(warning)
            elif "актёр" in warning.lower() or "сценари" in warning.lower() or "use case" in warning.lower():
                categories["👤 Use Case диаграммы"].append(warning)
            elif "класс" in warning.lower() or "интерфейс" in warning.lower():
                categories["🏗️ Классы и структура"].append(warning)
        
        # Удаляем пустые категории
        return {k: v for k, v in categories.items() if v}
    
    def _populate_results(self):
        """Заполнить дерево результатов"""
        self.tree_widget.clear()
        
        if not self.warnings:
            item = QTreeWidgetItem(["✅ Проблем не обнаружено", "0"])
            self.tree_widget.addTopLevelItem(item)
            self.details_text.setHtml(
                "<h3 style='color: #4CAF50;'>✅ Диаграмма корректна!</h3>"
                "<p>Все проверки пройдены успешно. Диаграмма готова к генерации кода.</p>"
            )
            return
        
        # Добавляем категории в дерево
        for category, items in self.categorized_warnings.items():
            category_item = QTreeWidgetItem([category, str(len(items))])
            
            # Устанавливаем цвет в зависимости от типа
            if "❌" in category:
                category_item.setForeground(0, QColor("#F44336"))
            elif "⚠️" in category:
                category_item.setForeground(0, QColor("#FF9800"))
            elif "ℹ️" in category:
                category_item.setForeground(0, QColor("#2196F3"))
            
            # Добавляем элементы категории
            for item_text in items:
                child_item = QTreeWidgetItem([item_text, ""])
                category_item.addChild(child_item)
            
            self.tree_widget.addTopLevelItem(category_item)
            category_item.setExpanded(True)
        
        # Показываем общую информацию в деталях
        self._show_summary()
    
    def _show_summary(self):
        """Показать общую сводку"""
        html = "<h3>📊 Сводка по результатам валидации</h3>"
        
        errors = len([w for w in self.warnings if w.startswith("❌")])
        warnings = len([w for w in self.warnings if w.startswith("⚠️")])
        infos = len([w for w in self.warnings if w.startswith("ℹ️")])
        
        html += "<ul>"
        if errors > 0:
            html += f"<li style='color: #F44336;'><b>❌ Критических ошибок:</b> {errors}</li>"
        if warnings > 0:
            html += f"<li style='color: #FF9800;'><b>⚠️ Предупреждений:</b> {warnings}</li>"
        if infos > 0:
            html += f"<li style='color: #2196F3;'><b>ℹ️ Информационных сообщений:</b> {infos}</li>"
        html += "</ul>"
        
        html += "<h4>💡 Рекомендации:</h4><ul>"
        if errors > 0:
            html += "<li>Исправьте критические ошибки перед генерацией кода</li>"
        if warnings > 0:
            html += "<li>Рассмотрите предупреждения для улучшения качества диаграммы</li>"
        html += "<li>Используйте информационные сообщения для оптимизации структуры</li>"
        html += "</ul>"
        
        self.details_text.setHtml(html)
    
    def _on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Обработка клика по элементу дерева"""
        # Если это элемент проблемы (не категория)
        if item.parent() is not None:
            warning_text = item.text(0)
            self._show_warning_details(warning_text)
    
    def _show_warning_details(self, warning_text: str):
        """Показать детали конкретного предупреждения"""
        html = "<h3>🔍 Детали проблемы</h3>"
        
        # Определяем тип проблемы
        if warning_text.startswith("❌"):
            html += "<p style='color: #F44336; font-weight: bold;'>Тип: Критическая ошибка</p>"
            severity = "Высокая"
        elif warning_text.startswith("⚠️"):
            html += "<p style='color: #FF9800; font-weight: bold;'>Тип: Предупреждение</p>"
            severity = "Средняя"
        else:
            html += "<p style='color: #2196F3; font-weight: bold;'>Тип: Информация</p>"
            severity = "Низкая"
        
        html += f"<p><b>Описание:</b><br>{warning_text}</p>"
        html += f"<p><b>Важность:</b> {severity}</p>"
        
        # Добавляем рекомендации по исправлению
        html += "<h4>💡 Как исправить:</h4>"
        html += self._get_fix_recommendation(warning_text)
        
        self.details_text.setHtml(html)
    
    def _get_fix_recommendation(self, warning_text: str) -> str:
        """Получить рекомендацию по исправлению"""
        recommendations = {
            "Дублирующееся имя": "<ul><li>Переименуйте один из элементов с дублирующимся именем</li><li>Используйте уникальные имена для всех элементов диаграммы</li></ul>",
            "не имеет атрибутов и методов": "<ul><li>Добавьте атрибуты или методы к классу</li><li>Если класс пустой намеренно, рассмотрите использование абстрактного класса</li></ul>",
            "не имеет методов": "<ul><li>Добавьте хотя бы один метод к интерфейсу</li><li>Интерфейсы должны определять контракт поведения</li></ul>",
            "Циклическое наследование": "<ul><li>Удалите одну из связей наследования, создающих цикл</li><li>Пересмотрите иерархию классов</li></ul>",
            "несуществующий": "<ul><li>Удалите связь или восстановите удалённый элемент</li><li>Проверьте целостность диаграммы</li></ul>",
            "не связан": "<ul><li>Добавьте связь с другими элементами</li><li>Удалите элемент, если он не используется</li></ul>",
            "не имеет описания": "<ul><li>Добавьте описание сценария через панель свойств</li><li>Описание помогает понять назначение сценария</li></ul>",
            "должна связывать только сценарии": "<ul><li>Используйте Include/Extend только между сценариями</li><li>Для связи актёра и сценария используйте обычную ассоциацию</li></ul>"
        }
        
        for key, recommendation in recommendations.items():
            if key.lower() in warning_text.lower():
                return recommendation
        
        return "<ul><li>Проверьте элемент и исправьте указанную проблему</li></ul>"
    
    def _on_export_clicked(self):
        """Экспорт отчёта о валидации"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить отчёт о валидации",
            "validation_report.txt",
            "Text Files (*.txt);;HTML Files (*.html)"
        )
        
        if not filepath:
            return
        
        try:
            if filepath.endswith('.html'):
                content = self._generate_html_report()
            else:
                content = self._generate_text_report()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            QMessageBox.information(self, "Успех", f"Отчёт сохранён:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения отчёта:\n{str(e)}")
    
    def _generate_text_report(self) -> str:
        """Генерация текстового отчёта"""
        report = "=" * 60 + "\n"
        report += "ОТЧЁТ О ВАЛИДАЦИИ ДИАГРАММЫ\n"
        report += "=" * 60 + "\n\n"
        
        if not self.warnings:
            report += "✅ Диаграмма корректна! Проблем не обнаружено.\n"
        else:
            report += f"Обнаружено проблем: {len(self.warnings)}\n\n"
            
            for category, items in self.categorized_warnings.items():
                report += f"\n{category} ({len(items)})\n"
                report += "-" * 60 + "\n"
                for item in items:
                    report += f"  • {item}\n"
        
        report += "\n" + "=" * 60 + "\n"
        return report
    
    def _generate_html_report(self) -> str:
        """Генерация HTML отчёта"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Отчёт о валидации диаграммы</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .error { color: #F44336; }
        .warning { color: #FF9800; }
        .info { color: #2196F3; }
        .category { margin: 20px 0; }
        .category h2 { border-bottom: 2px solid #ddd; padding-bottom: 5px; }
        ul { list-style-type: none; padding-left: 20px; }
        li { margin: 5px 0; }
    </style>
</head>
<body>
    <h1>📊 Отчёт о валидации диаграммы</h1>
"""
        
        if not self.warnings:
            html += "<p class='info'>✅ Диаграмма корректна! Проблем не обнаружено.</p>"
        else:
            html += f"<p>Обнаружено проблем: <b>{len(self.warnings)}</b></p>"
            
            for category, items in self.categorized_warnings.items():
                html += f"<div class='category'>"
                html += f"<h2>{category} ({len(items)})</h2>"
                html += "<ul>"
                for item in items:
                    css_class = "error" if "❌" in item else ("warning" if "⚠️" in item else "info")
                    html += f"<li class='{css_class}'>{item}</li>"
                html += "</ul>"
                html += "</div>"
        
        html += """
</body>
</html>
"""
        return html
