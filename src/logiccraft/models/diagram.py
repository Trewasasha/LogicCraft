import re
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum
from uuid import uuid4
from typing import Optional, List, Any, Dict

def _strip_dict_keys(d: Any) -> Any:
    """Рекурсивно удаляет пробелы из ключей и значений при загрузке JSON"""
    if isinstance(d, dict):
        return {k.strip() if isinstance(k, str) else k: _strip_dict_keys(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [_strip_dict_keys(item) for item in d]
    elif isinstance(d, str):
        return d.strip()
    return d

class NodeType(str, Enum):
    CLASS = "class"
    INTERFACE = "interface"
    ENUM = "enum"
    ABSTRACT_CLASS = "abstract_class"

class DiagramType(str, Enum):
    CLASS = "class"
    USE_CASE = "use_case"

class UMLEnumLiteral(BaseModel):
    name: str
    value: Optional[str] = None

    @field_validator('name', 'value', mode='before')
    @classmethod
    def strip_strings(cls, v: Any) -> Any:
        return v.strip() if isinstance(v, str) else v

class UMLProperty(BaseModel):
    name: str
    type: str
    visibility: str = "public"
    is_static: bool = False
    default_value: Optional[str] = None

    @field_validator('name', 'type', 'visibility', 'default_value', mode='before')
    @classmethod
    def strip_strings(cls, v: Any) -> Any:
        return v.strip() if isinstance(v, str) else v

    @model_validator(mode='after')
    def clean_property(self) -> 'UMLProperty':
        clean_name = self.name
        if clean_name.startswith('+'):
            self.visibility = 'public'
            clean_name = clean_name[1:].strip()
        elif clean_name.startswith('-'):
            self.visibility = 'private'
            clean_name = clean_name[1:].strip()
        elif clean_name.startswith('#'):
            self.visibility = 'protected'
            clean_name = clean_name[1:].strip()
        self.name = clean_name
        return self

class UMLMethod(BaseModel):
    name: str
    return_type: Optional[str] = "void"
    visibility: str = "public"
    is_abstract: bool = False
    is_static: bool = False
    parameters: List[UMLProperty] = Field(default_factory=list)

    @field_validator('name', 'return_type', 'visibility', mode='before')
    @classmethod
    def strip_strings(cls, v: Any) -> Any:
        return v.strip() if isinstance(v, str) else v

    @model_validator(mode='after')
    def parse_uml_signature(self) -> 'UMLMethod':
        clean_name = self.name
        if clean_name.startswith('+'):
            self.visibility = 'public'
            clean_name = clean_name[1:].strip()
        elif clean_name.startswith('-'):
            self.visibility = 'private'
            clean_name = clean_name[1:].strip()
        elif clean_name.startswith('#'):
            self.visibility = 'protected'
            clean_name = clean_name[1:].strip()

        if ':' in clean_name:
            parts = clean_name.split(':', 1)
            clean_name = parts[0].strip()
            extracted_type = parts[1].strip()
            if not self.return_type or str(self.return_type).lower() in ['void', 'none', '']:
                self.return_type = extracted_type

        self.name = clean_name
        if not self.return_type or str(self.return_type).lower() == 'void':
            self.return_type = 'None'
        return self

class UMLNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    x: float
    y: float
    properties: List[UMLProperty] = Field(default_factory=list)
    methods: List[UMLMethod] = Field(default_factory=list)
    is_abstract: bool = False
    stereotype: Optional[str] = None
    node_type: NodeType = NodeType.CLASS
    enum_literals: List[UMLEnumLiteral] = Field(default_factory=list)

    def add_enum_literal(self, name: str, value: Optional[str] = None) -> None:
        literal = UMLEnumLiteral(name=name, value=value)
        self.enum_literals.append(literal)

    def remove_enum_literal(self, index: int) -> bool:
        if 0 <= index < len(self.enum_literals):
            self.enum_literals.pop(index)
            return True
        return False

    def add_attribute(self, name: str, type: str, visibility: str = "public",
                      is_static: bool = False, default_value: Optional[str] = None) -> None:
        prop = UMLProperty(name=name, type=type, visibility=visibility, is_static=is_static, default_value=default_value)
        self.properties.append(prop)

    def remove_attribute(self, attr_name: str) -> bool:
        for i, prop in enumerate(self.properties):
            if prop.name == attr_name:
                self.properties.pop(i)
                return True
        return False

    def add_method(self, name: str, return_type: str = "void",
                   visibility: str = "public", is_abstract: bool = False,
                   is_static: bool = False) -> None:
        method = UMLMethod(name=name, return_type=return_type, visibility=visibility, is_abstract=is_abstract, is_static=is_static)
        self.methods.append(method)

    def remove_method(self, method_name: str) -> bool:
        for i, method in enumerate(self.methods):
            if method.name == method_name:
                self.methods.pop(i)
                return True
        return False

class ConnectionType(str, Enum):
    association = "association"
    inheritance = "inheritance"
    composition = "composition"
    aggregation = "aggregation"
    dependency = "dependency"
    interaction = "interaction"
    realization = "realization"
    uc_association = "uc_association"
    uc_include = "uc_include"
    uc_extend = "uc_extend"

class UMLConnection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    source_id: str
    target_id: str
    type: ConnectionType = ConnectionType.association
    source_anchor: str = "right"
    target_anchor: str = "left"
    multiplicity: Optional[str] = None
    name: Optional[str] = None

class UseCaseActor(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    x: float
    y: float

class UseCaseScenario(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    x: float
    y: float
    description: Optional[str] = None

class UseCaseConnection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    source_id: str
    target_id: str
    type: ConnectionType = ConnectionType.uc_association
    source_anchor: str = "right"
    target_anchor: str = "left"

class UMLDiagram(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    diagram_type: DiagramType = DiagramType.CLASS
    nodes: List[UMLNode] = Field(default_factory=list)
    connections: List[UMLConnection] = Field(default_factory=list)
    uc_actors: List[UseCaseActor] = Field(default_factory=list)
    uc_scenarios: List[UseCaseScenario] = Field(default_factory=list)
    uc_connections: List[UseCaseConnection] = Field(default_factory=list)

    def get_node(self, node_id: str) -> Optional[UMLNode]:
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def get_connections_for_node(self, node_id: str) -> List[UMLConnection]:
        return [conn for conn in self.connections
                if conn.source_id == node_id or conn.target_id == node_id]

    def validate(self) -> List[str]:
        errors = []
        node_ids = {node.id for node in self.nodes}
        for conn in self.connections:
            if conn.source_id not in node_ids:
                errors.append(f"Connection {conn.id}: source {conn.source_id} not found")
            if conn.target_id not in node_ids:
                errors.append(f"Connection {conn.id}: target {conn.target_id} not found")
        return errors

# Обновляем forward references
UMLDiagram.model_rebuild()

# Backward compatibility aliases
PropertyModel = UMLProperty
NodeModel = UMLNode
EdgeModel = UMLConnection
DiagramModel = UMLDiagram