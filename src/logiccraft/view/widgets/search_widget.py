"""Виджет поиска классов на диаграмме"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QListWidget, 
    QListWidgetItem, QLabel, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon


class SearchWidget(QWidget):
    """Виджет для поиска классов по имени"""
    
    class_selected = pyqtSignal(str)  # card_id
    close_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_cards = []  # Список всех карточек для поиска
        self._setup_ui()
        
    def _setup_ui(self):
        """Настройка UI"""
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Заголовок
        header_layout = QHBoxLayout()
        title = QLabel("🔍 Поиск классов")
        title.setFont(QFont("Inter", 12, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #666;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #F3EEFF;
                border-radius: 12px;
                color: #7C3AED;
            }
        """)
        close_btn.clicked.connect(self.close_requested.emit)
        header_layout.addWidget(close_btn)
        layout.addLayout(header_layout)
        
        # Поле поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите имя класса...")
        self.search_input.setFont(QFont("Inter", 11))
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #F9FAFB;
                border: 2px solid #E5E0F8;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #7C3AED;
                background-color: white;
            }
        """)
        self.search_input.textChanged.connect(self._on_search_text_changed)
        self.search_input.returnPressed.connect(self._on_enter_pressed)
        layout.addWidget(self.search_input)
        
        # Список результатов
        self.results_list = QListWidget()
        self.results_list.setFont(QFont("Inter", 11))
        self.results_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #E5E0F8;
                border-radius: 8px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-radius: 6px;
                margin: 2px;
            }
            QListWidget::item:hover {
                background-color: #F3EEFF;
            }
            QListWidget::item:selected {
                background-color: #7C3AED;
                color: white;
            }
        """)
        self.results_list.itemClicked.connect(self._on_item_clicked)
        self.results_list.itemActivated.connect(self._on_item_activated)
        layout.addWidget(self.results_list)
        
        # Счетчик результатов
        self.results_label = QLabel("Введите текст для поиска")
        self.results_label.setFont(QFont("Inter", 9))
        self.results_label.setStyleSheet("color: #666;")
        layout.addWidget(self.results_label)
        
        # Стиль виджета
        self.setStyleSheet("""
            SearchWidget {
                background-color: white;
                border: 2px solid #7C3AED;
                border-radius: 12px;
            }
        """)
        
        self.setFixedSize(350, 400)
    
    def set_cards(self, cards):
        """Установить список карточек для поиска"""
        self._all_cards = cards
        self._update_results()
    
    def _on_search_text_changed(self, text):
        """Обработка изменения текста поиска"""
        self._update_results()
    
    def _update_results(self):
        """Обновить список результатов"""
        self.results_list.clear()
        search_text = self.search_input.text().lower().strip()
        
        if not search_text:
            self.results_label.setText("Введите текст для поиска")
            return
        
        # Поиск с поддержкой частичного совпадения
        matches = []
        for card in self._all_cards:
            if search_text in card.name.lower():
                matches.append(card)
        
        # Сортировка: сначала точные совпадения, потом частичные
        matches.sort(key=lambda c: (
            not c.name.lower().startswith(search_text),
            c.name.lower()
        ))
        
        # Добавление результатов
        for card in matches:
            item = QListWidgetItem(f"⬡ {card.name}")
            item.setData(Qt.ItemDataRole.UserRole, card.id)
            self.results_list.addItem(item)
        
        # Обновление счетчика
        if matches:
            self.results_label.setText(f"Найдено: {len(matches)} класс(ов)")
            self.results_list.setCurrentRow(0)  # Выбираем первый результат
        else:
            self.results_label.setText("Ничего не найдено")
    
    def _on_item_clicked(self, item):
        """Обработка клика на элемент"""
        card_id = item.data(Qt.ItemDataRole.UserRole)
        self.class_selected.emit(card_id)
    
    def _on_item_activated(self, item):
        """Обработка активации элемента (двойной клик или Enter)"""
        card_id = item.data(Qt.ItemDataRole.UserRole)
        self.class_selected.emit(card_id)
        self.close_requested.emit()
    
    def _on_enter_pressed(self):
        """Обработка нажатия Enter в поле поиска"""
        if self.results_list.count() > 0:
            current_item = self.results_list.currentItem()
            if current_item:
                self._on_item_activated(current_item)
    
    def keyPressEvent(self, event):
        """Обработка клавиш"""
        if event.key() == Qt.Key.Key_Escape:
            self.close_requested.emit()
        elif event.key() == Qt.Key.Key_Down:
            self.results_list.setFocus()
            if self.results_list.count() > 0:
                self.results_list.setCurrentRow(0)
        else:
            super().keyPressEvent(event)
    
    def showEvent(self, event):
        """При показе виджета устанавливаем фокус на поле поиска"""
        super().showEvent(event)
        self.search_input.setFocus()
        self.search_input.selectAll()
