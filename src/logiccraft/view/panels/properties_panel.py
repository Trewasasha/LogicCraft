"""Правая панель свойств выбранного элемента"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QComboBox, QFrame, QScrollArea,
    QSizePolicy, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont


NODE_TYPE_OPTIONS = [
    ("⬡  Класс", "class"),
    ("△  Абстрактный", "abstract_class"),
    ("◇  Интерфейс", "interface"),
    ("≡  Перечисление", "enum"),
]


class PropertiesPanel(QWidget):
    """Правая панель свойств выбранного UML элемента"""

    # Сигналы для обновления модели
    name_changed = pyqtSignal(str, str)           # card_id, new_name
    type_changed = pyqtSignal(str, str)           # card_id, new_type
    attributes_changed = pyqtSignal(str, list)    # card_id, attributes
    methods_changed = pyqtSignal(str, list)       # card_id, methods
    delete_requested = pyqtSignal(str)            # card_id
    # Use Case сигналы
    uc_actor_name_changed = pyqtSignal(str, str)      # actor_id, new_name
    uc_scenario_name_changed = pyqtSignal(str, str)   # scenario_id, new_name
    uc_scenario_desc_changed = pyqtSignal(str, str)   # scenario_id, new_description
    uc_element_delete_requested = pyqtSignal(str, str) # element_id, element_type

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PropertiesPanel")
        self.setFixedWidth(220)
        self._current_card_id = None
        self._current_uc_id = None
        self._current_uc_type = None
        self._updating = False  # флаг чтобы не зациклить сигналы
        self._setup_ui()
        self.show_empty()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Заголовок панели
        title = QLabel("Свойства")
        title.setObjectName("PropertiesPanelTitle")
        outer.addWidget(title)

        # Скролл-область для содержимого
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setObjectName("PropertiesScroll")

        self._content = QWidget()
        self._content.setObjectName("PropertiesContent")
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(12, 12, 12, 12)
        self._content_layout.setSpacing(12)
        self._content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(self._content)
        outer.addWidget(scroll)

        # Пустое состояние
        self._empty_label = QLabel("Выберите элемент\nна диаграмме")
        self._empty_label.setObjectName("PropertiesEmptyLabel")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._content_layout.addWidget(self._empty_label)

        # --- Блок: Имя ---
        self._name_section = self._make_section("Имя")
        self._name_edit = QLineEdit()
        self._name_edit.setObjectName("PropertiesInput")
        self._name_edit.setPlaceholderText("Название класса")
        self._name_edit.textChanged.connect(self._on_name_changed)
        self._name_section.layout().addWidget(self._name_edit)
        self._content_layout.addWidget(self._name_section)

        # --- Блок: Тип ---
        self._type_section = self._make_section("Тип")
        self._type_combo = QComboBox()
        self._type_combo.setObjectName("PropertiesCombo")
        for label, value in NODE_TYPE_OPTIONS:
            self._type_combo.addItem(label, value)
        self._type_combo.currentIndexChanged.connect(self._on_type_changed)
        self._type_section.layout().addWidget(self._type_combo)
        self._content_layout.addWidget(self._type_section)

        # --- Блок: Атрибуты ---
        self._attrs_section = self._make_section("Атрибуты")
        self._attrs_list = QListWidget()
        self._attrs_list.setObjectName("PropertiesList")
        self._attrs_list.setMaximumHeight(120)
        self._attrs_section.layout().addWidget(self._attrs_list)

        attrs_btns = QHBoxLayout()
        add_attr_btn = QPushButton("+ Добавить")
        add_attr_btn.setObjectName("PropertiesSmallButton")
        add_attr_btn.clicked.connect(self._on_add_attribute)
        rm_attr_btn = QPushButton("Удалить")
        rm_attr_btn.setObjectName("PropertiesSmallButtonDanger")
        rm_attr_btn.clicked.connect(self._on_remove_attribute)
        attrs_btns.addWidget(add_attr_btn)
        attrs_btns.addWidget(rm_attr_btn)
        self._attrs_section.layout().addLayout(attrs_btns)
        self._content_layout.addWidget(self._attrs_section)

        # --- Блок: Методы ---
        self._methods_section = self._make_section("Методы")
        self._methods_list = QListWidget()
        self._methods_list.setObjectName("PropertiesList")
        self._methods_list.setMaximumHeight(120)
        self._methods_section.layout().addWidget(self._methods_list)

        methods_btns = QHBoxLayout()
        add_method_btn = QPushButton("+ Добавить")
        add_method_btn.setObjectName("PropertiesSmallButton")
        add_method_btn.clicked.connect(self._on_add_method)
        rm_method_btn = QPushButton("Удалить")
        rm_method_btn.setObjectName("PropertiesSmallButtonDanger")
        rm_method_btn.clicked.connect(self._on_remove_method)
        methods_btns.addWidget(add_method_btn)
        methods_btns.addWidget(rm_method_btn)
        self._methods_section.layout().addLayout(methods_btns)
        self._content_layout.addWidget(self._methods_section)

        # --- Кнопка удаления ---
        self._delete_btn = QPushButton("🗑  Удалить элемент")
        self._delete_btn.setObjectName("PropertiesDeleteButton")
        self._delete_btn.clicked.connect(self._on_delete)
        self._content_layout.addWidget(self._delete_btn)

        # --- Use Case элементы (скрыты по умолчанию) ---
        self._uc_name_section = self._make_section("Имя")
        self._uc_name_edit = QLineEdit()
        self._uc_name_edit.setObjectName("PropertiesInput")
        self._uc_name_edit.setPlaceholderText("Название")
        self._uc_name_edit.textChanged.connect(self._on_uc_name_changed)
        self._uc_name_section.layout().addWidget(self._uc_name_edit)
        self._content_layout.addWidget(self._uc_name_section)
        
        self._uc_desc_section = self._make_section("Описание")
        from PyQt6.QtWidgets import QTextEdit
        self._uc_desc_edit = QTextEdit()
        self._uc_desc_edit.setObjectName("PropertiesTextEdit")
        self._uc_desc_edit.setPlaceholderText("Описание сценария...")
        self._uc_desc_edit.setMaximumHeight(100)
        self._uc_desc_edit.textChanged.connect(self._on_uc_desc_changed)
        self._uc_desc_section.layout().addWidget(self._uc_desc_edit)
        self._content_layout.addWidget(self._uc_desc_section)
        
        self._uc_delete_btn = QPushButton("🗑  Удалить элемент")
        self._uc_delete_btn.setObjectName("PropertiesDeleteButton")
        self._uc_delete_btn.clicked.connect(self._on_uc_delete)
        self._content_layout.addWidget(self._uc_delete_btn)

        self._content_layout.addStretch()

        # Скрываем всё кроме пустого состояния
        self._set_card_widgets_visible(False)
        self._set_uc_widgets_visible(False)

    def _make_section(self, title: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        label = QLabel(title)
        label.setObjectName("PropertiesSectionLabel")
        layout.addWidget(label)
        return widget

    def _set_card_widgets_visible(self, visible: bool):
        self._empty_label.setVisible(not visible)
        self._name_section.setVisible(visible)
        self._type_section.setVisible(visible)
        self._attrs_section.setVisible(visible)
        self._methods_section.setVisible(visible)
        self._delete_btn.setVisible(visible)
    
    def _set_uc_widgets_visible(self, visible: bool, show_desc: bool = False):
        """Показать/скрыть виджеты Use Case элементов"""
        self._empty_label.setVisible(not visible)
        self._uc_name_section.setVisible(visible)
        self._uc_desc_section.setVisible(visible and show_desc)
        self._uc_delete_btn.setVisible(visible)

    # --- Публичные методы ---

    def show_empty(self):
        """Показать пустое состояние"""
        self._current_card_id = None
        self._current_uc_id = None
        self._current_uc_type = None
        self._set_card_widgets_visible(False)
        self._set_uc_widgets_visible(False)

    def show_card(self, card_id: str, name: str, node_type: str,
                  attributes: list, methods: list):
        """Показать свойства карточки"""
        self._updating = True
        self._current_card_id = card_id
        self._current_uc_id = None

        self._name_edit.setText(name)

        # Устанавливаем тип
        for i in range(self._type_combo.count()):
            if self._type_combo.itemData(i) == node_type:
                self._type_combo.setCurrentIndex(i)
                break

        # Атрибуты
        self._attrs_list.clear()
        for attr in attributes:
            self._attrs_list.addItem(attr)

        # Методы
        self._methods_list.clear()
        for method in methods:
            self._methods_list.addItem(method)

        self._set_card_widgets_visible(True)
        self._set_uc_widgets_visible(False)
        self._updating = False
    
    def show_uc_actor(self, actor_id: str, name: str):
        """Показать свойства актёра Use Case"""
        self._updating = True
        self._current_uc_id = actor_id
        self._current_uc_type = "actor"
        self._current_card_id = None
        
        self._uc_name_edit.setText(name)
        
        self._set_card_widgets_visible(False)
        self._set_uc_widgets_visible(True, show_desc=False)
        self._updating = False
    
    def show_uc_scenario(self, scenario_id: str, name: str, description: str = ""):
        """Показать свойства сценария Use Case"""
        self._updating = True
        self._current_uc_id = scenario_id
        self._current_uc_type = "scenario"
        self._current_card_id = None
        
        self._uc_name_edit.setText(name)
        self._uc_desc_edit.setPlainText(description or "")
        
        self._set_card_widgets_visible(False)
        self._set_uc_widgets_visible(True, show_desc=True)
        self._updating = False

    # --- Обработчики изменений ---

    def _on_name_changed(self, text: str):
        if self._updating or not self._current_card_id:
            return
        # Дебаунс — не шлём сигнал при каждом символе
        if not hasattr(self, '_name_timer'):
            self._name_timer = QTimer()
            self._name_timer.setSingleShot(True)
            self._name_timer.timeout.connect(self._emit_name_changed)
        self._name_timer.start(500)

    def _emit_name_changed(self):
        if self._current_card_id:
            self.name_changed.emit(self._current_card_id, self._name_edit.text())

    def _on_type_changed(self):
        if self._updating or not self._current_card_id:
            return
        new_type = self._type_combo.currentData()
        self.type_changed.emit(self._current_card_id, new_type)

    def _on_add_attribute(self):
        if not self._current_card_id:
            return
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "Добавить атрибут", "Атрибут (например: +name: str):")
        if ok and text:
            self._attrs_list.addItem(text)
            self._emit_attributes()

    def _on_remove_attribute(self):
        row = self._attrs_list.currentRow()
        if row >= 0:
            self._attrs_list.takeItem(row)
            self._emit_attributes()

    def _on_add_method(self):
        if not self._current_card_id:
            return
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "Добавить метод", "Метод (например: +login(): void):")
        if ok and text:
            self._methods_list.addItem(text)
            self._emit_methods()

    def _on_remove_method(self):
        row = self._methods_list.currentRow()
        if row >= 0:
            self._methods_list.takeItem(row)
            self._emit_methods()

    def _emit_attributes(self):
        if self._current_card_id:
            attrs = [self._attrs_list.item(i).text()
                     for i in range(self._attrs_list.count())]
            self.attributes_changed.emit(self._current_card_id, attrs)

    def _emit_methods(self):
        if self._current_card_id:
            methods = [self._methods_list.item(i).text()
                       for i in range(self._methods_list.count())]
            self.methods_changed.emit(self._current_card_id, methods)

    def _on_delete(self):
        if self._current_card_id:
            self.delete_requested.emit(self._current_card_id)
            self.show_empty()
    
    # --- Use Case обработчики ---
    
    def _on_uc_name_changed(self, text: str):
        if self._updating or not self._current_uc_id:
            return
        if not hasattr(self, '_uc_name_timer'):
            self._uc_name_timer = QTimer()
            self._uc_name_timer.setSingleShot(True)
            self._uc_name_timer.timeout.connect(self._emit_uc_name_changed)
        self._uc_name_timer.start(500)
    
    def _emit_uc_name_changed(self):
        if self._current_uc_id and self._current_uc_type:
            if self._current_uc_type == "actor":
                self.uc_actor_name_changed.emit(self._current_uc_id, self._uc_name_edit.text())
            elif self._current_uc_type == "scenario":
                self.uc_scenario_name_changed.emit(self._current_uc_id, self._uc_name_edit.text())
    
    def _on_uc_desc_changed(self):
        if self._updating or not self._current_uc_id or self._current_uc_type != "scenario":
            return
        if not hasattr(self, '_uc_desc_timer'):
            self._uc_desc_timer = QTimer()
            self._uc_desc_timer.setSingleShot(True)
            self._uc_desc_timer.timeout.connect(self._emit_uc_desc_changed)
        self._uc_desc_timer.start(500)
    
    def _emit_uc_desc_changed(self):
        if self._current_uc_id and self._current_uc_type == "scenario":
            self.uc_scenario_desc_changed.emit(self._current_uc_id, self._uc_desc_edit.toPlainText())
    
    def _on_uc_delete(self):
        if self._current_uc_id and self._current_uc_type:
            self.uc_element_delete_requested.emit(self._current_uc_id, self._current_uc_type)
            self.show_empty()
