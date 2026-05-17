"""Диалог выбора типа проекта при создании"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout, QWidget, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QFont

from logiccraft.utils.icon_manager import icon_manager


class DiagramTypeCard(QPushButton):
    """Карточка типа диаграммы с превью"""

    def __init__(self, diagram_type: str, title: str, description: str,
                 icon_text: str, is_available: bool = True,
                 width: int = 240, height: int = 280):
        super().__init__()
        self.diagram_type = diagram_type
        self.is_available = is_available

        self.setCursor(Qt.CursorShape.PointingHandCursor if is_available else Qt.CursorShape.ForbiddenCursor)
        self.setFixedSize(width, height)
        self.setEnabled(is_available)

        if is_available:
            self.setObjectName("DiagramTypeCard")
        else:
            self.setObjectName("DiagramTypeCardDisabled")

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Превью диаграммы
        preview = self._create_preview(icon_text, is_available)
        preview_label = QLabel()
        preview_label.setPixmap(preview)
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(preview_label)

        # Заголовок
        title_label = QLabel(title)
        title_label.setObjectName("DiagramTypeTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        # Описание
        desc_label = QLabel(description)
        desc_label.setObjectName("DiagramTypeDescription")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Бейдж "Скоро" для недоступных
        if not is_available:
            badge = QLabel("Скоро")
            badge.setObjectName("ComingSoonBadge")
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(badge)

        layout.addStretch()

    def _create_preview(self, icon_text: str, is_available: bool) -> QPixmap:
        """Создать превью диаграммы"""
        pixmap = QPixmap(200, 140)
        pixmap.fill(QColor("#F9F7FF") if is_available else QColor("#F5F5F5"))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Рамка
        pen = QPen(QColor("#E5E0F8") if is_available else QColor("#E0E0E0"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRoundedRect(1, 1, 198, 138, 8, 8)

        # Иконка/текст в центре
        font = QFont("Arial", 42, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor("#7C3AED") if is_available else QColor("#CCCCCC"))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, icon_text)

        painter.end()
        return pixmap


class ProjectTypeDialog(QDialog):
    """Диалог выбора типа проекта"""

    diagram_type_selected = pyqtSignal(str)  # diagram_type

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создать новый проект")
        self.resize(1000, 700)
        self.setModal(True)
        self.setObjectName("ProjectTypeDialog")

        self.selected_type = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # Заголовок
        header_layout = QVBoxLayout()
        header_layout.setSpacing(10)

        title = QLabel("Выберите тип диаграммы")
        title.setObjectName("ProjectTypeDialogTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)

        subtitle = QLabel("Вы сможете добавить другие типы диаграмм позже")
        subtitle.setObjectName("ProjectTypeDialogSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle)

        layout.addLayout(header_layout)

        # Скролл-область для карточек
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setObjectName("ProjectTypeScrollArea")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        # Сетка карточек
        grid = QGridLayout()
        grid.setSpacing(20)
        grid.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Определяем типы диаграмм
        diagram_types = [
            {
                "type": "class",
                "title": "Диаграмма классов",
                "description": "Структура классов, атрибуты, методы и связи между ними",
                "icon": "📦",
                "available": True
            },
            {
                "type": "use_case",
                "title": "Use Case диаграмма",
                "description": "Актёры, сценарии использования и их взаимодействия",
                "icon": "👤",
                "available": True
            },
            {
                "type": "sequence",
                "title": "Sequence диаграмма",
                "description": "Временная последовательность взаимодействий между объектами",
                "icon": "⏱️",
                "available": False
            },
            {
                "type": "package",
                "title": "Package диаграмма",
                "description": "Организация классов в пакеты и зависимости между ними",
                "icon": "📁",
                "available": False
            },
            {
                "type": "activity",
                "title": "Activity диаграмма",
                "description": "Поток действий, решений и параллельных процессов",
                "icon": "🔄",
                "available": False
            },
            {
                "type": "state",
                "title": "State Machine диаграмма",
                "description": "Состояния объекта и переходы между ними",
                "icon": "🔀",
                "available": False
            },
            {
                "type": "component",
                "title": "Component диаграмма",
                "description": "Компоненты системы и их интерфейсы",
                "icon": "⬡",
                "available": False
            },
            {
                "type": "deployment",
                "title": "Deployment диаграмма",
                "description": "Физическое размещение компонентов на узлах",
                "icon": "🖥️",
                "available": False
            },
            {
                "type": "object",
                "title": "Object диаграмма",
                "description": "Экземпляры классов с конкретными значениями",
                "icon": "🎯",
                "available": False
            }
        ]

        # Создаём карточки в сетке 3x3
        row, col = 0, 0
        for dt in diagram_types:
            card = DiagramTypeCard(
                diagram_type=dt["type"],
                title=dt["title"],
                description=dt["description"],
                icon_text=dt["icon"],
                is_available=dt["available"]
            )
            if dt["available"]:
                card.clicked.connect(lambda checked, t=dt["type"]: self._on_type_selected(t))

            grid.addWidget(card, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1

        scroll_layout.addLayout(grid)
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # Кнопки внизу
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("SecondaryButton")
        cancel_btn.setFixedHeight(40)
        cancel_btn.setMinimumWidth(120)
        cancel_btn.clicked.connect(self.reject)

        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

    def _on_type_selected(self, diagram_type: str):
        """Обработка выбора типа диаграммы"""
        self.selected_type = diagram_type
        self.diagram_type_selected.emit(diagram_type)
        self.accept()

    def get_selected_type(self) -> str:
        """Получить выбранный тип диаграммы"""
        return self.selected_type
