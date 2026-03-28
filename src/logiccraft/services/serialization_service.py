"""Сервис сериализации диаграмм"""
import json
from pathlib import Path
from typing import Dict, Any, Tuple, List
from ..models.diagram import UMLDiagram, UMLNode, UMLConnection


class SerializationService:
    """Сериализация и десериализация диаграмм"""

    @staticmethod
    def serialize(diagram: UMLDiagram) -> Dict[str, Any]:
        """Сериализовать диаграмму в словарь"""
        return {
            "name": diagram.name,
            "id": diagram.id,
            "nodes": [SerializationService._serialize_node(node) for node in diagram.nodes],
            "connections": [SerializationService._serialize_connection(conn) for conn in diagram.connections]
        }

    @staticmethod
    def _serialize_node(node: UMLNode) -> Dict[str, Any]:
        """Сериализовать узел"""
        return {
            "id": node.id,
            "name": node.name,
            "x": node.x,
            "y": node.y,
            "properties": [prop.model_dump() for prop in node.properties],
            "methods": [method.model_dump() for method in node.methods],
            "is_abstract": node.is_abstract,
            "stereotype": node.stereotype
        }

    @staticmethod
    def _serialize_connection(conn: UMLConnection) -> Dict[str, Any]:
        """Сериализовать связь"""
        return {
            "id": conn.id,
            "source_id": conn.source_id,
            "target_id": conn.target_id,
            "type": conn.type.value,
            "multiplicity": conn.multiplicity,
            "name": conn.name
        }

    @staticmethod
    def deserialize(data: Dict[str, Any]) -> UMLDiagram:
        """Десериализовать диаграмму из словаря"""
        nodes = [UMLNode(**node_data) for node_data in data.get("nodes", [])]
        connections = [UMLConnection(**conn_data) for conn_data in data.get("connections", [])]

        return UMLDiagram(
            id=data.get("id"),
            name=data.get("name", "Untitled"),
            nodes=nodes,
            connections=connections
        )

    @staticmethod
    def save_to_json(diagram: UMLDiagram, filepath: str) -> bool:
        """Сохранить диаграмму в JSON файл"""
        try:
            data = SerializationService.serialize(diagram)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return False

    @staticmethod
    def load_from_json(filepath: str) -> Tuple[bool, UMLDiagram]:
        """Загрузить диаграмму из JSON файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            diagram = SerializationService.deserialize(data)
            return True, diagram
        except Exception as e:
            print(f"Error loading from JSON: {e}")
            return False, None