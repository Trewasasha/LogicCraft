from pydantic import BaseModel, Field
from enum import Enum
from uuid import uuid4
from typing import Optional, List


class NodeType(str, Enum):
    """Типы UML узлов"""
    CLASS = "class"
    INTERFACE = "interface"
    ENUM = "enum"
    ABSTRACT_CLASS = "abstract_class"


class UMLEnumLiteral(BaseModel):
    """Значение перечисления (Enum literal)"""
    name: str
    value: Optional[str] = None


class UMLProperty(BaseModel):
    """Свойства класса"""
    name: str
    type: str
    visibility: str = "public"
    is_static: bool = False
    default_value: Optional[str] = None


class UMLMethod(BaseModel):
    """Методы класса"""
    name: str
    return_type: Optional[str] = "void"
    visibility: str = "public"
    is_abstract: bool = False
    is_static: bool = False
    parameters: list[UMLProperty] = Field(default_factory=list)


class UMLNode(BaseModel):
    """UML class node model with position and members."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    x: float
    y: float
    properties: list[UMLProperty] = Field(default_factory=list)
    methods: list[UMLMethod] = Field(default_factory=list)
    is_abstract: bool = False
    stereotype: Optional[str] = None
    node_type: NodeType = NodeType.CLASS
    enum_literals: List[UMLEnumLiteral] = Field(default_factory=list)

    def add_enum_literal(self, name: str, value: Optional[str] = None) -> None:
        """Добавить значение перечисления"""
        literal = UMLEnumLiteral(name=name, value=value)
        self.enum_literals.append(literal)

    def remove_enum_literal(self, index: int) -> bool:
        """Удалить значение перечисления по индексу"""
        if 0 <= index < len(self.enum_literals):
            self.enum_literals.pop(index)
            return True
        return False

    def add_attribute(self, name: str, type: str, visibility: str = "public",
                      is_static: bool = False, default_value: Optional[str] = None) -> None:
        """Добавить атрибут"""
        prop = UMLProperty(
            name=name,
            type=type,
            visibility=visibility,
            is_static=is_static,
            default_value=default_value
        )
        self.properties.append(prop)

    def remove_attribute(self, attr_name: str) -> bool:
        """Удалить атрибут"""
        for i, prop in enumerate(self.properties):
            if prop.name == attr_name:
                self.properties.pop(i)
                return True
        return False

    def add_method(self, name: str, return_type: str = "void",
                   visibility: str = "public", is_abstract: bool = False,
                   is_static: bool = False) -> None:
        """Добавить метод"""
        method = UMLMethod(
            name=name,
            return_type=return_type,
            visibility=visibility,
            is_abstract=is_abstract,
            is_static=is_static
        )
        self.methods.append(method)

    def remove_method(self, method_name: str) -> bool:
        """Удалить метод"""
        for i, method in enumerate(self.methods):
            if method.name == method_name:
                self.methods.pop(i)
                return True
        return False


class ConnectionType(str, Enum):
    """Типы соединения"""
    association = "association"      # простая связь
    inheritance = "inheritance"      # наследование
    composition = "composition"      # композиция
    aggregation = "aggregation"      # агрегация
    dependency = "dependency"        # зависимость
    interaction = "interaction"      # взаимодействие
    realization = "realization"      # реализация интерфейса


class UMLConnection(BaseModel):
    """Соединения между двумя узлами"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    source_id: str
    target_id: str
    type: ConnectionType = ConnectionType.association
    source_anchor: str = "right"
    target_anchor: str = "left"
    multiplicity: Optional[str] = None
    name: Optional[str] = None


class UMLDiagram(BaseModel):
    """Модель диаграммы"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    nodes: list[UMLNode] = Field(default_factory=list)
    connections: list[UMLConnection] = Field(default_factory=list)

    def get_node(self, node_id: str) -> Optional[UMLNode]:
        """Получить узел по ID"""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def get_connections_for_node(self, node_id: str) -> list[UMLConnection]:
        """Получить все связи для узла"""
        return [conn for conn in self.connections
                if conn.source_id == node_id or conn.target_id == node_id]

    def validate(self) -> list[str]:
        """Валидация диаграммы"""
        errors = []
        node_ids = {node.id for node in self.nodes}

        for conn in self.connections:
            if conn.source_id not in node_ids:
                errors.append(f"Connection {conn.id}: source {conn.source_id} not found")
            if conn.target_id not in node_ids:
                errors.append(f"Connection {conn.id}: target {conn.target_id} not found")

        return errors


# Backward compatibility aliases
PropertyModel = UMLProperty
NodeModel = UMLNode
EdgeModel = UMLConnection
DiagramModel = UMLDiagram