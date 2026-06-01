from typing import List, Dict, Optional, Tuple
from pathlib import Path
import json
import logging
from .diagram import (
    UMLDiagram, UMLNode, UMLConnection, ConnectionType, UMLProperty, UMLMethod, NodeType,
    UseCaseActor, UseCaseScenario, UseCaseConnection
)

logger = logging.getLogger(__name__)


class DiagramManager:
    """Управляет состоянием диаграммы и бизнес-логикой"""

    def __init__(self):
        self.diagram = UMLDiagram(
            name="Untitled",
            nodes=[],
            connections=[]
        )

    def add_node(self, x: float, y: float, name: str = None, node_type: NodeType = NodeType.CLASS) -> UMLNode:
        """Добавить узел"""
        if name is None:
            if node_type == NodeType.INTERFACE:
                name = f"IInterface{len([n for n in self.diagram.nodes if n.node_type == NodeType.INTERFACE]) + 1}"
            elif node_type == NodeType.ENUM:
                name = f"Enum{len([n for n in self.diagram.nodes if n.node_type == NodeType.ENUM]) + 1}"
            else:
                name = f"Class{len(self.diagram.nodes) + 1}"

        node = UMLNode(
            name=name,
            x=x,
            y=y,
            properties=[],
            methods=[],
            node_type=node_type
        )
        self.diagram.nodes.append(node)
        return node

    def remove_node(self, node_id: str) -> bool:
        """Удалить узел"""
        for i, node in enumerate(self.diagram.nodes):
            if node.id == node_id:
                self.diagram.nodes.pop(i)
                return True
        return False

    def update_node(self, node_id: str, name: str = None,
                    x: float = None, y: float = None,
                    properties: List[Dict] = None,
                    methods: List[Dict] = None,
                    node_type: NodeType = None,
                    enum_literals: List[Dict] = None) -> bool:
        """Обновить узел"""
        node = self.get_node_by_id(node_id)
        if not node:
            return False

        if name is not None:
            node.name = name
        if x is not None:
            node.x = x
        if y is not None:
            node.y = y
        if properties is not None:
            node.properties = [UMLProperty(**p) for p in properties]
        if methods is not None:
            node.methods = [UMLMethod(**m) for m in methods]
        if node_type is not None:
            node.node_type = node_type
        if enum_literals is not None:
            from .diagram import UMLEnumLiteral
            node.enum_literals = [UMLEnumLiteral(**el) for el in enum_literals]

        return True

    def add_connection(self, source_id: str, target_id: str,
                       connection_type: str, source_anchor: str = "right",
                       target_anchor: str = "left") -> UMLConnection:
        """Добавить связь"""
        connection = UMLConnection(
            source_id=source_id,
            target_id=target_id,
            type=ConnectionType(connection_type),
            source_anchor=source_anchor,
            target_anchor=target_anchor
        )
        self.diagram.connections.append(connection)
        return connection

    def remove_connection(self, connection_id: str) -> bool:
        """Удалить связь"""
        for i, conn in enumerate(self.diagram.connections):
            if conn.id == connection_id:
                self.diagram.connections.pop(i)
                return True
        return False

    def update_connection_type(self, connection_id: str, new_type: str) -> bool:
        """Обновить тип связи"""
        connection = self.get_connection_by_id(connection_id)
        if connection:
            connection.type = ConnectionType(new_type)
            return True
        return False

    def get_node_by_id(self, node_id: str) -> Optional[UMLNode]:
        """Получить узел по ID"""
        for node in self.diagram.nodes:
            if node.id == node_id:
                return node
        return None

    def get_connection_by_id(self, connection_id: str) -> Optional[UMLConnection]:
        """Получить связь по ID"""
        for conn in self.diagram.connections:
            if conn.id == connection_id:
                return conn
        return None

    def get_connections_for_node(self, node_id: str) -> List[UMLConnection]:
        """Получить все связи для узла"""
        return [conn for conn in self.diagram.connections
                if conn.source_id == node_id or conn.target_id == node_id]

    def save_to_file(self, filepath: str) -> bool:
        """Сохранить диаграмму в файл"""
        try:
            data = {
                "version": "1.0",
                "name": self.diagram.name,
                "diagram_type": self.diagram.diagram_type.value if hasattr(self.diagram, 'diagram_type') and self.diagram.diagram_type else "class",
                "nodes": [node.model_dump() for node in self.diagram.nodes],
                "connections": [conn.model_dump() for conn in self.diagram.connections],
                "uc_actors": [actor.model_dump() for actor in self.diagram.uc_actors],
                "uc_scenarios": [scenario.model_dump() for scenario in self.diagram.uc_scenarios],
                "uc_connections": [conn.model_dump() for conn in self.diagram.uc_connections],
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving diagram: {e}")
            return False

    def load_from_file(self, filepath: str) -> bool:
        """Загрузить диаграмму из файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            nodes = [UMLNode(**node_data) for node_data in data.get("nodes", [])]
            connections = [UMLConnection(**conn_data) for conn_data in data.get("connections", [])]
            uc_actors = [UseCaseActor(**a) for a in data.get("uc_actors", [])]
            uc_scenarios = [UseCaseScenario(**s) for s in data.get("uc_scenarios", [])]
            uc_connections = [UseCaseConnection(**c) for c in data.get("uc_connections", [])]

            from .diagram import DiagramType
            diagram_type = DiagramType(data.get("diagram_type", "class"))

            self.diagram = UMLDiagram(
                name=data.get("name", "Untitled"),
                diagram_type=diagram_type,
                nodes=nodes,
                connections=connections,
                uc_actors=uc_actors,
                uc_scenarios=uc_scenarios,
                uc_connections=uc_connections,
            )
            return True
        except Exception as e:
            logger.error(f"Error loading diagram: {e}")
            return False

    def clear(self):
        """Очистить диаграмму"""
        self.diagram.nodes.clear()
        self.diagram.connections.clear()

    def get_statistics(self) -> Dict[str, int]:
        """Получить статистику диаграммы"""
        return {
            "nodes": len(self.diagram.nodes),
            "connections": len(self.diagram.connections),
            "classes": sum(1 for n in self.diagram.nodes if n.node_type.value == 'class'),
            "interfaces": sum(1 for n in self.diagram.nodes if n.node_type.value == 'interface'),
            "enums": sum(1 for n in self.diagram.nodes if n.node_type.value == 'enum'),
            "abstract_classes": sum(1 for n in self.diagram.nodes if n.node_type.value == 'abstract_class' or n.is_abstract),
            "total_attributes": sum(len(n.properties) for n in self.diagram.nodes),
            "total_methods": sum(len(n.methods) for n in self.diagram.nodes),
            "total_enum_literals": sum(len(n.enum_literals) for n in self.diagram.nodes)
        }