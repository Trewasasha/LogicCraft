"""Стартовое окно приложения"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal

from pathlib import Path
from logiccraft.utils.icon_manager import icon_manager


class WelcomeCard(QPushButton):
    """Карточка действия на стартовом экране"""

    def __init__(self, icon, title: str, subtitle: str, is_primary: bool = False):
        super().__init__()
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(200, 180)

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

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel()
        icon_label.setObjectName(icon_obj_name)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setPixmap(icon.pixmap(48, 48))
        layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setObjectName(title_obj_name)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

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
        self.setWindowTitle("LogicCraft — Добро пожаловать")
        self.resize(700, 560)
        self.setMinimumSize(500, 400)
        self.setModal(True)
        self.setObjectName("WelcomeDialog")
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(40)

        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.setSpacing(15)

        maus_icon = icon_manager.get_icon("maus")
        if not maus_icon.isNull():
            maus_label = QLabel()
            maus_label.setPixmap(maus_icon.pixmap(56, 56))
            top_layout.addWidget(maus_label)

        title = QLabel("СХЕМАТУС")
        title.setObjectName("WelcomeTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)



        top_layout.addWidget(title)

        layout.addLayout(top_layout)

        subtitle = QLabel("Начните работу с вашими схемами и классами")
        subtitle.setObjectName("WelcomeSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(30)

        folder_icon = icon_manager.get_icon("folder")
        open_card = WelcomeCard(
            icon=folder_icon,
            title="Открыть проект",
            subtitle="Выберите существующий проект",
            is_primary=False
        )
        open_card.clicked.connect(self._on_open_project)
        cards_layout.addWidget(open_card)

        add_icon = icon_manager.get_icon("add")
        new_card = WelcomeCard(
            icon=add_icon,
            title="Создать новый проект",
            subtitle="Начните с чистого листа",
            is_primary=True
        )
        new_card.clicked.connect(self._on_new_project)
        cards_layout.addWidget(new_card)

        layout.addLayout(cards_layout)

    def _on_new_project(self):
        self.new_project_requested.emit()
        self.accept()

    def _on_open_project(self):
        self.open_project_requested.emit()
        self.accept()