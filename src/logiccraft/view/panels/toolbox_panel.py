"""Левая панель инструментов — типы элементов и связей"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class ToolboxSection(QWidget):
    """Секция с заголовком и кнопками"""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        label = QLabel(title)
        label.setObjectName("ToolboxSectionTitle")
        layout.addWidget(label)

        self._buttons_layout = QVBoxLayout()
        self._buttons_layout.setSpacing(4)
        layout.addLayout(self._buttons_layout)

    def add_button(self, btn: QPushButton):
        self._buttons_layout.addWidget(btn)


class ToolboxButton(QPushButton):
    """Кнопка элемента в тулбоксе"""

    def __init__(self, icon: str, label: str, data: str, parent=None):
        super().__init__(f"  {icon}  {label}", parent)
        self.setObjectName("ToolboxButton")
        self.data = data
        self.setFixedHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


class ToolboxPanel(QWidget):
    """Левая панель с типами UML элементов и связей"""

    # Сигналы
    add_element_requested = pyqtSignal(str)   # node_type или uc_actor / uc_scenario
    set_connection_mode = pyqtSignal(str)      # connection_type

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ToolboxPanel")
        self.setFixedWidth(200)
        self._setup_ui()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Прокручиваемая область — чтобы все секции влезали
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Заголовок панели
        title = QLabel("Элементы")
        title.setObjectName("ToolboxTitle")
        layout.addWidget(title)

        # ── Секция: Диаграмма классов ──────────────────────────────────────────
        elements_section = ToolboxSection("Классы")

        btn_class = ToolboxButton("⬡", "Класс", "class")
        btn_class.clicked.connect(lambda: self.add_element_requested.emit("class"))
        elements_section.add_button(btn_class)

        btn_abstract = ToolboxButton("△", "Абстрактный", "abstract_class")
        btn_abstract.clicked.connect(lambda: self.add_element_requested.emit("abstract_class"))
        elements_section.add_button(btn_abstract)

        btn_interface = ToolboxButton("◇", "Интерфейс", "interface")
        btn_interface.clicked.connect(lambda: self.add_element_requested.emit("interface"))
        elements_section.add_button(btn_interface)

        btn_enum = ToolboxButton("≡", "Перечисление", "enum")
        btn_enum.clicked.connect(lambda: self.add_element_requested.emit("enum"))
        elements_section.add_button(btn_enum)

        layout.addWidget(elements_section)
        layout.addWidget(self._make_divider())

        # ── Секция: Связи классов ──────────────────────────────────────────────
        connections_section = ToolboxSection("Связи классов")

        conn_types = [
            ("→", "Ассоциация", "association"),
            ("▷", "Наследование", "inheritance"),
            ("◆", "Композиция", "composition"),
            ("◇", "Агрегация", "aggregation"),
            ("⇢", "Зависимость", "dependency"),
            ("⇒", "Реализация", "realization"),
        ]
        for icon, label, ctype in conn_types:
            btn = ToolboxButton(icon, label, ctype)
            btn.clicked.connect(lambda checked, t=ctype: self.set_connection_mode.emit(t))
            connections_section.add_button(btn)

        layout.addWidget(connections_section)
        layout.addWidget(self._make_divider())

        # ── Секция: Use Case элементы ──────────────────────────────────────────
        uc_elements_section = ToolboxSection("Use Case")

        btn_actor = ToolboxButton("🧍", "Актёр", "uc_actor")
        btn_actor.clicked.connect(lambda: self.add_element_requested.emit("uc_actor"))
        uc_elements_section.add_button(btn_actor)

        btn_scenario = ToolboxButton("○", "Сценарий", "uc_scenario")
        btn_scenario.clicked.connect(lambda: self.add_element_requested.emit("uc_scenario"))
        uc_elements_section.add_button(btn_scenario)

        layout.addWidget(uc_elements_section)
        layout.addWidget(self._make_divider())

        # ── Секция: Связи Use Case ─────────────────────────────────────────────
        uc_conn_section = ToolboxSection("Связи Use Case")

        uc_conn_types = [
            ("—", "Ассоциация", "uc_association"),
            ("⇢", "Include", "uc_include"),
            ("⇠", "Extend", "uc_extend"),
        ]
        for icon, label, ctype in uc_conn_types:
            btn = ToolboxButton(icon, label, ctype)
            btn.clicked.connect(lambda checked, t=ctype: self.set_connection_mode.emit(t))
            uc_conn_section.add_button(btn)

        layout.addWidget(uc_conn_section)
        layout.addStretch()

    def _make_divider(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setObjectName("ToolboxDivider")
        return line

    def set_diagram_type(self, diagram_type: str):
        """Показать только инструменты для выбранного типа диаграммы"""
        # Получаем все секции
        sections = self.findChildren(ToolboxSection)
        
        for section in sections:
            title = section.title() if hasattr(section, 'title') else ""
            # Получаем заголовок из первого QLabel
            label = section.findChild(QLabel)
            section_title = label.text() if label else ""
            
            if diagram_type == "class":
                # Показываем только секции для диаграммы классов
                if section_title in ["Классы", "Связи классов"]:
                    section.setVisible(True)
                else:
                    section.setVisible(False)
            elif diagram_type == "use_case":
                # Показываем только секции для Use Case диаграммы
                if section_title in ["Use Case", "Связи Use Case"]:
                    section.setVisible(True)
                else:
                    section.setVisible(False)
