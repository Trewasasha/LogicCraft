"""Сервис сериализации диаграмм"""
import json
import logging
from typing import Dict, Any, Tuple
from ..models.diagram import (
    UMLDiagram, UMLNode, UMLConnection,
    UseCaseActor, UseCaseScenario, UseCaseConnection, _strip_dict_keys
)

logger = logging.getLogger(__name__)

class SerializationService:
    @staticmethod
    def serialize(diagram: UMLDiagram) -> Dict[str, Any]:
        return {
            "version": "1.0",
            "name": diagram.name.strip() if isinstance(diagram.name, str) else "Untitled",
            "id": diagram.id,
            "diagram_type": diagram.diagram_type.value,
            "nodes": [SerializationService._serialize_node(node) for node in diagram.nodes],
            "connections": [SerializationService._serialize_connection(conn) for conn in diagram.connections],
            "uc_actors": [a.model_dump(exclude_none=True) for a in diagram.uc_actors],
            "uc_scenarios": [s.model_dump(exclude_none=True) for s in diagram.uc_scenarios],
            "uc_connections": [c.model_dump(exclude_none=True) for c in diagram.uc_connections],
        }

    @staticmethod
    def _serialize_node(node: UMLNode) -> Dict[str, Any]:
        return {
            "id": node.id,
            "name": node.name.strip() if isinstance(node.name, str) else "",
            "x": node.x,
            "y": node.y,
            "node_type": node.node_type.value,
            "properties": [prop.model_dump(exclude_none=True) for prop in node.properties],
            "methods": [method.model_dump(exclude_none=True) for method in node.methods],
            "enum_literals": [lit.model_dump(exclude_none=True) for lit in node.enum_literals],
            "is_abstract": node.is_abstract,
            "stereotype": node.stereotype
        }

    @staticmethod
    def _serialize_connection(conn: UMLConnection) -> Dict[str, Any]:
        return {
            "id": conn.id,
            "source_id": conn.source_id,
            "target_id": conn.target_id,
            "type": conn.type.value,
            "source_anchor": conn.source_anchor,
            "target_anchor": conn.target_anchor,
            "multiplicity": conn.multiplicity,
            "name": conn.name
        }

    @staticmethod
    def deserialize(data: Dict[str, Any]) -> UMLDiagram:
        # МАГИЯ: Рекурсивно чистим все ключи и значения от пробелов перед созданием моделей
        clean_data = _strip_dict_keys(data)

        nodes = [UMLNode(**node_data) for node_data in clean_data.get("nodes", [])]
        connections = [UMLConnection(**conn_data) for conn_data in clean_data.get("connections", [])]
        uc_actors = [UseCaseActor(**a) for a in clean_data.get("uc_actors", [])]
        uc_scenarios = [UseCaseScenario(**s) for s in clean_data.get("uc_scenarios", [])]
        uc_connections = [UseCaseConnection(**c) for c in clean_data.get("uc_connections", [])]

        from ..models.diagram import DiagramType
        diagram_type = DiagramType(clean_data.get("diagram_type", "class"))

        return UMLDiagram(
            id=clean_data.get("id"),
            name=clean_data.get("name", "Untitled"),
            diagram_type=diagram_type,
            nodes=nodes,
            connections=connections,
            uc_actors=uc_actors,
            uc_scenarios=uc_scenarios,
            uc_connections=uc_connections,
        )

    @staticmethod
    def save_to_json(diagram: UMLDiagram, filepath: str) -> bool:
        try:
            data = SerializationService.serialize(diagram)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
            return False

    @staticmethod
    def load_from_json(filepath: str) -> Tuple[bool, UMLDiagram]:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            diagram = SerializationService.deserialize(data)
            return True, diagram
        except Exception as e:
            logger.error(f"Error loading from JSON: {e}")
            return False, None