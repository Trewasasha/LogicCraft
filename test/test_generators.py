"""Tests for diagram I/O and serialization utilities.

Tests for diagram_io.py module including:
- DiagramMapper: parsing and formatting attributes/methods
- DiagramIO: saving and loading diagrams
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import json

from logiccraft.models.diagram import UMLNode, UMLProperty, UMLMethod, UMLDiagram
from logiccraft.utils.diagram_io import DiagramMapper, DiagramIO, save_diagram, load_diagram


class TestDiagramMapperParseAttribute:
    """Tests for parse_attribute method."""

    def test_parse_public_attribute(self):
        """Test parsing public attribute '+ name: str'."""
        result = DiagramMapper.parse_attribute("+ name: str")
        
        assert result.name == "name"
        assert result.type == "str"
        assert result.visibility == "public"

    def test_parse_private_attribute(self):
        """Test parsing private attribute '- _password: str'."""
        result = DiagramMapper.parse_attribute("- _password: str")
        
        assert result.name == "_password"
        assert result.visibility == "private"

    def test_parse_protected_attribute(self):
        """Test parsing protected attribute '# _id: int'."""
        result = DiagramMapper.parse_attribute("# _id: int")
        
        assert result.name == "_id"
        assert result.visibility == "protected"

    def test_parse_attribute_without_type(self):
        """Test parsing attribute without type annotation."""
        result = DiagramMapper.parse_attribute("+ data")
        
        assert result.name == "data"
        assert result.type == "Any"

    def test_parse_attribute_with_whitespace(self):
        """Test parsing attribute with extra whitespace."""
        result = DiagramMapper.parse_attribute("  +  name  :  str  ")
        
        assert result.name == "name"
        assert result.type == "str"


class TestDiagramMapperParseMethod:
    """Tests for parse_method method."""

    def test_parse_public_method(self):
        """Test parsing public method '+ getName(): str'."""
        result = DiagramMapper.parse_method("+ getName(): str")
        
        assert result.name == "getName"
        assert result.return_type == "str"
        assert result.visibility == "public"

    def test_parse_private_method(self):
        """Test parsing private method '- _validate(): bool'."""
        result = DiagramMapper.parse_method("- _validate(): bool")
        
        assert result.name == "_validate"
        assert result.visibility == "private"

    def test_parse_method_without_parens(self):
        """Test parsing method without parentheses."""
        result = DiagramMapper.parse_method("+ process: void")
        
        assert result.name == "process"
        assert result.return_type == "void"

    def test_parse_method_without_return_type(self):
        """Test parsing method without explicit return type."""
        result = DiagramMapper.parse_method("+ doSomething()")
        
        assert result.name == "doSomething"
        assert result.return_type == "void"


class TestDiagramMapperFormatAttribute:
    """Tests for format_attribute method."""

    def test_format_public_attribute(self):
        """Test formatting public attribute."""
        prop = UMLProperty(name="username", type="str", visibility="public")
        result = DiagramMapper.format_attribute(prop)
        
        assert result == "+ username: str"

    def test_format_private_attribute(self):
        """Test formatting private attribute."""
        prop = UMLProperty(name="_password", type="str", visibility="private")
        result = DiagramMapper.format_attribute(prop)
        
        assert result == "- _password: str"

    def test_format_protected_attribute(self):
        """Test formatting protected attribute."""
        prop = UMLProperty(name="_id", type="int", visibility="protected")
        result = DiagramMapper.format_attribute(prop)
        
        assert result == "# _id: int"


class TestDiagramMapperFormatMethod:
    """Tests for format_method method."""

    def test_format_public_method(self):
        """Test formatting public method."""
        method = UMLMethod(name="getName", return_type="str", visibility="public")
        result = DiagramMapper.format_method(method)
        
        assert result == "+ getName(): str"

    def test_format_private_method(self):
        """Test formatting private method."""
        method = UMLMethod(name="_validate", return_type="bool", visibility="private")
        result = DiagramMapper.format_method(method)
        
        assert result == "- _validate(): bool"


class TestDiagramMapperCardToNode:
    """Tests for card_to_node conversion."""

    def test_card_to_node_conversion(self):
        """Test converting UMLCard to UMLNode."""
        card = Mock()
        card.card_name = "User"
        card.card_x = 100.0
        card.card_y = 200.0
        card.attributes = ["+ username: str", "- _password: str"]
        card.methods = ["+ login(): bool"]
        
        node = DiagramMapper.card_to_node(card, node_id="test-id")
        
        assert node.id == "test-id"
        assert node.name == "User"
        assert node.x == 100.0
        assert node.y == 200.0
        assert len(node.properties) == 2
        assert len(node.methods) == 1


class TestDiagramMapperNodeToCard:
    """Tests for node_to_card conversion."""

    def test_node_to_card_conversion(self):
        """Test converting UMLNode to UMLCard."""
        node = UMLNode(
            id="node-1",
            name="Order",
            x=50.0,
            y=75.0,
            properties=[UMLProperty(name="total", type="float")],
            methods=[UMLMethod(name="pay", return_type="void")]
        )
        
        card = DiagramMapper.node_to_card(node)
        
        assert card.name == "Order"
        assert card.x == 50.0
        assert card.y == 75.0
        assert len(card.attributes) == 1
        assert "+ total: float" in card.attributes


class TestDiagramIOSave:
    """Tests for DiagramIO.save_diagram."""

    @patch('pathlib.Path.write_text')
    @patch('pathlib.Path.__init__', return_value=None)
    def test_save_diagram_creates_json(self, mock_path_init, mock_write):
        """Test saving diagram creates JSON file."""
        card = Mock()
        card.card_name = "TestClass"
        card.card_x = 0.0
        card.card_y = 0.0
        card.attributes = []
        card.methods = []
        
        with patch.object(Path, 'mkdir', return_value=None):
            DiagramIO.save_diagram([card], "/test/diagram.json", "Test Diagram")
        
        mock_write.assert_called_once()
        written_content = mock_write.call_args[0][0]
        assert "Test Diagram" in written_content


class TestDiagramIOLoad:
    """Tests for DiagramIO.load_diagram."""

    @patch('pathlib.Path.read_text')
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_diagram_reads_json(self, mock_exists, mock_read):
        """Test loading diagram from JSON file."""
        diagram_data = {
            "id": "test-id",
            "name": "Loaded Diagram",
            "nodes": [
                {
                    "id": "node-1",
                    "name": "Product",
                    "x": 100.0,
                    "y": 100.0,
                    "properties": [],
                    "methods": [],
                    "is_abstract": False,
                    "stereotype": None
                }
            ],
            "connections": []
        }
        mock_read.return_value = json.dumps(diagram_data)
        
        with patch.object(Path, '__init__', return_value=None):
            cards, name = DiagramIO.load_diagram("/test/diagram.json")
        
        assert name == "Loaded Diagram"
        assert len(cards) == 1


class TestConvenienceFunctions:
    """Tests for convenience functions save_diagram and load_diagram."""

    @patch.object(DiagramIO, 'save_diagram')
    def test_save_diagram_convenience(self, mock_save):
        """Test save_diagram convenience function."""
        save_diagram([], "/test.json", "Test")
        mock_save.assert_called_once()

    @patch.object(DiagramIO, 'load_diagram')
    def test_load_diagram_convenience(self, mock_load):
        """Test load_diagram convenience function."""
        mock_load.return_value = ([], "Test")
        result = load_diagram("/test.json")
        mock_load.assert_called_once()
        assert result == ([], "Test")
