"""Главное окно приложения"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QToolBar, QLabel, QFileDialog, QMessageBox, QGraphicsView,
    QMenu, QMenuBar, QDockWidget, QSizePolicy, QToolButton
)
from PyQt6.QtGui import QAction, QPainter, QKeySequence
from PyQt6.QtCore import pyqtSignal, Qt, QTimer, QSize

from .scenes.diagram_scene import DiagramScene
from .widgets.uml_card import UMLCard
from .widgets.connection_line import ConnectionLine
from .dialogs.edit_class_dialog import EditClassDialog
from .dialogs.connection_properties import ConnectionPropertiesDialog
from .dialogs.code_generation_dialog import CodeGenerationDialog
from .dialogs.project_export_dialog import ProjectExportDialog
from .dialogs.validation_results_dialog import ValidationResultsDialog
from .panels.toolbox_panel import ToolboxPanel
from .panels.properties_panel import PropertiesPanel
from .builders import MenuBarBuilder, ToolBarBuilder, StatusBarBuilder
from logiccraft.utils.icon_manager import icon_manager


class DiagramView(QGraphicsView):
    """Вид для отображения сцены с поддержкой навигации"""

    zoom_changed = pyqtSignal(int)  # процент масштаба

    def __init__(self, scene: DiagramScene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.scale_factor = 1.15
        self._zoom_level = 100  # текущий масштаб в %
        self._min_zoom = 20
        self._max_zoom = 400
        self._panning = False
        self._pan_start = None
        self.main_window = parent

    def keyPressEvent(self, event):
        if self.main_window and hasattr(self.main_window, 'handle_key_press'):
            if self.main_window.handle_key_press(event):
                return
        # Пробел — режим панорамирования
        if event.key() == Qt.Key.Key_Space:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        super().keyReleaseEvent(event)

    def wheelEvent(self, event):
        """Zoom колесом мыши + Ctrl, прокрутка без Ctrl"""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self._zoom_in()
            else:
                self._zoom_out()
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        """Средняя кнопка — панорамирование"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._pan_start = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._panning and self._pan_start is not None:
            delta = event.position().toPoint() - self._pan_start
            self._pan_start = event.position().toPoint()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _zoom_in(self):
        if self._zoom_level < self._max_zoom:
            self.scale(self.scale_factor, self.scale_factor)
            self._zoom_level = min(self._max_zoom, int(self._zoom_level * self.scale_factor))
            self.zoom_changed.emit(self._zoom_level)

    def _zoom_out(self):
        if self._zoom_level > self._min_zoom:
            self.scale(1 / self.scale_factor, 1 / self.scale_factor)
            self._zoom_level = max(self._min_zoom, int(self._zoom_level / self.scale_factor))
            self.zoom_changed.emit(self._zoom_level)

    def set_zoom(self, percent: int):
        """Установить масштаб в процентах"""
        percent = max(self._min_zoom, min(self._max_zoom, percent))
        factor = percent / self._zoom_level
        self.scale(factor, factor)
        self._zoom_level = percent
        self.zoom_changed.emit(self._zoom_level)

    def reset_zoom(self):
        """Сбросить масштаб до 100%"""
        self.set_zoom(100)

    def fit_in_view_all(self):
        """Вписать всю диаграмму в экран"""
        items = self.scene().items()
        if not items:
            return
        self.fitInView(self.scene().itemsBoundingRect().adjusted(-40, -40, 40, 40),
                       Qt.AspectRatioMode.KeepAspectRatio)
        # Обновляем zoom_level
        transform = self.transform()
        self._zoom_level = int(transform.m11() * 100)
        self.zoom_changed.emit(self._zoom_level)


class MainWindow(QMainWindow):
    """Главное окно приложения"""

    # Сигналы для контроллера
    add_card_requested = pyqtSignal(float, float, str)  # x, y, node_type
    save_requested = pyqtSignal(str)
    load_requested = pyqtSignal(str)
    clear_requested = pyqtSignal()
    edit_card_requested = pyqtSignal(str, str, list, list)
    delete_selected_requested = pyqtSignal()
    edit_connection_requested = pyqtSignal(str, str)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.card_map = {}
        self.connection_map = {}
        self.uc_actor_map = {}      # actor_id -> ActorWidget
        self.uc_scenario_map = {}   # scenario_id -> ScenarioWidget
        self.uc_connection_map = {} # conn_id -> ConnectionLine
        self._search_widget = None  # Виджет поиска
        self.setWindowTitle("LogicCraft UML Architect")
        self.setGeometry(100, 100, 1400, 860)

        # Устанавливаем иконку окна
        window_icon = icon_manager.get_icon("icon2")
        if not window_icon.isNull():
            self.setWindowIcon(window_icon)

        self._setup_ui()
        self._setup_panels()
        self._connect_signals()
        self._connect_controller_signals()
        
        # Используем билдеры для создания UI компонентов
        self._setup_menubar_with_builder()
        self._setup_toolbar_with_builder()
        self._setup_statusbar_with_builder()

    def _setup_menubar_with_builder(self):
        """Настройка менюбары через билдер"""
        builder = MenuBarBuilder(self)
        builder.build()
        # Подключаем сигналы undo/redo от контроллера
        self.controller.history.history_changed.connect(self._on_history_changed)

    def _setup_toolbar_with_builder(self):
        """Настройка тулбара через билдер"""
        builder = ToolBarBuilder(self)
        builder.build()

    def _setup_statusbar_with_builder(self):
        """Настройка статусбара через билдер"""
        builder = StatusBarBuilder(self)
        builder.build()

    def _setup_ui(self):
        """Настройка UI компонентов"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        central.setLayout(layout)

        self.scene = DiagramScene()
        self.view = DiagramView(self.scene, self)
        self.view.setStyleSheet("background-color: #F0EFFE; border: none;")
        layout.addWidget(self.view)

        # Панель статуса
        self.status_bar = self.statusBar()
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        # Правая часть статусбара — zoom контролы + статистика
        from PyQt6.QtWidgets import QPushButton, QSpinBox

        zoom_widget = QWidget()
        zoom_layout = QHBoxLayout(zoom_widget)
        zoom_layout.setContentsMargins(0, 0, 8, 0)
        zoom_layout.setSpacing(4)

        zoom_out_btn = QPushButton("−")
        zoom_out_btn.setFixedSize(22, 22)
        zoom_out_btn.setObjectName("ZoomButton")
        zoom_out_btn.clicked.connect(lambda: self.view._zoom_out())

        self.zoom_label = QLabel("100%")
        self.zoom_label.setObjectName("ZoomLabel")
        self.zoom_label.setFixedWidth(44)

        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedSize(22, 22)
        zoom_in_btn.setObjectName("ZoomButton")
        zoom_in_btn.clicked.connect(lambda: self.view._zoom_in())

        fit_btn = QPushButton("⊡")
        fit_btn.setFixedSize(22, 22)
        fit_btn.setObjectName("ZoomButton")
        fit_btn.setToolTip("Вписать в экран")
        fit_btn.clicked.connect(lambda: self.view.fit_in_view_all())

        reset_btn = QPushButton("1:1")
        reset_btn.setFixedSize(28, 22)
        reset_btn.setObjectName("ZoomButton")
        reset_btn.setToolTip("Сбросить масштаб")
        reset_btn.clicked.connect(lambda: self.view.reset_zoom())

        zoom_layout.addWidget(zoom_out_btn)
        zoom_layout.addWidget(self.zoom_label)
        zoom_layout.addWidget(zoom_in_btn)
        zoom_layout.addWidget(fit_btn)
        zoom_layout.addWidget(reset_btn)

        self.stats_label = QLabel("")
        self.stats_label.setObjectName("StatusBarStats")

        self.status_bar.addPermanentWidget(self.stats_label)
        self.status_bar.addPermanentWidget(zoom_widget)

    def _setup_panels(self):
        """Настройка боковых панелей через QDockWidget"""
        # Левая панель — Toolbox
        self.toolbox_panel = ToolboxPanel()
        toolbox_dock = QDockWidget("Инструменты", self)
        toolbox_dock.setWidget(self.toolbox_panel)
        toolbox_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.RightDockWidgetArea
        )
        toolbox_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, toolbox_dock)

        # Правая панель — Properties
        self.properties_panel = PropertiesPanel()
        properties_dock = QDockWidget("Свойства", self)
        properties_dock.setWidget(self.properties_panel)
        properties_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.RightDockWidgetArea
        )
        properties_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, properties_dock)

        # Подключаем сигналы Toolbox
        self.toolbox_panel.add_element_requested.connect(self._on_toolbox_add_element)
        self.toolbox_panel.set_connection_mode.connect(self._on_toolbox_set_connection_type)

        # Подключаем сигналы Properties
        self.properties_panel.name_changed.connect(self._on_properties_name_changed)
        self.properties_panel.type_changed.connect(self._on_properties_type_changed)
        self.properties_panel.attributes_changed.connect(self._on_properties_attrs_changed)
        self.properties_panel.methods_changed.connect(self._on_properties_methods_changed)
        self.properties_panel.delete_requested.connect(self._on_properties_delete)
        # Use Case сигналы
        self.properties_panel.uc_actor_name_changed.connect(self._on_uc_actor_name_changed)
        self.properties_panel.uc_scenario_name_changed.connect(self._on_uc_scenario_name_changed)
        self.properties_panel.uc_scenario_desc_changed.connect(self._on_uc_scenario_desc_changed)
        self.properties_panel.uc_element_delete_requested.connect(self._on_uc_element_delete)

        # Слушаем изменение выделения на сцене
        self.scene.selectionChanged.connect(self._on_scene_selection_changed)

        # Подключаем zoom сигнал
        self.view.zoom_changed.connect(self._on_zoom_changed)

    def _on_toolbox_add_element(self, node_type: str):
        """Добавить элемент из тулбокса в центр холста"""
        center = self.view.mapToScene(self.view.viewport().rect().center())
        import random
        offset_x = random.randint(-60, 60)
        offset_y = random.randint(-60, 60)
        x = center.x() + offset_x
        y = center.y() + offset_y

        if node_type == "uc_actor":
            self.controller.add_uc_actor(x, y)
        elif node_type == "uc_scenario":
            self.controller.add_uc_scenario(x, y)
        else:
            self.add_card_requested.emit(x, y, node_type)

    def _on_toolbox_set_connection_type(self, connection_type: str):
        """Применить тип связи к выбранной связи или запомнить для следующей"""
        # Ищем выбранную связь на сцене
        selected_connections = [
            item for item in self.scene.selectedItems()
            if isinstance(item, ConnectionLine)
        ]
        if selected_connections:
            # Меняем тип у всех выбранных связей
            for conn in selected_connections:
                self.controller.update_connection_type(conn.id, connection_type)
                conn.set_connection_type(connection_type)
                conn.update_position()
            self.update_status(f"Тип связи изменён: {connection_type}")
        else:
            # Запоминаем тип для следующей создаваемой связи
            self._default_connection_type = connection_type
            self.update_status(f"Следующая связь: {connection_type}")

    def _on_scene_selection_changed(self):
        """Обновить панель свойств при изменении выделения"""
        from .widgets.actor_widget import ActorWidget
        from .widgets.scenario_widget import ScenarioWidget
        
        selected_items = self.scene.selectedItems()
        
        # Проверяем UML карточки
        selected_cards = [item for item in selected_items if isinstance(item, UMLCard)]
        if selected_cards:
            card = selected_cards[0]
            node_type = card.node_type
            if hasattr(node_type, 'value'):
                node_type = node_type.value
            self.properties_panel.show_card(
                card_id=card.id,
                name=card.name,
                node_type=node_type,
                attributes=card.attributes,
                methods=card.methods
            )
            # Подсвечиваем связанные классы
            self.scene.highlight_related_cards(card.id, self.card_map, self.connection_map)
            return
        
        # Проверяем Use Case актёров
        selected_actors = [item for item in selected_items if isinstance(item, ActorWidget)]
        if selected_actors:
            actor = selected_actors[0]
            self.properties_panel.show_uc_actor(actor.id, actor.name)
            return
        
        # Проверяем Use Case сценарии
        selected_scenarios = [item for item in selected_items if isinstance(item, ScenarioWidget)]
        if selected_scenarios:
            scenario = selected_scenarios[0]
            # Получаем описание из модели
            scenario_model = next((s for s in self.controller.manager.diagram.uc_scenarios 
                                  if s.id == scenario.id), None)
            description = scenario_model.description if scenario_model else ""
            self.properties_panel.show_uc_scenario(scenario.id, scenario.name, description)
            return
        
        # Ничего не выбрано
        self.properties_panel.show_empty()
        # Снимаем подсветку если ничего не выбрано
        self.scene.clear_highlights(self.card_map, self.connection_map)

    def _on_properties_name_changed(self, card_id: str, name: str):
        card = self.card_map.get(card_id)
        if card and card.name != name:
            self.controller.edit_card(card_id, name, card.attributes, card.methods)
            card.name = name
            card.update_content()

    def _on_properties_type_changed(self, card_id: str, node_type: str):
        from logiccraft.models.diagram import NodeType
        card = self.card_map.get(card_id)
        if card:
            try:
                nt = NodeType(node_type)
            except ValueError:
                nt = NodeType.CLASS
            self.controller.update_card(card_id, node_type=nt)
            card.node_type = nt
            card.update_content()

    def _on_properties_attrs_changed(self, card_id: str, attributes: list):
        card = self.card_map.get(card_id)
        if card:
            self.controller.edit_card(card_id, card.name, attributes, card.methods)
            card.attributes = attributes
            card.update_content()

    def _on_properties_methods_changed(self, card_id: str, methods: list):
        card = self.card_map.get(card_id)
        if card:
            self.controller.edit_card(card_id, card.name, card.attributes, methods)
            card.methods = methods
            card.update_content()

    def _on_properties_delete(self, card_id: str):
        self.controller.remove_card(card_id)
    
    def _on_uc_actor_name_changed(self, actor_id: str, name: str):
        """Обработка изменения имени актёра из Properties панели"""
        widget = self.uc_actor_map.get(actor_id)
        if widget and widget.name != name:
            widget.update_name(name)
            self.controller.update_uc_actor(actor_id, name=name)
    
    def _on_uc_scenario_name_changed(self, scenario_id: str, name: str):
        """Обработка изменения имени сценария из Properties панели"""
        widget = self.uc_scenario_map.get(scenario_id)
        if widget and widget.name != name:
            widget.update_name(name)
            self.controller.update_uc_scenario(scenario_id, name=name)
    
    def _on_uc_scenario_desc_changed(self, scenario_id: str, description: str):
        """Обработка изменения описания сценария из Properties панели"""
        self.controller.update_uc_scenario(scenario_id, description=description)
    
    def _on_uc_element_delete(self, element_id: str, element_type: str):
        """Обработка удаления Use Case элемента из Properties панели"""
        if element_type == "actor":
            self.controller.remove_uc_actor(element_id)
        elif element_type == "scenario":
            self.controller.remove_uc_scenario(element_id)

    def _connect_signals(self):
        """Подключение сигналов сцены"""
        self.scene.connection_ready.connect(self._on_connection_ready)
        self.scene.card_moved.connect(self._on_card_moved)
        # UC-переименования подключаем один раз здесь
        self.scene.actor_renamed.connect(
            lambda aid, name: self.controller.update_uc_actor(aid, name=name)
        )
        self.scene.scenario_renamed.connect(
            lambda sid, name: self.controller.update_uc_scenario(sid, name=name)
        )

    def _connect_controller_signals(self):
        """Подключение сигналов контроллера"""
        self.controller.connection_updated.connect(self._on_connection_updated)
        self.controller.card_added.connect(self._on_card_added)
        self.controller.card_removed.connect(self._on_card_removed)
        self.controller.diagram_cleared.connect(self._on_diagram_cleared)
        self.controller.status_changed.connect(self.update_status)
        self.controller.error_occurred.connect(self.show_error)
        # Сигнал загрузки диаграммы - обновляем панель инструментов
        self.controller.diagram_loaded.connect(self._on_diagram_loaded)
        # Use Case сигналы
        self.controller.uc_actor_added.connect(self._on_uc_actor_added)
        self.controller.uc_actor_removed.connect(self._on_uc_actor_removed)
        self.controller.uc_scenario_added.connect(self._on_uc_scenario_added)
        self.controller.uc_scenario_removed.connect(self._on_uc_scenario_removed)
        self.controller.uc_connection_added.connect(self._on_uc_connection_added)
        self.controller.uc_connection_removed.connect(self._on_uc_connection_removed)

    def _on_zoom_changed(self, percent: int):
        """Обновить индикатор масштаба"""
        self.zoom_label.setText(f"{percent}%")
    
    def _on_diagram_loaded(self):
        """Обработка загрузки диаграммы - обновляем панель инструментов"""
        diagram_type = self.controller.manager.diagram.diagram_type
        # Синхронизируем комбобокс с типом загруженной диаграммы
        for i in range(self.diagram_type_combo.count()):
            if self.diagram_type_combo.itemData(i) == diagram_type:
                self.diagram_type_combo.setCurrentIndex(i)
                break
        # Обновляем панель инструментов
        self.toolbox_panel.set_diagram_type(diagram_type)
    
    def _on_diagram_type_changed(self, index: int):
        """Обработка переключения типа диаграммы"""
        diagram_type = self.diagram_type_combo.itemData(index)
        
        # Обновляем тип диаграммы в модели
        self.controller.manager.diagram.diagram_type = diagram_type
        
        # Обновляем панель инструментов - показываем только нужные секции
        self.toolbox_panel.set_diagram_type(diagram_type)
        
        # Обновляем видимость элементов в зависимости от типа
        if diagram_type == "class":
            # Показываем классы, скрываем Use Case элементы
            for card in self.card_map.values():
                card.setVisible(True)
            for conn in self.connection_map.values():
                conn.setVisible(True)
            for actor in self.uc_actor_map.values():
                actor.setVisible(False)
            for scenario in self.uc_scenario_map.values():
                scenario.setVisible(False)
            for uc_conn in self.uc_connection_map.values():
                uc_conn.setVisible(False)
            self.update_status("Переключено на диаграмму классов")
        else:  # use_case
            # Скрываем классы, показываем Use Case элементы
            for card in self.card_map.values():
                card.setVisible(False)
            for conn in self.connection_map.values():
                conn.setVisible(False)
            for actor in self.uc_actor_map.values():
                actor.setVisible(True)
            for scenario in self.uc_scenario_map.values():
                scenario.setVisible(True)
            for uc_conn in self.uc_connection_map.values():
                uc_conn.setVisible(True)
            self.update_status("Переключено на Use Case диаграмму")

    def handle_key_press(self, event):
        """Обработка нажатий клавиш (вызывается из DiagramView)"""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_S:
            self._on_save_clicked()
            return True
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Z:
            self._on_undo()
            return True
        if event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier) and event.key() == Qt.Key.Key_Z:
            self._on_redo()
            return True
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Y:
            self._on_redo()
            return True
        if event.key() == Qt.Key.Key_Delete or event.key() == Qt.Key.Key_Backspace:
            self._on_delete_selected()
            return True
        # Zoom горячие клавиши
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Equal:
            self.view._zoom_in()
            return True
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Minus:
            self.view._zoom_out()
            return True
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_0:
            self.view.reset_zoom()
            return True
        # Поиск классов
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_F:
            self._show_search()
            return True
        # Вписать в экран
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_G:
            self.view.fit_in_view_all()
            return True
        # Копирование / вставка / дублирование / выделить всё
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_C:
            self._on_copy()
            return True
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_V:
            self._on_paste()
            return True
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_D:
            self._on_duplicate()
            return True
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_A:
            self._on_select_all()
            return True
        # Переименование выбранного элемента (F2 или Ctrl+M)
        if event.key() == Qt.Key.Key_F2:
            self._on_inline_rename()
            return True
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_M:
            self._on_rename_selected()
            return True
        return False
    
    def keyPressEvent(self, event):
        """Обработка нажатий клавиш (для MainWindow)"""
        if not self.handle_key_press(event):
            super().keyPressEvent(event)
    
    def _on_add_clicked(self):
        """Обработка добавления карточки — обычный класс"""
        center = self.view.mapToScene(self.view.viewport().rect().center())
        self.add_card_requested.emit(center.x(), center.y(), "class")

    def _on_copy(self):
        """Копировать выбранные элементы (классы + UC)"""
        from .widgets.actor_widget import ActorWidget
        from .widgets.scenario_widget import ScenarioWidget

        selected = self.scene.selectedItems()
        card_ids = [i.id for i in selected if isinstance(i, UMLCard)]
        actor_ids = [i.id for i in selected if isinstance(i, ActorWidget)]
        scenario_ids = [i.id for i in selected if isinstance(i, ScenarioWidget)]

        self.controller.copy_selected(card_ids, actor_ids, scenario_ids)
        total = len(card_ids) + len(actor_ids) + len(scenario_ids)
        if total:
            self.update_status(f"Скопировано: {total} элементов")

    def _on_paste(self):
        """Вставить из буфера"""
        self.controller.paste_clipboard()

    def _on_duplicate(self):
        """Дублировать выбранные карточки"""
        selected = [item for item in self.scene.selectedItems() if isinstance(item, UMLCard)]
        for card in selected:
            self.controller.duplicate_card(card.id)

    def _on_select_all(self):
        """Выделить все элементы"""
        for item in self.scene.items():
            item.setSelected(True)

    def _on_export_image(self):
        """Экспорт диаграммы в PNG или SVG"""
        filepath, selected_filter = QFileDialog.getSaveFileName(
            self, "Экспорт диаграммы", "",
            "PNG Image (*.png);;SVG Vector (*.svg)"
        )
        if not filepath:
            return

        if filepath.endswith(".svg"):
            self._export_svg(filepath)
        else:
            if not filepath.endswith(".png"):
                filepath += ".png"
            self._export_png(filepath)

    def _export_png(self, filepath: str):
        """Экспорт в PNG"""
        from PyQt6.QtGui import QImage, QPainter as QPainterImg
        from PyQt6.QtCore import QRectF

        rect = self.scene.itemsBoundingRect().adjusted(-20, -20, 20, 20)
        if rect.isEmpty():
            self.show_info("Диаграмма пуста.")
            return

        scale = 2  # Высокое разрешение
        img = QImage(int(rect.width() * scale), int(rect.height() * scale),
                     QImage.Format.Format_ARGB32)
        img.fill(0xFFF0EFFE)  # Фон

        painter = QPainterImg(img)
        painter.setRenderHint(QPainterImg.RenderHint.Antialiasing)
        self.scene.render(painter, source=rect)
        painter.end()

        if img.save(filepath):
            self.update_status(f"Экспортировано: {filepath}")
        else:
            self.show_error(f"Не удалось сохранить: {filepath}")

    def _export_svg(self, filepath: str):
        """Экспорт в SVG"""
        from PyQt6.QtSvg import QSvgGenerator
        from PyQt6.QtGui import QPainter as QPainterSvg
        from PyQt6.QtCore import QRectF, QSize

        rect = self.scene.itemsBoundingRect().adjusted(-20, -20, 20, 20)
        if rect.isEmpty():
            self.show_info("Диаграмма пуста.")
            return

        generator = QSvgGenerator()
        generator.setFileName(filepath)
        generator.setSize(QSize(int(rect.width()), int(rect.height())))
        generator.setViewBox(rect)
        generator.setTitle("LogicCraft UML Diagram")

        painter = QPainterSvg(generator)
        painter.setRenderHint(QPainterSvg.RenderHint.Antialiasing)
        self.scene.render(painter, source=rect)
        painter.end()

        self.update_status(f"Экспортировано: {filepath}")

    def _on_validate(self):
        """Валидация диаграммы"""
        warnings = self.controller.validate_diagram()
        dialog = ValidationResultsDialog(warnings, self)
        dialog.exec()

    def _get_selected_cards(self):
        return [i for i in self.scene.selectedItems() if isinstance(i, UMLCard)]

    def _align_left(self):
        cards = self._get_selected_cards()
        if len(cards) < 2: return
        min_x = min(c.pos().x() for c in cards)
        for c in cards:
            c.setPos(min_x, c.pos().y())
            self.controller.update_card(c.id, x=min_x, y=c.pos().y())

    def _align_right(self):
        cards = self._get_selected_cards()
        if len(cards) < 2: return
        max_x = max(c.pos().x() + c.rect().width() for c in cards)
        for c in cards:
            c.setPos(max_x - c.rect().width(), c.pos().y())
            self.controller.update_card(c.id, x=c.pos().x(), y=c.pos().y())

    def _align_top(self):
        cards = self._get_selected_cards()
        if len(cards) < 2: return
        min_y = min(c.pos().y() for c in cards)
        for c in cards:
            c.setPos(c.pos().x(), min_y)
            self.controller.update_card(c.id, x=c.pos().x(), y=min_y)

    def _align_bottom(self):
        cards = self._get_selected_cards()
        if len(cards) < 2: return
        max_y = max(c.pos().y() + c.rect().height() for c in cards)
        for c in cards:
            c.setPos(c.pos().x(), max_y - c.rect().height())
            self.controller.update_card(c.id, x=c.pos().x(), y=c.pos().y())

    def _align_center_h(self):
        cards = self._get_selected_cards()
        if len(cards) < 2: return
        avg_x = sum(c.pos().x() + c.rect().width() / 2 for c in cards) / len(cards)
        for c in cards:
            nx = avg_x - c.rect().width() / 2
            c.setPos(nx, c.pos().y())
            self.controller.update_card(c.id, x=nx, y=c.pos().y())

    def _align_center_v(self):
        cards = self._get_selected_cards()
        if len(cards) < 2: return
        avg_y = sum(c.pos().y() + c.rect().height() / 2 for c in cards) / len(cards)
        for c in cards:
            ny = avg_y - c.rect().height() / 2
            c.setPos(c.pos().x(), ny)
            self.controller.update_card(c.id, x=c.pos().x(), y=ny)

    def _on_save_clicked(self):
        """Обработка сохранения"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Diagram", "", "JSON Files (*.json)"
        )
        if filepath:
            self.save_requested.emit(filepath)

    def _on_load_clicked(self):
        """Обработка загрузки"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Load Diagram", "", "JSON Files (*.json)"
        )
        if filepath:
            self.load_requested.emit(filepath)

    def _on_clear_clicked(self):
        """Обработка очистки"""
        reply = QMessageBox.question(
            self, "Clear Diagram",
            "Are you sure you want to clear all classes and connections?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.clear_requested.emit()

    def _on_edit_selected(self):
        """Редактирование выбранной карточки"""
        selected_cards = [item for item in self.scene.selectedItems() if isinstance(item, UMLCard)]
        if selected_cards:
            card = selected_cards[0]
            dialog = EditClassDialog(card, self)
            if dialog.exec():
                name, attributes, methods, node_type = dialog.get_data()
                self.controller.edit_card(card.id, name, attributes, methods, node_type)
        else:
            self.show_info("Выберите карточку класса для редактирования.")

    def _on_delete_selected(self):
        """Удаление всех выбранных элементов (групповое)"""
        selected_items = self.scene.selectedItems()
        if not selected_items:
            self.show_info("Выберите элементы для удаления.")
            return

        from .widgets.actor_widget import ActorWidget
        from .widgets.scenario_widget import ScenarioWidget

        cards = [i for i in selected_items if isinstance(i, UMLCard)]
        conns = [i for i in selected_items if isinstance(i, ConnectionLine)]
        actors = [i for i in selected_items if isinstance(i, ActorWidget)]
        scenarios = [i for i in selected_items if isinstance(i, ScenarioWidget)]
        # UC-связи не выделяются напрямую, но удаляем их если выделены
        uc_conns = [i for i in selected_items if isinstance(i, ConnectionLine)
                    and i.id in self.uc_connection_map]

        count = len(cards) + len(conns) + len(actors) + len(scenarios)
        if count == 0:
            self.show_info("Выберите элементы для удаления.")
            return

        reply = QMessageBox.question(
            self, "Подтвердить удаление",
            f"Удалить {count} элемент(ов)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        for conn in conns:
            if conn.id in self.uc_connection_map:
                self.controller.remove_uc_connection(conn.id)
            else:
                self.controller.remove_connection(conn.id)
        for card in cards:
            self.controller.remove_card(card.id)
        for actor in actors:
            self.controller.remove_uc_actor(actor.id)
        for scenario in scenarios:
            self.controller.remove_uc_scenario(scenario.id)

    def _on_rename_selected(self):
        """Переименование выбранного элемента (Ctrl+M) - через диалог"""
        from PyQt6.QtWidgets import QInputDialog
        from .widgets.actor_widget import ActorWidget
        from .widgets.scenario_widget import ScenarioWidget

        selected = self.scene.selectedItems()
        if not selected:
            return

        item = selected[0]

        if isinstance(item, UMLCard):
            new_name, ok = QInputDialog.getText(self, "Переименовать", "Имя:", text=item.name)
            if ok and new_name.strip():
                self.controller.edit_card(item.id, new_name.strip(),
                                          item.attributes, item.methods)
        elif isinstance(item, ActorWidget):
            new_name, ok = QInputDialog.getText(self, "Переименовать актёра", "Имя:", text=item.name)
            if ok and new_name.strip():
                item.update_name(new_name.strip())
                self.controller.update_uc_actor(item.id, name=new_name.strip())
        elif isinstance(item, ScenarioWidget):
            new_name, ok = QInputDialog.getText(self, "Переименовать сценарий", "Имя:", text=item.name)
            if ok and new_name.strip():
                item.update_name(new_name.strip())
                self.controller.update_uc_scenario(item.id, name=new_name.strip())
    
    def _on_inline_rename(self):
        """Inline переименование выбранного элемента (F2)"""
        selected = self.scene.selectedItems()
        if not selected:
            return
        
        item = selected[0]
        
        # Пока поддерживаем только UMLCard
        if isinstance(item, UMLCard):
            item.start_inline_editing()
    
    def _show_search(self):
        """Показать виджет поиска классов (Ctrl+F)"""
        from .widgets.search_widget import SearchWidget
        
        if self._search_widget is None:
            self._search_widget = SearchWidget(self)
            self._search_widget.class_selected.connect(self._on_search_class_selected)
            self._search_widget.close_requested.connect(self._on_search_closed)
        
        # Обновляем список карточек
        cards = [card for card in self.card_map.values()]
        self._search_widget.set_cards(cards)
        
        # Позиционируем виджет в центре окна
        widget_width = self._search_widget.width()
        widget_height = self._search_widget.height()
        x = (self.width() - widget_width) // 2
        y = 100  # Отступ сверху
        self._search_widget.move(self.mapToGlobal(self.rect().topLeft()) + self.rect().topLeft() + self.pos() + self.geometry().topLeft())
        self._search_widget.move(x, y)
        
        self._search_widget.show()
        self._search_widget.raise_()
        self._search_widget.activateWindow()
    
    def _on_search_class_selected(self, card_id: str):
        """Обработка выбора класса из поиска"""
        if card_id in self.card_map:
            card = self.card_map[card_id]
            
            # Снимаем выделение со всех элементов
            self.scene.clearSelection()
            
            # Выделяем найденный класс
            card.setSelected(True)
            
            # Центрируем вид на карточке
            self.view.centerOn(card)
            
            # Подсвечиваем связанные классы
            self.scene.highlight_related_cards(card_id, self.card_map, self.connection_map)
            
            # Анимация: временно подсвечиваем карточку
            self._highlight_card_temporarily(card)
    
    def _on_search_closed(self):
        """Обработка закрытия виджета поиска"""
        if self._search_widget:
            self._search_widget.hide()
    
    def _highlight_card_temporarily(self, card):
        """Временная подсветка карточки"""
        # Можно добавить анимацию мигания или изменения цвета
        # Пока просто выделяем
        pass

    def _on_edit_connection(self):
        """Редактирование выбранной связи"""
        selected = [item for item in self.scene.items()
                    if isinstance(item, ConnectionLine) and item.is_selected()]
        if selected:
            connection = selected[0]
            dialog = ConnectionPropertiesDialog(connection, self)
            if dialog.exec():
                new_type = dialog.get_connection_type()
                multiplicity = dialog.get_multiplicity()
                name = dialog.get_name()
                self.controller.update_connection_properties(
                    connection.id,
                    new_type=new_type.value,
                    multiplicity=multiplicity,
                    name=name
                )
        else:
            self.show_info("Выберите связь для редактирования.")

    def _on_connection_ready(self, source_id, target_id, source_anchor, target_anchor):
        conn_type = getattr(self, '_default_connection_type', 'association')
        # Определяем, UC-связь или обычная
        uc_types = {"uc_association", "uc_include", "uc_extend"}
        all_uc_ids = set(self.uc_actor_map) | set(self.uc_scenario_map)
        if source_id in all_uc_ids or target_id in all_uc_ids or conn_type in uc_types:
            uc_type = conn_type if conn_type in uc_types else "uc_association"
            self.controller.add_uc_connection(source_id, target_id, uc_type,
                                              source_anchor, target_anchor)
        else:
            self.controller.add_connection(source_id, target_id, conn_type, source_anchor, target_anchor)

    def _on_card_moved(self, card_id, x, y):
        """Перемещение карточки - вызывается когда пользователь переместил карточку на сцене"""
        # Обновляем позицию карточки в модели
        self.controller.update_card(card_id, x=x, y=y)

    def _on_connection_updated(self, connection_id):
        connection = self.connection_map.get(connection_id)
        if connection:
            connection_model = self.controller.get_connection_model(connection_id)
            if connection_model:
                connection.set_connection_type(connection_model.type)
                connection.set_multiplicity(connection_model.multiplicity or "")
                connection.set_name(connection_model.name or "")

    def _on_card_added(self, node_model):
        pass  # handled in Application._on_add_card

    def _on_card_removed(self, card_id):
        self.remove_card_from_scene(card_id)

    def _on_diagram_cleared(self):
        self.clear_scene()

    # ── Use Case обработчики ───────────────────────────────────────────────────

    def _on_uc_actor_added(self, actor_model):
        """Добавить виджет актёра на сцену"""
        from .widgets.actor_widget import ActorWidget
        widget = ActorWidget(
            name=actor_model.name,
            x=actor_model.x,
            y=actor_model.y,
            actor_id=actor_model.id
        )
        widget.signals.move_finished.connect(
            lambda aid, x, y: self.controller.on_uc_actor_move_finished(aid, x, y)
        )
        widget.signals.delete_requested.connect(self.controller.remove_uc_actor)
        self.scene.addItem(widget)
        self.uc_actor_map[actor_model.id] = widget

    def _on_uc_actor_removed(self, actor_id: str):
        widget = self.uc_actor_map.pop(actor_id, None)
        if widget and widget.scene():
            self.scene.removeItem(widget)

    def _on_uc_scenario_added(self, scenario_model):
        """Добавить виджет сценария на сцену"""
        from .widgets.scenario_widget import ScenarioWidget
        widget = ScenarioWidget(
            name=scenario_model.name,
            x=scenario_model.x,
            y=scenario_model.y,
            scenario_id=scenario_model.id
        )
        widget.signals.move_finished.connect(
            lambda sid, x, y: self.controller.on_uc_scenario_move_finished(sid, x, y)
        )
        widget.signals.delete_requested.connect(self.controller.remove_uc_scenario)
        self.scene.addItem(widget)
        self.uc_scenario_map[scenario_model.id] = widget

    def _on_uc_scenario_removed(self, scenario_id: str):
        widget = self.uc_scenario_map.pop(scenario_id, None)
        if widget and widget.scene():
            self.scene.removeItem(widget)

    def _on_uc_connection_added(self, conn_model):
        """Добавить линию UC-связи на сцену"""
        from .widgets.connection_line import ConnectionLine
        from .widgets.arrow_head import ConnectionType as ArrowConnType

        # Ищем виджеты источника и цели среди всех UC-элементов
        all_uc = {**self.uc_actor_map, **self.uc_scenario_map}
        source_widget = all_uc.get(conn_model.source_id)
        target_widget = all_uc.get(conn_model.target_id)

        if not source_widget or not target_widget:
            return

        try:
            arrow_type = ArrowConnType(conn_model.type.value)
        except ValueError:
            arrow_type = ArrowConnType.UC_ASSOCIATION

        line = ConnectionLine(
            source=source_widget,
            target=target_widget,
            source_anchor=conn_model.source_anchor,
            target_anchor=conn_model.target_anchor,
            connection_type=arrow_type,
            connection_id=conn_model.id
        )
        self.scene.addItem(line)
        self.uc_connection_map[conn_model.id] = line
        line.signals.about_to_delete.connect(
            lambda c: self.controller.remove_uc_connection(c.id)
        )

    def _on_uc_connection_removed(self, conn_id: str):
        line = self.uc_connection_map.pop(conn_id, None)
        if line:
            if hasattr(line, 'arrow_head') and line.arrow_head and line.arrow_head.scene():
                self.scene.removeItem(line.arrow_head)
            if line.scene():
                self.scene.removeItem(line)

    def add_card_to_scene(self, card: UMLCard):
        """Добавить карточку на сцену"""
        self.scene.addItem(card)
        self.card_map[card.id] = card
        self.controller.register_card_view(card.id, card)

    def remove_card_from_scene(self, card_id: str):
        """Удалить карточку со сцены"""
        for item in self.scene.items():
            if isinstance(item, UMLCard) and item.id == card_id:
                self.scene.removeItem(item)
                if card_id in self.card_map:
                    del self.card_map[card_id]
                break

    def add_connection_to_scene(self, connection: ConnectionLine):
        if connection.id in self.connection_map:
            return
        self.scene.addItem(connection)
        self.connection_map[connection.id] = connection
        connection.signals.about_to_delete.connect(
            lambda c: self.remove_connection_from_scene(c.id)
        )

    def remove_connection_from_scene(self, connection_id: str):
        connection = self.connection_map.get(connection_id)
        if connection:
            if hasattr(connection, 'arrow_head') and connection.arrow_head:
                if connection.arrow_head.scene():
                    self.scene.removeItem(connection.arrow_head)
            if connection.scene():
                self.scene.removeItem(connection)
            del self.connection_map[connection_id]

    def clear_scene(self):
        """Очистить сцену"""
        self.scene.clear()
        self.card_map.clear()
        self.connection_map.clear()
        self.uc_actor_map.clear()
        self.uc_scenario_map.clear()
        self.uc_connection_map.clear()

    def update_status(self, text: str):
        """Обновить статус"""
        self.status_label.setText(text)
        # Обновляем статистику
        n_nodes = len(self.controller.manager.diagram.nodes)
        n_conns = len(self.controller.manager.diagram.connections)
        self.stats_label.setText(f"Классов: {n_nodes}  |  Связей: {n_conns}")

    def show_error(self, message: str):
        """Показать ошибку"""
        QMessageBox.critical(self, "Error", message)

    def show_info(self, message: str):
        """Показать информацию"""
        QMessageBox.information(self, "Information", message)
    
    def _on_history_changed(self):
        """Обработка изменений в истории undo/redo"""
        self.undo_action.setEnabled(self.controller.can_undo())
        self.redo_action.setEnabled(self.controller.can_redo())
    
    def _on_undo(self):
        """Отменить последнее действие"""
        self.controller.undo()
    
    def _on_redo(self):
        """Повторить отмененное действие"""
        self.controller.redo()

    def _on_generate_code_clicked(self):
        """Обработка генерации кода"""
        # Проверяем, есть ли классы в диаграмме
        if not self.controller.manager.diagram.nodes:
            QMessageBox.information(
                self, 
                "Информация", 
                "Диаграмма пуста. Добавьте классы для генерации кода."
            )
            return
        
        # Открываем диалог генерации кода
        dialog = CodeGenerationDialog(self.controller.manager.diagram, self)
        dialog.exec()

    def _on_export_project_clicked(self):
        """Обработка экспорта проекта"""
        dialog = ProjectExportDialog(self.controller.manager.diagram, self)
        dialog.exec()