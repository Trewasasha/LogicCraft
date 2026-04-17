"""Tests for data models (Month 1 and ongoing).

Tests for Pydantic models: UMLProperty, UMLMethod, UMLNode, UMLConnection, UMLDiagram
"""

import pytest
from uuid import UUID
from logiccraft.models.diagram import (
    UMLProperty, UMLMethod, UMLNode, UMLConnection, UMLDiagram,
    ConnectionType
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
