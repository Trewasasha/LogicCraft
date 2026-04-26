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
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Верхняя панель с кнопками управления окном
        title_bar = QWidget()
        title_bar.setObjectName("WelcomeTitleBar")
        title_bar.setFixedHeight(44)
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(16, 0, 16, 0)
        title_bar_layout.addStretch()

        # Кнопка свернуть
        minimize_btn = QPushButton("−")
        minimize_btn.setObjectName("WelcomeMinimizeButton")
        minimize_btn.setFixedSize(28, 28)
        minimize_btn.setToolTip("Свернуть")
        minimize_btn.clicked.connect(self.showMinimized)
        title_bar_layout.addWidget(minimize_btn)

        # Кнопка на весь экран
        maximize_btn = QPushButton("□")
        maximize_btn.setObjectName("WelcomeMaximizeButton")
        maximize_btn.setFixedSize(28, 28)
        maximize_btn.setToolTip("Развернуть")
        maximize_btn.clicked.connect(self._toggle_maximize)
        title_bar_layout.addWidget(maximize_btn)

        # Кнопка закрыть
        close_btn = QPushButton("×")
        close_btn.setObjectName("WelcomeCloseButton")
        close_btn.setFixedSize(28, 28)
        close_btn.setToolTip("Закрыть")
        close_btn.clicked.connect(self.reject)
        title_bar_layout.addWidget(close_btn)

        main_layout.addWidget(title_bar)

        # Контент
        content = QWidget()
        content.setObjectName("WelcomeContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(50, 20, 50, 50)
        content_layout.setSpacing(40)

        # Заголовок
        title = QLabel("СХЕМАТУС")
        title.setObjectName("WelcomeTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title)

        # Подзаголовок
        subtitle = QLabel("Начните работу с вашими схемами и классами")
        subtitle.setObjectName("WelcomeSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(subtitle)

        # Карточки
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(30)
        cards_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        open_card = WelcomeCard(
            icon="📂",
            title="Открыть проект",
            subtitle="Выберите существующий проект",
            is_primary=False
        )
        open_card.clicked.connect(self._on_open_project)
        cards_layout.addWidget(open_card)

        new_card = WelcomeCard(
            icon="✨",
            title="Создать новый проект",
            subtitle="Начните с чистого листа",
            is_primary=True
        )
        new_card.clicked.connect(self._on_new_project)
        cards_layout.addWidget(new_card)

        content_layout.addLayout(cards_layout)
        content_layout.addStretch()

        main_layout.addWidget(content)

    def _toggle_maximize(self):
        """Переключить полноэкранный режим"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    def _on_new_project(self):
        """Создать новый проект"""
        self.new_project_requested.emit()
        self.accept()
    
    def _on_open_project(self):
        """Открыть существующий проект"""
        self.open_project_requested.emit()
        self.accept()
