"""Tests for data models (Month 1 and ongoing).

Tests for Pydantic models: UMLProperty, UMLMethod, UMLNode, UMLConnection, UMLDiagram
"""

import pytest
from uuid import UUID
from logiccraft.models.diagram import (
    UMLProperty, UMLMethod, UMLNode, UMLConnection, UMLDiagram,
    ConnectionType, NodeType, UMLEnumLiteral
)


class TestUMLProperty:
    """Tests for UMLProperty model."""

    def test_create_property(self):
        """Test creating a basic property."""
        prop = UMLProperty(name="username", type="str")
        
        assert prop.name == "username"
        assert prop.type == "str"
        assert prop.visibility == "public"  # default
        assert prop.is_static is False
        assert prop.default_value is None

    def test_create_property_with_visibility(self):
        """Test creating property with different visibility."""
        prop_private = UMLProperty(name="_password", type="str", visibility="private")
        prop_protected = UMLProperty(name="_id", type="int", visibility="protected")
        
        assert prop_private.visibility == "private"
        assert prop_protected.visibility == "protected"

    def test_create_static_property(self):
        """Test creating static property."""
        prop = UMLProperty(name="MAX_SIZE", type="int", is_static=True, default_value="100")
        
        assert prop.is_static is True
        assert prop.default_value == "100"


class TestUMLMethod:
    """Tests for UMLMethod model."""

    def test_create_method(self):
        """Test creating a basic method."""
        method = UMLMethod(name="getName")
        
        assert method.name == "getName"
        assert method.return_type == "void"  # default
        assert method.visibility == "public"
        assert method.is_abstract is False
        assert method.is_static is False
        assert method.parameters == []

    def test_create_method_with_parameters(self):
        """Test creating method with parameters."""
        params = [
            UMLProperty(name="x", type="int"),
            UMLProperty(name="y", type="int")
        ]
        method = UMLMethod(
            name="move",
            return_type="void",
            parameters=params
        )
        
        assert len(method.parameters) == 2
        assert method.parameters[0].name == "x"

    def test_create_abstract_method(self):
        """Test creating abstract method."""
        method = UMLMethod(name="calculate", return_type="float", is_abstract=True)
        
        assert method.is_abstract is True


class TestUMLNode:
    """Tests for UMLNode model."""

    def test_create_node(self):
        """Test creating a node with auto-generated ID."""
        node = UMLNode(name="User", x=100.0, y=200.0)
        
        assert node.name == "User"
        assert node.x == 100.0
        assert node.y == 200.0
        assert isinstance(node.id, str)
        # Check it's a valid UUID
        UUID(node.id)

    def test_create_node_with_members(self):
        """Test creating node with properties and methods."""
        node = UMLNode(
            name="Order",
            x=0.0,
            y=0.0,
            properties=[
                UMLProperty(name="total", type="float")
            ],
            methods=[
                UMLMethod(name="calculateTotal", return_type="float")
            ]
        )
        
        assert len(node.properties) == 1
        assert len(node.methods) == 1
        assert node.properties[0].name == "total"

    def test_create_abstract_class(self):
        """Test creating abstract class node."""
        node = UMLNode(name="Shape", x=0.0, y=0.0, is_abstract=True)
        
        assert node.is_abstract is True

    def test_create_node_with_stereotype(self):
        """Test creating node with stereotype."""
        node = UMLNode(name="UserController", x=0.0, y=0.0, stereotype="controller")
        
        assert node.stereotype == "controller"


class TestUMLConnection:
    """Tests for UMLConnection model."""

    def test_create_connection(self):
        """Test creating a connection."""
        conn = UMLConnection(
            source_id="node-1",
            target_id="node-2",
            type=ConnectionType.association
        )
        
        assert conn.source_id == "node-1"
        assert conn.target_id == "node-2"
        assert conn.type == ConnectionType.association
        assert isinstance(conn.id, str)

    def test_connection_types(self):
        """Test all connection types."""
        types = [
            ConnectionType.association,
            ConnectionType.interaction,
            ConnectionType.realization,
            ConnectionType.inheritance,
            ConnectionType.dependency
        ]
        
        for i, conn_type in enumerate(types):
            conn = UMLConnection(
                source_id=f"s{i}",
                target_id=f"t{i}",
                type=conn_type
            )
            assert conn.type == conn_type

    def test_connection_with_multiplicity(self):
        """Test connection with multiplicity."""
        conn = UMLConnection(
            source_id="a",
            target_id="b",
            type=ConnectionType.association,
            multiplicity="1..*"
        )
        
        assert conn.multiplicity == "1..*"

    def test_connection_with_name(self):
        """Test connection with name/label."""
        conn = UMLConnection(
            source_id="a",
            target_id="b",
            type=ConnectionType.association,
            name="owns"
        )
        
        assert conn.name == "owns"


class TestUMLDiagram:
    """Tests for UMLDiagram model."""

    def test_create_diagram(self):
        """Test creating a diagram."""
        diagram = UMLDiagram(
            name="Shop System",
            nodes=[],
            connections=[]
        )
        
        assert diagram.name == "Shop System"
        assert diagram.nodes == []
        assert diagram.connections == []

    def test_diagram_serialization(self):
        """Test diagram JSON serialization."""
        diagram = UMLDiagram(
            name="Test",
            nodes=[
                UMLNode(name="User", x=100.0, y=100.0)
            ],
            connections=[]
        )
        
        json_str = diagram.model_dump_json()
        
        assert "User" in json_str
        assert "100.0" in json_str

    def test_diagram_deserialization(self):
        """Test diagram JSON deserialization."""
        import json
        
        data = {
            "id": "test-id",
            "name": "Test Diagram",
            "nodes": [
                {
                    "id": "node-1",
                    "name": "Product",
                    "x": 50.0,
                    "y": 50.0,
                    "properties": [],
                    "methods": [],
                    "is_abstract": False,
                    "stereotype": None
                }
            ],
            "connections": []
        }
        
        diagram = UMLDiagram.model_validate(data)
        
        assert diagram.name == "Test Diagram"
        assert len(diagram.nodes) == 1
        assert diagram.nodes[0].name == "Product"


class TestBackwardCompatibility:
    """Tests for backward compatibility aliases."""

    def test_property_model_alias(self):
        """Test PropertyModel alias works."""
        from logiccraft.models.diagram import PropertyModel
        
        prop = PropertyModel(name="test", type="int")
        assert isinstance(prop, UMLProperty)

    def test_node_model_alias(self):
        """Test NodeModel alias works."""
        from logiccraft.models.diagram import NodeModel
        
        node = NodeModel(name="Test", x=0.0, y=0.0)
        assert isinstance(node, UMLNode)

    def test_edge_model_alias(self):
        """Test EdgeModel alias works."""
        from logiccraft.models.diagram import EdgeModel
        
        edge = EdgeModel(source_id="a", target_id="b", type=ConnectionType.association)
        assert isinstance(edge, UMLConnection)

    def test_diagram_model_alias(self):
        """Test DiagramModel alias works."""
        from logiccraft.models.diagram import DiagramModel
        
        diagram = DiagramModel(name="Test", nodes=[], connections=[])
        assert isinstance(diagram, UMLDiagram)


class TestNodeType:
    """Tests for NodeType enum."""

    def test_node_type_values(self):
        """Test NodeType enum values."""
        assert NodeType.CLASS.value == "class"
        assert NodeType.INTERFACE.value == "interface"
        assert NodeType.ENUM.value == "enum"
        assert NodeType.ABSTRACT_CLASS.value == "abstract_class"

    def test_node_type_is_string(self):
        """Test NodeType is string-based."""
        assert isinstance(NodeType.CLASS, str)
        assert NodeType.CLASS == "class"


class TestUMLEnumLiteral:
    """Tests for UMLEnumLiteral model."""

    def test_create_enum_literal(self):
        """Test creating enum literal."""
        literal = UMLEnumLiteral(name="RED")
        assert literal.name == "RED"
        assert literal.value is None

    def test_create_enum_literal_with_value(self):
        """Test creating enum literal with value."""
        literal = UMLEnumLiteral(name="MAX", value="100")
        assert literal.name == "MAX"
        assert literal.value == "100"


class TestUMLNodeWithTypes:
    """Tests for UMLNode with node types."""

    def test_create_class_node(self):
        """Test creating a regular class node."""
        node = UMLNode(name="MyClass", x=0.0, y=0.0)
        assert node.node_type == NodeType.CLASS
        assert node.enum_literals == []

    def test_create_interface_node(self):
        """Test creating an interface node."""
        node = UMLNode(
            name="IRepository",
            x=0.0,
            y=0.0,
            node_type=NodeType.INTERFACE
        )
        assert node.node_type == NodeType.INTERFACE
        assert node.name == "IRepository"

    def test_create_enum_node(self):
        """Test creating an enum node."""
        node = UMLNode(
            name="Color",
            x=0.0,
            y=0.0,
            node_type=NodeType.ENUM
        )
        assert node.node_type == NodeType.ENUM

    def test_create_abstract_class_node(self):
        """Test creating an abstract class node."""
        node = UMLNode(
            name="BaseController",
            x=0.0,
            y=0.0,
            node_type=NodeType.ABSTRACT_CLASS
        )
        assert node.node_type == NodeType.ABSTRACT_CLASS

    def test_add_enum_literals(self):
        """Test adding enum literals to node."""
        node = UMLNode(name="Status", x=0.0, y=0.0, node_type=NodeType.ENUM)
        node.add_enum_literal("ACTIVE")
        node.add_enum_literal("INACTIVE", value="0")
        
        assert len(node.enum_literals) == 2
        assert node.enum_literals[0].name == "ACTIVE"
        assert node.enum_literals[0].value is None
        assert node.enum_literals[1].name == "INACTIVE"
        assert node.enum_literals[1].value == "0"

    def test_remove_enum_literal(self):
        """Test removing enum literal."""
        node = UMLNode(name="Status", x=0.0, y=0.0, node_type=NodeType.ENUM)
        node.add_enum_literal("ACTIVE")
        node.add_enum_literal("INACTIVE")
        
        assert node.remove_enum_literal(0) is True
        assert len(node.enum_literals) == 1
        assert node.enum_literals[0].name == "INACTIVE"
        
        assert node.remove_enum_literal(10) is False


class TestDiagramManagerWithTypes:
    """Tests for DiagramManager with node types."""

    def test_add_interface_node(self):
        """Test adding interface node with auto-naming."""
        from logiccraft.models.diagram_manager import DiagramManager
        
        mgr = DiagramManager()
        node = mgr.add_node(0, 0, node_type=NodeType.INTERFACE)
        
        assert node.node_type == NodeType.INTERFACE
        assert node.name.startswith("IInterface")

    def test_add_enum_node(self):
        """Test adding enum node with auto-naming."""
        from logiccraft.models.diagram_manager import DiagramManager
        
        mgr = DiagramManager()
        node = mgr.add_node(0, 0, node_type=NodeType.ENUM)
        
        assert node.node_type == NodeType.ENUM
        assert node.name.startswith("Enum")

    def test_statistics_with_types(self):
        """Test statistics include node types."""
        from logiccraft.models.diagram_manager import DiagramManager
        
        mgr = DiagramManager()
        mgr.add_node(0, 0, "MyClass", NodeType.CLASS)
        mgr.add_node(100, 0, "IRepo", NodeType.INTERFACE)
        mgr.add_node(200, 0, "Color", NodeType.ENUM)
        
        stats = mgr.get_statistics()
        
        assert stats["classes"] == 1
        assert stats["interfaces"] == 1
        assert stats["enums"] == 1
        assert stats["nodes"] == 3
