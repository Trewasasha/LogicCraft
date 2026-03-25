from pydantic import BaseModel, Field
from enum import Enum
from uuid import uuid4
from typing import Optional


class UMLProperty(BaseModel):
    #свойства
    name: str
    type: str
    visibility: str = "public"
    is_static: bool = False
    default_value: Optional[str] = None


class UMLMethod(BaseModel):
    # методы
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
    properties: list[UMLProperty] = []  #свойства
    methods: list[UMLMethod] = []  #методы
    is_abstract: bool = False
    stereotype: Optional[str] = None

    def add_attribute(self, name: str, type: str, visibility: str = "public", 
                     is_static: bool = False, default_value: Optional[str] = None) -> None:
      
        prop = UMLProperty(
            name=name,
            type=type,
            visibility=visibility,
            is_static=is_static,
            default_value=default_value
        )
        self.properties.append(prop)

    def remove_method(self, method_name: str) -> bool:
       
        for i, method in enumerate(self.methods):
            if method.name == method_name:
                self.methods.pop(i)
                return True
        return False


class ConnectionType(str, Enum):
    #типы соединения
    association = "association"  # простая связь
    interaction = "interaction"  # взаимодействие
    realization = "realization"  # интерфейса
    inheritance = "inheritance"  # наследование
    dependency = "dependency"  # зависимость


class UMLConnection(BaseModel):
     #соединения между 2 узлами
    id: str = Field(default_factory=lambda: str(uuid4()))
    source_id: str
    target_id: str
    type: ConnectionType
    multiplicity: Optional[str] = None
    name: Optional[str] = None


class UMLDiagram(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    nodes: list[UMLNode]
    connections: list[UMLConnection]


# Backward compatibility aliases
PropertyModel = UMLProperty
NodeModel = UMLNode
EdgeModel = UMLConnection
DiagramModel = UMLDiagram