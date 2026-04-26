"""Модели данных LogicCraft"""

from .diagram import (
    UMLDiagram,
    UMLNode,
    UMLConnection,
    UMLProperty,
    UMLMethod,
    ConnectionType,
    NodeType,
    UMLEnumLiteral,
    PropertyModel,
    NodeModel,
    EdgeModel,
    DiagramModel
)

from .diagram_manager import DiagramManager
from .engine import DiagramEngine, ValidationError
from .project_settings import ProjectSettings, CodeStyleSettings
from .structure_template import StructureTemplate

__all__ = [
    "UMLDiagram",
    "UMLNode",
    "UMLConnection",
    "UMLProperty",
    "UMLMethod",
    "ConnectionType",
    "NodeType",
    "UMLEnumLiteral",
    "PropertyModel",
    "NodeModel",
    "EdgeModel",
    "DiagramModel",
    "DiagramManager",
    "DiagramEngine",
    "ValidationError",
    "ProjectSettings",
    "CodeStyleSettings",
    "StructureTemplate"
]