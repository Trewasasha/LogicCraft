"""Стартовое окно приложения"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class WelcomeCard(QPushButton):
    """Карточка действия на стартовом экране"""
    
    def __init__(self, icon: str, title: str, subtitle: str, is_primary: bool = False):
        super().__init__()
        self.setFixedSize(360, 200)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Стили
        if is_primary:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #8B5CF6, stop:1 #7C3AED);
                    border: none;
                    border-radius: 16px;
                    padding: 20px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #7C3AED, stop:1 #6D28D9);
                }
                QPushButton:pressed {
                    background: #6D28D9;
                }
            """)
            icon_color = "rgba(255, 255, 255, 200)"
            title_color = "#FFFFFF"
            subtitle_color = "rgba(255, 255, 255, 180)"
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    border: 2px solid #E5E0F8;
                    border-radius: 16px;
                    padding: 20px;
                }
                QPushButton:hover {
                    background-color: #F8F6FF;
                    border-color: #C4B5FD;
                }
                QPushButton:pressed {
                    background-color: #EDE9FE;
                }
            """)
            icon_color = "#9B72F5"
            title_color = "#1F1F1F"
            subtitle_color = "#6B7280"
        
        # Лейаут
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Иконка
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 48px; color: {icon_color};")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Заголовок
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {title_color};")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setMaximumWidth(300)
        layout.addWidget(title_label)
        
        # Подзаголовок
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet(f"font-size: 13px; color: {subtitle_color};")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setWordWrap(True)
        layout.addWidget(subtitle_label)


class WelcomeDialog(QDialog):
    """Стартовое окно приложения"""
    
    new_project_requested = pyqtSignal()
    open_project_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LogicCraft")
        self.setFixedSize(900, 620)
        self.setModal(True)
        
        # Убираем рамку окна для современного вида
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        
        # Для перемещения окна
        self._drag_position = None
        
        self._setup_ui()
    
    def mousePressEvent(self, event):
        """Начало перемещения окна"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Перемещение окна"""
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_position is not None:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Конец перемещения окна"""
        self._drag_position = None
    
    def _setup_ui(self):
        """Настройка UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(40)
        
        # Фон
        self.setStyleSheet("""
            QDialog {
                background-color: #F0EFFE;
                border-radius: 20px;
            }
        """)
        
        # Заголовок
        title = QLabel("СХЕМАТУС")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 56px;
            font-weight: 800;
            color: #7C3AED;
            letter-spacing: 2px;
            margin-bottom: 10px;
        """)
        main_layout.addWidget(title)
        
        # Подзаголовок
        subtitle = QLabel("Начните работу с вашими схемами и классами")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 16px;
            color: #6B7280;
            margin-bottom: 20px;
        """)
        main_layout.addWidget(subtitle)
        
        # Карточки
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(30)
        cards_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Карточка "Открыть проект"
        open_card = WelcomeCard(
            icon="📂",
            title="Открыть проект",
            subtitle="Выберите существующий проект",
            is_primary=False
        )
        open_card.clicked.connect(self._on_open_project)
        cards_layout.addWidget(open_card)
        
        # Карточка "Создать новый проект"
        new_card = WelcomeCard(
            icon="✨",
            title="Создать новый проект",
            subtitle="Начните с чистого листа",
            is_primary=True
        )
        new_card.clicked.connect(self._on_new_project)
        cards_layout.addWidget(new_card)
        
        main_layout.addLayout(cards_layout)
        main_layout.addStretch()
        
        # Кнопка закрытия (маленький крестик в углу)
        close_btn = QPushButton("×")
        close_btn.setFixedSize(32, 32)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #9B72F5;
                font-size: 24px;
                font-weight: bold;
                border: none;
                border-radius: 16px;
            }
            QPushButton:hover {
                background-color: rgba(155, 114, 245, 0.1);
            }
        """)
        close_btn.clicked.connect(self.reject)
        
        # Размещаем крестик в правом верхнем углу
        close_btn.move(self.width() - 40, 8)
    
    def _on_new_project(self):
        """Создать новый проект"""
        self.new_project_requested.emit()
        self.accept()
    
    def _on_open_project(self):
        """Открыть существующий проект"""
        self.open_project_requested.emit()
        self.accept()
