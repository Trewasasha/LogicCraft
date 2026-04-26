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
        self.setFixedSize(240, 200)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Устанавливаем objectName для применения стилей из QSS
        if is_primary:
            self.setObjectName("WelcomeCardPrimary")
            icon_obj_name = "WelcomeCardIconPrimary"
            title_obj_name = "WelcomeCardTitlePrimary"
            subtitle_obj_name = "WelcomeCardSubtitlePrimary"
        else:
            self.setObjectName("WelcomeCardSecondary")
            icon_obj_name = "WelcomeCardIconSecondary"
            title_obj_name = "WelcomeCardTitleSecondary"
            subtitle_obj_name = "WelcomeCardSubtitleSecondary"
        
        # Лейаут
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Иконка
        icon_label = QLabel(icon)
        icon_label.setObjectName(icon_obj_name)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Заголовок
        title_label = QLabel(title)
        title_label.setObjectName(title_obj_name)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setMaximumWidth(200)
        layout.addWidget(title_label)
        
        # Подзаголовок
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName(subtitle_obj_name)
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
        self.setFixedSize(700, 600)
        self.setModal(True)
        self.setObjectName("WelcomeDialog")
        
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
        
        # Заголовок
        title = QLabel("СХЕМАТУС")
        title.setObjectName("WelcomeTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Подзаголовок
        subtitle = QLabel("Начните работу с вашими схемами и классами")
        subtitle.setObjectName("WelcomeSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
        close_btn.setObjectName("WelcomeCloseButton")
        close_btn.setFixedSize(32, 32)
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
