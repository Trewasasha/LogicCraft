"""Главная точка входа приложения"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication

from logiccraft.controllers.diagram_controller import DiagramController
from logiccraft.view.main_window import MainWindow
from logiccraft.view.widgets.uml_card import UMLCard
from logiccraft.view.widgets.connection_line import ConnectionLine
from logiccraft.view.theme import apply_stylesheet


class Application:
    """Главный класс приложения"""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")
        apply_stylesheet(self.app)

        self.controller = DiagramController()
        self.window = MainWindow(self.controller)
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

    def _on_add_card(self, x: float, y: float):
        node = self.controller.add_card(x, y)
        if node:
            card = UMLCard(node.name, node.x, node.y,
                           attributes=[p.name for p in node.properties],
                           methods=[m.name for m in node.methods],
                           card_id=node.id)
            self.controller.register_card_view(node.id, card)
            self.window.add_card_to_scene(card)

    def _on_card_added(self, node):
        pass  # handled in _on_add_card

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

    def _on_edit_card(self, card_id: str, name: str, attributes: list, methods: list):
        self.controller.update_card(card_id, name, attributes=attributes, methods=methods)
        card = self.controller.card_map.get(card_id)
        if card:
            card.name = name
            card.attributes = attributes
            card.methods = methods
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

    def _on_diagram_loaded(self):
        self.window.clear_scene()
        self.controller.card_map.clear()
        self.controller.connection_map.clear()

        for node in self.controller.manager.diagram.nodes:
            card = UMLCard(node.name, node.x, node.y,
                           attributes=[p.name for p in node.properties],
                           methods=[m.name for m in node.methods],
                           card_id=node.id)
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
                    conn.id
                )
                self.controller.register_connection_view(conn.id, conn_line)
                self.window.add_connection_to_scene(conn_line)

    def run(self):
        self.window.show()
        sys.exit(self.app.exec())


def main():
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
