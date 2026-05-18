"""Главная точка входа приложения"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication, QDialog

from logiccraft.controllers.diagram_controller import DiagramController
from logiccraft.view.main_window import MainWindow
from logiccraft.view.widgets.uml_card import UMLCard
from logiccraft.view.widgets.connection_line import ConnectionLine
from logiccraft.view.theme import apply_stylesheet
from logiccraft.view.dialogs.welcome_dialog import WelcomeDialog


class Application:
    """Главный класс приложения"""

    def __init__(self):
        self.app = QApplication(sys.argv)

        # Устанавливаем иконку приложения
        from PyQt6.QtGui import QIcon
        from pathlib import Path
        icon_path = Path(__file__).parent.parent.parent / "resources" / "icons" / "icon2.png"
        if icon_path.exists():
            self.app.setWindowIcon(QIcon(str(icon_path)))

        self.app.setStyle("Fusion")
        apply_stylesheet(self.app)

        self.controller = DiagramController()
        self.window = MainWindow(self.controller)
        self.project_config = None  # Конфигурация проекта
        self._connect_signals()

    def _connect_signals(self):
        self.window.add_card_requested.connect(self._on_add_card)
        self.window.save_requested.connect(self._on_save)
        self.window.load_requested.connect(self._on_load)
        self.window.clear_requested.connect(self._on_clear)
        self.window.edit_card_requested.connect(self._on_edit_card)
        self.window.delete_selected_requested.connect(self._on_delete_selected)
        self.window.edit_connection_requested.connect(self._on_edit_connection)

        self.controller.card_added.connect(self._on_card_added)
        self.controller.card_removed.connect(self._on_card_removed)
        self.controller.connection_added.connect(self._on_connection_added)
        self.controller.connection_removed.connect(self._on_connection_removed)
        self.controller.diagram_cleared.connect(self._on_diagram_cleared)
        self.controller.diagram_loaded.connect(self._on_diagram_loaded)
        self.controller.status_changed.connect(self.window.update_status)
        self.controller.error_occurred.connect(self.window.show_error)

    def _on_add_card(self, x: float, y: float, node_type: str = "class"):
        from logiccraft.models.diagram import NodeType
        try:
            nt = NodeType(node_type)
        except ValueError:
            nt = NodeType.CLASS
        self._creating_card = True  # флаг: карточка создаётся через UI
        node = self.controller.add_card(x, y, node_type=nt)
        self._creating_card = False
        if node:
            card = UMLCard(node.name, node.x, node.y,
                           attributes=[p.name for p in node.properties],
                           methods=[m.name for m in node.methods],
                           card_id=node.id,
                           node_type=node.node_type)
            card.signals.move_finished.connect(self._on_card_move_finished)
            card.signals.edit_requested.connect(self._on_card_edit_requested)
            card.signals.delete_requested.connect(self._on_card_delete_requested)
            self.controller.register_card_view(node.id, card)
            self.window.add_card_to_scene(card)

    def _on_card_added(self, node):
        """Создать карточку на сцене при добавлении через контроллер (дублирование, вставка)"""
        # Пропускаем если карточка создаётся через _on_add_card
        if getattr(self, '_creating_card', False):
            return
        card = UMLCard(node.name, node.x, node.y,
                       attributes=[p.name for p in node.properties],
                       methods=[m.name for m in node.methods],
                       card_id=node.id,
                       node_type=node.node_type)
        card.signals.move_finished.connect(self._on_card_move_finished)
        card.signals.edit_requested.connect(self._on_card_edit_requested)
        card.signals.delete_requested.connect(self._on_card_delete_requested)
        self.controller.register_card_view(node.id, card)
        self.window.add_card_to_scene(card)

    def _on_card_move_finished(self, card_id: str, x: float, y: float):
        """Сохраняем состояние после завершения перетаскивания"""
        self.controller.on_card_move_finished(card_id, x, y)

    def _on_card_edit_requested(self, card_id: str):
        """Обработка запроса на редактирование карточки из контекстного меню"""
        from logiccraft.view.dialogs.edit_class_dialog import EditClassDialog

        card = self.controller.card_map.get(card_id)
        if card:
            dialog = EditClassDialog(card, self.window)
            if dialog.exec():
                name, attributes, methods, node_type = dialog.get_data()
                self._on_edit_card(card_id, name, attributes, methods, node_type)

    def _on_card_delete_requested(self, card_id: str):
        """Обработка запроса на удаление карточки из контекстного меню"""
        self.controller.remove_card(card_id)

    def _on_card_removed(self, card_id):
        self.window.remove_card_from_scene(card_id)

    def _on_connection_added(self, connection):
        if connection.id in self.controller.connection_map:
            return
        source_card = self.controller.card_map.get(connection.source_id)
        target_card = self.controller.card_map.get(connection.target_id)
        if source_card and target_card:
            conn_line = ConnectionLine(
                source_card, target_card,
                connection.source_anchor,
                connection.target_anchor,
                connection.type,
                connection.id
            )
            self.controller.register_connection_view(connection.id, conn_line)
            self.window.add_connection_to_scene(conn_line)

    def _on_connection_removed(self, connection_id):
        self.window.remove_connection_from_scene(connection_id)

    def _on_save(self, filepath: str):
        self.controller.save_diagram(filepath)

    def _on_load(self, filepath: str):
        self.controller.load_diagram(filepath)

    def _on_clear(self):
        self.controller.clear_diagram()

    def _on_edit_card(self, card_id: str, name: str, attributes: list, methods: list, node_type=None):
        self.controller.edit_card(card_id, name, attributes, methods, node_type)
        card = self.controller.card_map.get(card_id)
        if card:
            card.name = name
            card.attributes = attributes
            card.methods = methods
            if node_type is not None:
                card.node_type = node_type
            card.update_content()

    def _on_delete_selected(self):
        for card_id, card in list(self.controller.card_map.items()):
            if card.isSelected():
                self.controller.remove_card(card_id)
        for conn_id, conn in list(self.controller.connection_map.items()):
            if conn.is_selected():
                self.controller.remove_connection(conn_id)

    def _on_edit_connection(self, connection_id: str, new_type: str):
        self.controller.update_connection_type(connection_id, new_type)
        connection = self.controller.connection_map.get(connection_id)
        if connection:
            connection.set_connection_type(new_type)
            connection.update_position()

    def _on_diagram_cleared(self):
        self.window.clear_scene()
        self.controller.card_map.clear()
        self.controller.connection_map.clear()
        self.window.uc_actor_map.clear()
        self.window.uc_scenario_map.clear()
        self.window.uc_connection_map.clear()

    def _on_diagram_loaded(self):
        self.window.clear_scene()
        self.controller.card_map.clear()
        self.controller.connection_map.clear()
        self.window.uc_actor_map.clear()
        self.window.uc_scenario_map.clear()
        self.window.uc_connection_map.clear()

        # Восстанавливаем обычные классы
        for node in self.controller.manager.diagram.nodes:
            card = UMLCard(node.name, node.x, node.y,
                           attributes=[p.name for p in node.properties],
                           methods=[m.name for m in node.methods],
                           card_id=node.id,
                           node_type=node.node_type)
            card.signals.move_finished.connect(self._on_card_move_finished)
            card.signals.edit_requested.connect(self._on_card_edit_requested)
            card.signals.delete_requested.connect(self._on_card_delete_requested)
            self.controller.register_card_view(node.id, card)
            self.window.add_card_to_scene(card)

        for conn in self.controller.manager.diagram.connections:
            source_card = self.controller.card_map.get(conn.source_id)
            target_card = self.controller.card_map.get(conn.target_id)
            if source_card and target_card:
                conn_line = ConnectionLine(
                    source_card, target_card,
                    conn.source_anchor,
                    conn.target_anchor,
                    conn.type,
                    conn.id,
                    multiplicity=conn.multiplicity or "",
                    name=conn.name or ""
                )
                self.controller.register_connection_view(conn.id, conn_line)
                self.window.add_connection_to_scene(conn_line)

        # Восстанавливаем UC-элементы
        for actor in self.controller.manager.diagram.uc_actors:
            self.controller.uc_actor_added.emit(actor)

        for scenario in self.controller.manager.diagram.uc_scenarios:
            self.controller.uc_scenario_added.emit(scenario)

        for uc_conn in self.controller.manager.diagram.uc_connections:
            self.controller.uc_connection_added.emit(uc_conn)

    def run(self):
        self._show_welcome_dialog()
        sys.exit(self.app.exec())

    def _show_welcome_dialog(self):
        """Показать стартовое окно"""
        self.welcome_dialog = WelcomeDialog()
        self.welcome_dialog.new_project_requested.connect(self._on_welcome_new_project)
        self.welcome_dialog.open_project_requested.connect(self._on_welcome_open_project)
        self.welcome_dialog.rejected.connect(self._on_welcome_rejected)

        # Показываем Welcome Dialog
        self.welcome_dialog.show()

    def _on_welcome_rejected(self):
        """Обработка закрытия Welcome Dialog крестиком"""
        sys.exit(0)

    def _on_welcome_new_project(self):
        """Обработка создания нового проекта"""
        # Получаем конфигурацию из Welcome Dialog (она уже показала NewProjectDialog)
        if hasattr(self.welcome_dialog, 'last_project_config'):
            self.project_config = self.welcome_dialog.last_project_config

            # Устанавливаем тип диаграммы
            diagram_type = self.project_config.get("diagram_type", "class")
            self.controller.manager.diagram.diagram_type = diagram_type

            # Обновляем заголовок окна с названием проекта
            project_name = self.project_config.get("name", "Untitled")
            self.window.setWindowTitle(f"LogicCraft — {project_name}")

            # Создаём структуру проекта и сохраняем конфигурацию
            self._create_project_structure()

            # Показываем главное окно
            self.window.show()

    def _create_project_structure(self):
        """Создать структуру проекта на диске"""
        if not self.project_config:
            return

        import json
        from pathlib import Path

        try:
            # Создаём папку проекта
            project_path = Path(self.project_config["path"]) / self.project_config["name"]
            project_path.mkdir(parents=True, exist_ok=True)

            # Создаём папку .logiccraft для метаданных
            logiccraft_dir = project_path / ".logiccraft"
            logiccraft_dir.mkdir(exist_ok=True)

            # Сохраняем конфигурацию проекта
            config_file = logiccraft_dir / "project.json"
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(self.project_config, f, indent=2, ensure_ascii=False)

            # Создаём пустой файл диаграммы сразу при создании проекта
            diagram_file = project_path / "diagram.json"
            empty_diagram = {
                "version": "1.0",
                "diagram_type": self.project_config.get("diagram_type", "class"),
                "nodes": [],
                "connections": [],
                "uc_actors": [],
                "uc_scenarios": [],
                "uc_connections": []
            }
            with open(diagram_file, "w", encoding="utf-8") as f:
                json.dump(empty_diagram, f, indent=2, ensure_ascii=False)

            # Создаём .gitignore если нужно
            if self.project_config.get("gitignore", False):
                gitignore_file = project_path / ".gitignore"
                gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# LogicCraft
.logiccraft/
"""
                with open(gitignore_file, "w", encoding="utf-8") as f:
                    f.write(gitignore_content)

            # Инициализируем Git репозиторий если нужно
            if self.project_config.get("git_init", False):
                import subprocess
                subprocess.run(["git", "init"], cwd=project_path, check=True)
                subprocess.run(["git", "add", "."], cwd=project_path, check=False)
                subprocess.run(
                    ["git", "commit", "-m", "Initial commit: LogicCraft project"],
                    cwd=project_path,
                    check=False
                )

            self.window.update_status(f"Проект создан: {project_path}")

        except Exception as e:
            self.window.show_error(f"Ошибка создания проекта: {e}")

    def _on_welcome_open_project(self):
        """Открыть проект из стартового окна"""
        from PyQt6.QtWidgets import QFileDialog
        filepath, _ = QFileDialog.getOpenFileName(
            self.welcome_dialog, "Открыть проект", "", "JSON Files (*.json)"
        )
        if filepath:
            self.controller.load_diagram(filepath)
            # Показываем главное окно только если файл выбран
            self.window.show()
        # Если отменили — ничего не делаем, Welcome остаётся открытым


def main():
    app = Application()
    app.run()


if __name__ == "__main__":
    main()

    def _save_project_config(self):
        """Сохранить конфигурацию проекта"""
        if not self.project_config:
            return
        
        import json
        from pathlib import Path
        
        project_path = Path(self.project_config["path"]) / self.project_config["name"]
        project_path.mkdir(parents=True, exist_ok=True)
        
        config_file = project_path / ".logiccraft" / "project.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(self.project_config, f, indent=2, ensure_ascii=False)
