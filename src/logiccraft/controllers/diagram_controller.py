"""Главный контроллер диаграммы"""
from PyQt6.QtCore import QObject, pyqtSignal
from typing import List, Dict, Optional, Any
from pathlib import Path

from ..models.diagram import UMLDiagram, UMLNode, UMLConnection, UMLProperty, UMLMethod
from ..models.diagram_manager import DiagramManager
from ..models.engine import DiagramEngine
from ..services.serialization_service import SerializationService
from ..services.code_generator import CodeGenerator
from ..view.widgets.uml_card import UMLCard
from ..view.widgets.connection_line import ConnectionLine


class DiagramController(QObject):
    """Главный контроллер, связывающий модель и представление"""

    # Сигналы для представления
    card_added = pyqtSignal(object)  # UMLCard
    card_removed = pyqtSignal(str)   # card_id
    card_updated = pyqtSignal(object)  # UMLCard
    connection_added = pyqtSignal(object)  # ConnectionLine
    connection_removed = pyqtSignal(str)  # connection_id
    connection_updated = pyqtSignal(object)  # ConnectionLine
    diagram_cleared = pyqtSignal()
    diagram_loaded = pyqtSignal()
    diagram_saved = pyqtSignal(str)

    # Сигналы для статуса
    status_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.manager = DiagramManager()
        self.engine = DiagramEngine()
        self.serializer = SerializationService()
        self.code_generator = CodeGenerator()

        # Словари для связи моделей и представлений
        self.card_map: Dict[str, UMLCard] = {}  # node_id -> UMLCard
        self.connection_map: Dict[str, ConnectionLine] = {}  # connection_id -> ConnectionLine

    def add_card(self, x: float, y: float, name: str = None) -> Optional[UMLNode]:
        """Добавить карточку"""
        try:
            node = self.manager.add_node(x, y, name)
            self.status_changed.emit(f"Added class: {node.name}")
            self.card_added.emit(node)
            return node
        except Exception as e:
            self.error_occurred.emit(f"Failed to add card: {e}")
            return None

    def remove_card(self, card_id: str) -> bool:
        """Удалить карточку"""
        try:
            # Удаляем все связи, связанные с этой карточкой
            connections = self.manager.get_connections_for_node(card_id)
            for conn in connections:
                self.remove_connection(conn.id)

            # Удаляем карточку из модели
            if self.manager.remove_node(card_id):
                self.status_changed.emit(f"Removed class")
                self.card_removed.emit(card_id)
                return True

            return False
        except Exception as e:
            self.error_occurred.emit(f"Failed to remove card: {e}")
            return False

    def update_card(self, card_id: str, name: str = None,
                    x: float = None, y: float = None,
                    attributes: List[str] = None,
                    methods: List[str] = None) -> bool:
        """Обновить карточку"""
        try:
            # Преобразуем строки атрибутов в UMLProperty
            properties = []
            if attributes:
                for attr in attributes:
                    # Парсим строку вида "+name: str" или "name: str"
                    visibility = "public"
                    attr_str = attr.strip()
                    if attr_str.startswith("+"):
                        visibility = "public"
                        attr_str = attr_str[1:]
                    elif attr_str.startswith("-"):
                        visibility = "private"
                        attr_str = attr_str[1:]
                    elif attr_str.startswith("#"):
                        visibility = "protected"
                        attr_str = attr_str[1:]

                    if ":" in attr_str:
                        name, type_str = attr_str.split(":", 1)
                        name = name.strip()
                        type_str = type_str.strip()
                    else:
                        name = attr_str
                        type_str = "Any"

                    properties.append({
                        "name": name,
                        "type": type_str,
                        "visibility": visibility
                    })

            # Преобразуем строки методов в UMLMethod
            method_objects = []
            if methods:
                for method in methods:
                    # Парсим строку вида "+getName(): str"
                    visibility = "public"
                    method_str = method.strip()
                    if method_str.startswith("+"):
                        visibility = "public"
                        method_str = method_str[1:]
                    elif method_str.startswith("-"):
                        visibility = "private"
                        method_str = method_str[1:]
                    elif method_str.startswith("#"):
                        visibility = "protected"
                        method_str = method_str[1:]

                    if "(" in method_str and ")" in method_str:
                        name_part = method_str[:method_str.index("(")]
                        return_part = method_str[method_str.index(")")+1:]
                        if return_part.startswith(":"):
                            return_type = return_part[1:].strip()
                        else:
                            return_type = "void"

                        method_objects.append({
                            "name": name_part.strip(),
                            "return_type": return_type,
                            "visibility": visibility
                        })
                    else:
                        method_objects.append({
                            "name": method_str,
                            "return_type": "void",
                            "visibility": visibility
                        })

            return self.manager.update_node(
                card_id, name, x, y, properties, method_objects
            )
        except Exception as e:
            self.error_occurred.emit(f"Failed to update card: {e}")
            return False


    def add_connection(self, source_id: str, target_id: str,
                       connection_type: str,
                       source_anchor: str = "right",
                       target_anchor: str = "left") -> Optional[UMLConnection]:

        print(f"DEBUG: DiagramController.add_connection called with source={source_id}, target={target_id}, type={connection_type}")
        try:
            connection = self.manager.add_connection(
                source_id, target_id, connection_type,
                source_anchor, target_anchor
            )
            print(f"DEBUG: Connection created: {connection}")
            self.status_changed.emit(f"Added connection: {connection_type}")
            self.connection_added.emit(connection)
            print(f"DEBUG: connection_added signal emitted")
            return connection
        except Exception as e:
            print(f"DEBUG: Error in add_connection: {e}")
            self.error_occurred.emit(f"Failed to add connection: {e}")
            return None

    def remove_connection(self, connection_id: str) -> bool:
        """Удалить связь"""
        try:
            if self.manager.remove_connection(connection_id):
                self.status_changed.emit("Removed connection")
                self.connection_removed.emit(connection_id)
                return True
            return False
        except Exception as e:
            self.error_occurred.emit(f"Failed to remove connection: {e}")
            return False

    def update_connection_type(self, connection_id: str, new_type: str) -> bool:
        """Обновить тип связи"""
        try:
            if self.manager.update_connection_type(connection_id, new_type):
                self.status_changed.emit(f"Updated connection type to {new_type}")
                self.connection_updated.emit(connection_id)
                return True
            return False
        except Exception as e:
            self.error_occurred.emit(f"Failed to update connection: {e}")
            return False

    def save_diagram(self, filepath: str) -> bool:
        """Сохранить диаграмму"""
        try:
            if self.manager.save_to_file(filepath):
                self.status_changed.emit(f"Diagram saved to {filepath}")
                self.diagram_saved.emit(filepath)
                return True
            return False
        except Exception as e:
            self.error_occurred.emit(f"Failed to save diagram: {e}")
            return False

    def load_diagram(self, filepath: str) -> bool:
        """Загрузить диаграмму"""
        try:
            if self.manager.load_from_file(filepath):
                self.status_changed.emit(f"Diagram loaded from {filepath}")
                self.diagram_loaded.emit()
                return True
            return False
        except Exception as e:
            self.error_occurred.emit(f"Failed to load diagram: {e}")
            return False

    def clear_diagram(self):
        """Очистить диаграмму"""
        try:
            self.manager.clear()
            self.status_changed.emit("Diagram cleared")
            self.diagram_cleared.emit()
        except Exception as e:
            self.error_occurred.emit(f"Failed to clear diagram: {e}")

    def generate_code(self, language: str = "python") -> str:
        """Сгенерировать код из диаграммы"""
        try:
            code = self.code_generator.generate(self.manager.diagram, language)
            self.status_changed.emit(f"Generated {language} code")
            return code
        except Exception as e:
            self.error_occurred.emit(f"Failed to generate code: {e}")
            return ""

    def validate_diagram(self) -> List:
        """Валидировать диаграмму"""
        self.engine.load_diagram(self.manager.diagram)
        errors = self.engine.validate()

        if errors:
            for error in errors:
                self.error_occurred.emit(f"Validation {error.severity}: {error.message}")
        else:
            self.status_changed.emit("Diagram is valid")

        return errors

    def get_statistics(self) -> Dict[str, int]:
        """Получить статистику диаграммы"""
        return self.manager.get_statistics()

    def register_card_view(self, node_id: str, card: UMLCard):
        """Зарегистрировать представление карточки"""
        self.card_map[node_id] = card

    def register_connection_view(self, connection_id: str, connection: ConnectionLine):
        """Зарегистрировать представление связи"""
        self.connection_map[connection_id] = connection

    def get_node_model(self, node_id: str) -> Optional[UMLNode]:
        """Получить модель узла по ID"""
        return self.manager.get_node_by_id(node_id)

    def get_connection_model(self, connection_id: str) -> Optional[UMLConnection]:
        """Получить модель связи по ID"""
        return self.manager.get_connection_by_id(connection_id)