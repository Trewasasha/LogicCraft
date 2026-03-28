"""Главное окно приложения"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QToolBar, QLabel, QFileDialog, QMessageBox, QGraphicsView
)
from PyQt6.QtGui import QAction, QPainter
from PyQt6.QtCore import pyqtSignal, Qt

from .scenes.diagram_scene import DiagramScene
from .widgets.uml_card import UMLCard
from .widgets.connection_line import ConnectionLine
from .dialogs.edit_class_dialog import EditClassDialog
from .dialogs.connection_properties import ConnectionPropertiesDialog


class DiagramView(QGraphicsView):
    """Вид для отображения сцены"""

    def __init__(self, scene: DiagramScene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.scale_factor = 1.15

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
    add_card_requested = pyqtSignal(float, float)
    save_requested = pyqtSignal(str)
    load_requested = pyqtSignal(str)
    clear_requested = pyqtSignal()
    edit_card_requested = pyqtSignal(str, str, list, list)
    delete_selected_requested = pyqtSignal()
    edit_connection_requested = pyqtSignal(str, str)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.card_map = {}  # card_id -> UMLCard
        self.connection_map = {}  # connection_id -> ConnectionLine  # ← добавить
        self.setWindowTitle("LogicCraft UML Architect")
        self.setGeometry(100, 100, 1200, 800)

        self._setup_ui()
        self._setup_toolbar()
        self._connect_signals()
        self._connect_controller_signals()

    def _setup_ui(self):
        """Настройка UI компонентов"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)

        self.scene = DiagramScene()
        self.view = DiagramView(self.scene)
        layout.addWidget(self.view)

        # Панель статуса
        self.status_bar = self.statusBar()
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

    def _setup_toolbar(self):
        """Настройка тулбара"""
        toolbar = self.addToolBar("Main")
        toolbar.setMovable(False)

        # Кнопки
        add_action = QAction("➕ Add Class", self)
        add_action.triggered.connect(self._on_add_clicked)
        toolbar.addAction(add_action)

        save_action = QAction("💾 Save", self)
        save_action.triggered.connect(self._on_save_clicked)
        toolbar.addAction(save_action)

        load_action = QAction("📂 Load", self)
        load_action.triggered.connect(self._on_load_clicked)
        toolbar.addAction(load_action)

        clear_action = QAction("🗑️ Clear All", self)
        clear_action.triggered.connect(self._on_clear_clicked)
        toolbar.addAction(clear_action)

        toolbar.addSeparator()

        edit_action = QAction("✏️ Edit Selected", self)
        edit_action.triggered.connect(self._on_edit_selected)
        toolbar.addAction(edit_action)

        delete_action = QAction("❌ Delete Selected", self)
        delete_action.triggered.connect(self._on_delete_selected)
        toolbar.addAction(delete_action)

        edit_conn_action = QAction("🔗 Edit Connection", self)
        edit_conn_action.triggered.connect(self._on_edit_connection)
        toolbar.addAction(edit_conn_action)

    def _connect_signals(self):
        """Подключение сигналов сцены"""
        self.scene.connection_ready.connect(self._on_connection_ready)
        self.scene.card_moved.connect(self._on_card_moved)

    def _connect_controller_signals(self):
        """Подключение сигналов контроллера"""
        self.controller.connection_added.connect(self._on_connection_added)
        self.controller.connection_updated.connect(self._on_connection_updated)  # ← добавить
        self.controller.card_added.connect(self._on_card_added)
        self.controller.card_removed.connect(self._on_card_removed)
        self.controller.diagram_cleared.connect(self._on_diagram_cleared)
        self.controller.status_changed.connect(self.update_status)
        self.controller.error_occurred.connect(self.show_error)

    def _on_add_clicked(self):
        """Обработка добавления карточки"""
        # Центрируем новую карточку в поле зрения
        center = self.view.mapToScene(self.view.viewport().rect().center())
        self.add_card_requested.emit(center.x(), center.y())

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
        # Используем встроенный метод сцены для получения всех выделенных объектов
        selected_items = self.scene.selectedItems()

        # Фильтруем только карточки (UMLCard)
        selected_cards = [item for item in selected_items if isinstance(item, UMLCard)]

        if selected_cards:
            card = selected_cards[0]
            print(f"DEBUG: Editing card {card.id}") # Добавь лог для проверки
            dialog = EditClassDialog(card, self)
            if dialog.exec():
                name, attributes, methods = dialog.get_data()
                # Эмиттим сигнал контроллеру для обновления данных в модели
                self.edit_card_requested.emit(card.id, name, attributes, methods)
        else:
            self.show_info("Please select a class card to edit.")

    def _on_delete_selected(self):
        """Удаление выбранных элементов (карточек или связей)"""
        # Получаем все выделенные объекты на сцене
        selected_items = self.scene.selectedItems()

        if not selected_items:
            return

        # Спрашиваем подтверждение
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete {len(selected_items)} selected item(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            for item in selected_items:
                # Если это карточка
                if isinstance(item, UMLCard):
                    print(f"DEBUG: Requesting card removal: {item.id}")
                    self.controller.remove_card(item.id)

                # Если это связь (ConnectionLine)
                elif isinstance(item, ConnectionLine):
                    print(f"DEBUG: Requesting connection removal: {item.id}")
                    # Вызываем метод напрямую у контроллера
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
        """Создание связи - вызывается когда пользователь завершил создание связи на сцене"""
        print(f"DEBUG: MainWindow._on_connection_ready - {source_id} -> {target_id}")
        print(f"DEBUG: Calling controller.add_connection with source={source_id}, target={target_id}, anchors={source_anchor}->{target_anchor}")
        # Вызываем контроллер для создания связи в модели
        result = self.controller.add_connection(
            source_id, target_id, "association",  # по умолчанию ассоциация
            source_anchor, target_anchor
        )
        print(f"DEBUG: controller.add_connection returned: {result}")

    def _on_card_moved(self, card_id, x, y):
        """Перемещение карточки - вызывается когда пользователь переместил карточку на сцене"""
        # Обновляем позицию карточки в модели
        self.controller.update_card(card_id, x=x, y=y)

    def _on_connection_added(self, connection_model):
        """Обработка добавления связи в модель - создаем визуальное представление"""
        print(f"DEBUG: Connection added to model: {connection_model.id}")

        # Находим карточки по ID
        source_card = self.card_map.get(connection_model.source_id)
        target_card = self.card_map.get(connection_model.target_id)

        if source_card and target_card:
            # Создаем визуальное представление связи
            connection = ConnectionLine(
                source_card, target_card,
                connection_model.source_anchor,
                connection_model.target_anchor,
                connection_model.type,
                connection_model.id
            )
            self.scene.addItem(connection)
            self.connection_map[connection_model.id] = connection  # ← добавить
            print(f"DEBUG: Connection view created and added to scene")
        else:
            print(f"DEBUG: Could not find cards for connection: source={source_card}, target={target_card}")

    def _on_connection_updated(self, connection_id):
        """Обработка обновления связи в модели"""
        print(f"DEBUG: Connection updated: {connection_id}")

        # Находим визуальное представление связи
        connection = self.connection_map.get(connection_id)
        if connection:
            # Получаем обновленную модель связи
            connection_model = self.controller.get_connection_model(connection_id)
            if connection_model:
                # Обновляем тип связи в визуальном представлении
                connection.set_connection_type(connection_model.type)
                print(f"DEBUG: Connection visual updated to {connection_model.type}")
        else:
            print(f"DEBUG: Connection view not found for {connection_id}")

    def _on_card_added(self, node_model):
        """Обработка добавления карточки в модель"""
        print(f"DEBUG: Card added to model: {node_model.id}")
        # Карточка уже должна быть создана и добавлена на сцену в другом месте
        pass

    def _on_card_removed(self, card_id):
        """Обработка удаления карточки из модели"""
        print(f"DEBUG: Card removed from model: {card_id}")
        self.remove_card_from_scene(card_id)

    def _on_diagram_cleared(self):
        """Обработка очистки диаграммы"""
        print(f"DEBUG: Diagram cleared")
        self.clear_scene()
        self.card_map.clear()
        self.connection_map.clear()  # ← добавить

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
        """Добавить связь на сцену"""
        # Проверка на дубликаты по ID
        if connection.id in self.connection_map:
            print(f"DEBUG: Connection {connection.id} already on scene, skipping.")
            return

        self.scene.addItem(connection)
        self.connection_map[connection.id] = connection

        # Подключаем сигнал удаления, чтобы при удалении карточки
        # связь корректно исчезала из нашего словаря
        connection.signals.about_to_delete.connect(
            lambda c: self.remove_connection_from_scene(c.id)
        )

    def remove_connection_from_scene(self, connection_id: str):
        """Удалить связь со сцены полностью"""
        print(f"DEBUG: Attempting to remove connection {connection_id}")

        connection = self.connection_map.get(connection_id)
        if connection:
            # Явно удаляем наконечник (защита для Mac)
            if hasattr(connection, 'arrow_head') and connection.arrow_head:
                if connection.arrow_head.scene():
                    self.scene.removeItem(connection.arrow_head)

            # Удаляем саму линию
            if connection.scene():
                self.scene.removeItem(connection)

            # Убираем из словаря
            del self.connection_map[connection_id]
            print(f"DEBUG: Connection {connection_id} successfully removed from scene")
        else:
            print(f"DEBUG: Connection {connection_id} not found in connection_map")

    def clear_scene(self):
        """Очистить сцену"""
        self.scene.clear()
        self.card_map.clear()
        self.connection_map.clear()  # ← добавить

    def update_status(self, text: str):
        """Обновить статус"""
        self.status_label.setText(text)

    def show_error(self, message: str):
        """Показать ошибку"""
        QMessageBox.critical(self, "Error", message)

    def show_info(self, message: str):
        """Показать информацию"""
        QMessageBox.information(self, "Information", message)