"""Главное окно приложения"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QToolBar, QLabel, QFileDialog, QMessageBox, QGraphicsView,
    QMenu, QMenuBar, QDockWidget, QSizePolicy
)
from PyQt6.QtGui import QAction, QPainter, QKeySequence
from PyQt6.QtCore import pyqtSignal, Qt

from .scenes.diagram_scene import DiagramScene
from .widgets.uml_card import UMLCard
from .widgets.connection_line import ConnectionLine
from .dialogs.edit_class_dialog import EditClassDialog
from .dialogs.connection_properties import ConnectionPropertiesDialog
from .dialogs.code_generation_dialog import CodeGenerationDialog
from .dialogs.project_export_dialog import ProjectExportDialog
from .panels.toolbox_panel import ToolboxPanel
from .panels.properties_panel import PropertiesPanel


class DiagramView(QGraphicsView):
    """Вид для отображения сцены"""

    def __init__(self, scene: DiagramScene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.scale_factor = 1.15
        self.main_window = parent  # Ссылка на главное окно
    
    def keyPressEvent(self, event):
        """Обработка нажатий клавиш"""
        # Проверяем, есть ли обработчик в главном окне
        if self.main_window and hasattr(self.main_window, 'handle_key_press'):
            if self.main_window.handle_key_press(event):
                return  # Обработано в главном окне
        
        # Иначе используем стандартную обработку
        super().keyPressEvent(event)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                self.scale(self.scale_factor, self.scale_factor)
            else:
                self.scale(1 / self.scale_factor, 1 / self.scale_factor)
        else:
            super().wheelEvent(event)


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
        self.setWindowTitle("LogicCraft UML Architect")
        self.setGeometry(100, 100, 1400, 860)

        self._setup_ui()
        self._setup_menubar()
        self._setup_toolbar()
        self._setup_panels()
        self._connect_signals()
        self._connect_controller_signals()

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
        # Правая часть статусбара — статистика
        self.stats_label = QLabel("")
        self.stats_label.setObjectName("StatusBarStats")
        self.status_bar.addPermanentWidget(self.stats_label)
    
    def _setup_menubar(self):
        """Настройка меню"""
        menubar = self.menuBar()
        
        # Меню File
        file_menu = menubar.addMenu("&File")
        
        # Save
        save_action = QAction("💾 Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._on_save_clicked)
        file_menu.addAction(save_action)
        
        # Load
        load_action = QAction("📂 Load", self)
        load_action.setShortcut(QKeySequence.StandardKey.Open)
        load_action.triggered.connect(self._on_load_clicked)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        # Меню Edit с Undo/Redo
        edit_menu = menubar.addMenu("&Edit")
        
        # Undo
        self.undo_action = QAction("↩️ Undo", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.triggered.connect(self._on_undo)
        self.undo_action.setEnabled(False)
        edit_menu.addAction(self.undo_action)
        
        # Redo
        self.redo_action = QAction("↪️ Redo", self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.triggered.connect(self._on_redo)
        self.redo_action.setEnabled(False)
        edit_menu.addAction(self.redo_action)
        
        edit_menu.addSeparator()
        
        # Delete
        delete_action = QAction("🗑️ Delete Selected", self)
        delete_action.setShortcut(QKeySequence("Del"))
        delete_action.triggered.connect(self._on_delete_selected)
        edit_menu.addAction(delete_action)
        
        edit_menu.addSeparator()
        
        # Clear All
        clear_action = QAction("💥 Clear All", self)
        clear_action.triggered.connect(self._on_clear_clicked)
        edit_menu.addAction(clear_action)
        
        # Меню Tools
        tools_menu = menubar.addMenu("&Tools")
        
        # Code Generation
        generate_code_action = QAction("🚀 Generate Code", self)
        generate_code_action.setShortcut(QKeySequence("Ctrl+G"))
        generate_code_action.triggered.connect(self._on_generate_code_clicked)
        tools_menu.addAction(generate_code_action)

        # Export Project
        export_project_action = QAction("📦 Export Project...", self)
        export_project_action.setShortcut(QKeySequence("Ctrl+E"))
        export_project_action.triggered.connect(self._on_export_project_clicked)
        tools_menu.addAction(export_project_action)
        
        # Подключаем сигналы undo/redo от контроллера
        self.controller.history.history_changed.connect(self._on_history_changed)

    def _setup_toolbar(self):
        """Настройка тулбара"""
        toolbar = self.addToolBar("Main")
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #FFFFFF;
                border-bottom: 1px solid #E5E0F8;
                spacing: 4px;
                padding: 4px 12px;
            }
            QToolButton {
                background-color: transparent;
                color: #1F1F1F;
                border: none;
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 13px;
            }
            QToolButton:hover {
                background-color: #F3EEFF;
                color: #7C3AED;
            }
        """)

        # Левая часть — инструменты работы с диаграммой
        add_action = QAction("➕ Добавить класс", self)
        add_action.triggered.connect(self._on_add_clicked)
        toolbar.addAction(add_action)

        toolbar.addSeparator()

        edit_action = QAction("✏️ Редактировать", self)
        edit_action.triggered.connect(self._on_edit_selected)
        toolbar.addAction(edit_action)

        delete_action = QAction("🗑️ Удалить", self)
        delete_action.triggered.connect(self._on_delete_selected)
        toolbar.addAction(delete_action)

        edit_conn_action = QAction("🔗 Связи", self)
        edit_conn_action.triggered.connect(self._on_edit_connection)
        toolbar.addAction(edit_conn_action)

        toolbar.addSeparator()

        clear_action = QAction("💥 Очистить", self)
        clear_action.triggered.connect(self._on_clear_clicked)
        toolbar.addAction(clear_action)

        # Растягивающийся разделитель — пушит правые кнопки вправо
        from PyQt6.QtWidgets import QSizePolicy, QPushButton
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        spacer.setStyleSheet("background: transparent;")
        toolbar.addWidget(spacer)

        # Правые кнопки — в стиле дизайна
        save_btn = QPushButton("💾  Сохранить диаграмму")
        save_btn.setStyleSheet(self._primary_btn_style())
        save_btn.setFixedHeight(34)
        save_btn.clicked.connect(self._on_save_clicked)
        toolbar.addWidget(save_btn)

        load_btn = QPushButton("📂  Загрузить диаграмму")
        load_btn.setStyleSheet(self._outline_btn_style())
        load_btn.setFixedHeight(34)
        load_btn.clicked.connect(self._on_load_clicked)
        toolbar.addWidget(load_btn)

        gen_btn = QPushButton("⚡  Сгенерировать код")
        gen_btn.setStyleSheet(self._primary_btn_style())
        gen_btn.setFixedHeight(34)
        gen_btn.clicked.connect(self._on_generate_code_clicked)
        toolbar.addWidget(gen_btn)

    def _primary_btn_style(self) -> str:
        return """
            QPushButton {
                background-color: #7C3AED;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 7px 18px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #6D28D9; }
            QPushButton:pressed { background-color: #5B21B6; }
        """

    def _outline_btn_style(self) -> str:
        return """
            QPushButton {
                background-color: transparent;
                color: #7C3AED;
                border: 1.5px solid #7C3AED;
                border-radius: 20px;
                padding: 7px 18px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #F3EEFF; }
            QPushButton:pressed { background-color: #EDE9FE; }
        """

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

        # Подключаем сигналы Properties
        self.properties_panel.name_changed.connect(self._on_properties_name_changed)
        self.properties_panel.type_changed.connect(self._on_properties_type_changed)
        self.properties_panel.attributes_changed.connect(self._on_properties_attrs_changed)
        self.properties_panel.methods_changed.connect(self._on_properties_methods_changed)
        self.properties_panel.delete_requested.connect(self._on_properties_delete)

        # Слушаем изменение выделения на сцене
        self.scene.selectionChanged.connect(self._on_scene_selection_changed)

    def _on_toolbox_add_element(self, node_type: str):
        """Добавить элемент из тулбокса в центр холста"""
        center = self.view.mapToScene(self.view.viewport().rect().center())
        import random
        offset_x = random.randint(-60, 60)
        offset_y = random.randint(-60, 60)
        self.add_card_requested.emit(center.x() + offset_x, center.y() + offset_y, node_type)

    def _on_scene_selection_changed(self):
        """Обновить панель свойств при изменении выделения"""
        selected = [item for item in self.scene.selectedItems()
                    if isinstance(item, UMLCard)]
        if selected:
            card = selected[0]
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
        else:
            self.properties_panel.show_empty()

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

    def _connect_signals(self):
        """Подключение сигналов сцены"""
        self.scene.connection_ready.connect(self._on_connection_ready)
        self.scene.card_moved.connect(self._on_card_moved)

    def _connect_controller_signals(self):
        """Подключение сигналов контроллера"""
        self.controller.connection_updated.connect(self._on_connection_updated)
        self.controller.card_added.connect(self._on_card_added)
        self.controller.card_removed.connect(self._on_card_removed)
        self.controller.diagram_cleared.connect(self._on_diagram_cleared)
        self.controller.status_changed.connect(self.update_status)
        self.controller.error_occurred.connect(self.show_error)

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
        return False
    
    def keyPressEvent(self, event):
        """Обработка нажатий клавиш (для MainWindow)"""
        if not self.handle_key_press(event):
            super().keyPressEvent(event)
    
    def _on_add_clicked(self):
        """Обработка добавления карточки — обычный класс"""
        center = self.view.mapToScene(self.view.viewport().rect().center())
        self.add_card_requested.emit(center.x(), center.y(), "class")

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
        """Удаление выбранных элементов"""
        selected_items = self.scene.selectedItems()
        if not selected_items:
            self.show_info("Please select items to delete.")
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete {len(selected_items)} selected item(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            for item in selected_items:
                if isinstance(item, UMLCard):
                    self.controller.remove_card(item.id)
                elif isinstance(item, ConnectionLine):
                    self.controller.remove_connection(item.id)

    def _on_edit_connection(self):
        """Редактирование выбранной связи"""
        selected = [item for item in self.scene.items()
                    if isinstance(item, ConnectionLine) and item.is_selected()]
        if selected:
            connection = selected[0]
            dialog = ConnectionPropertiesDialog(connection, self)
            if dialog.exec():
                new_type = dialog.get_connection_type()
                self.edit_connection_requested.emit(connection.id, new_type.value)

    def _on_connection_ready(self, source_id, target_id, source_anchor, target_anchor):
        self.controller.add_connection(source_id, target_id, "association", source_anchor, target_anchor)

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

    def _on_card_added(self, node_model):
        pass  # handled in Application._on_add_card

    def _on_card_removed(self, card_id):
        self.remove_card_from_scene(card_id)

    def _on_diagram_cleared(self):
        self.clear_scene()

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
        self.connection_map.clear()  # ← добавить

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