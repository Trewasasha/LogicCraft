"""Diagram serialization and UI-model mapping utilities."""

import json
from pathlib import Path
from typing import Optional

from logiccraft.models.diagram import UMLDiagram, UMLNode, UMLProperty, UMLMethod, UMLConnection
from logiccraft.view.widgets import UMLCard


class DiagramMapper:
    """Maps between UMLCard (UI) and UMLNode (data model)."""

    @staticmethod
    def parse_attribute(attr_str: str) -> UMLProperty:
        """Parse attribute string like '+ name: str' into UMLProperty."""
        attr_str = attr_str.strip()
        
        # Determine visibility
        visibility = "public"
        if attr_str.startswith("+"):
            visibility = "public"
            attr_str = attr_str[1:].strip()
        elif attr_str.startswith("-"):
            visibility = "private"
            attr_str = attr_str[1:].strip()
        elif attr_str.startswith("#"):
            visibility = "protected"
            attr_str = attr_str[1:].strip()
        
        # Parse name and type
        if ":" in attr_str:
            name, type_str = attr_str.split(":", 1)
            name = name.strip()
            type_str = type_str.strip()
        else:
            name = attr_str
            type_str = "Any"
        
        return UMLProperty(
            name=name,
            type=type_str,
            visibility=visibility
        )

    @staticmethod
    def parse_method(method_str: str) -> UMLMethod:
        """Parse method string like '+ getName(): str' into UMLMethod."""
        method_str = method_str.strip()
        
        # Determine visibility
        visibility = "public"
        if method_str.startswith("+"):
            visibility = "public"
            method_str = method_str[1:].strip()
        elif method_str.startswith("-"):
            visibility = "private"
            method_str = method_str[1:].strip()
        elif method_str.startswith("#"):
            visibility = "protected"
            method_str = method_str[1:].strip()
        
        # Parse return type
        return_type = "void"
        if ":" in method_str:
            method_str, return_type = method_str.rsplit(":", 1)
            return_type = return_type.strip()
        
        # Remove parentheses if present
        if "(" in method_str:
            name = method_str.split("(")[0].strip()
        else:
            name = method_str.strip()
        
        return UMLMethod(
            name=name,
            return_type=return_type,
            visibility=visibility
        )

    @staticmethod
    def format_attribute(prop: UMLProperty) -> str:
        """Format UMLProperty as string like '+ name: str'."""
        vis_map = {"public": "+", "private": "-", "protected": "#"}
        vis = vis_map.get(prop.visibility, "+")
        return f"{vis} {prop.name}: {prop.type}"

    @staticmethod
    def format_method(method: UMLMethod) -> str:
        """Format UMLMethod as string like '+ getName(): str'."""
        vis_map = {"public": "+", "private": "-", "protected": "#"}
        vis = vis_map.get(method.visibility, "+")
        return f"{vis} {method.name}(): {method.return_type}"

    @classmethod
    def card_to_node(cls, card: UMLCard, node_id: Optional[str] = None) -> UMLNode:
        """Convert UMLCard widget to UMLNode model."""
        properties = [cls.parse_attribute(attr) for attr in card.attributes]
        methods = [cls.parse_method(method) for method in card.methods]
        
        return UMLNode(
            id=node_id or f"node_{id(card)}",
            name=card.card_name,
            x=card.card_x,
            y=card.card_y,
            properties=properties,
            methods=methods
        )

    @classmethod
    def node_to_card(
        cls,
        node: UMLNode,
        on_select=None,
        on_move=None
    ) -> UMLCard:
        """Convert UMLNode model to UMLCard widget."""
        attributes = [cls.format_attribute(prop) for prop in node.properties]
        methods = [cls.format_method(method) for method in node.methods]
        
        return UMLCard(
            x=node.x,
            y=node.y,
            name=node.name,
            attributes=attributes,
            methods=methods,
            on_select=on_select,
            on_move=on_move
        )


class DiagramIO:
    """Handles saving and loading diagrams to/from disk."""

    @staticmethod
    def save_diagram(
        cards: list[UMLCard],
        filepath: Path | str,
        diagram_name: str = "Untitled"
    ) -> None:
        """Save list of UMLCards to JSON file."""
        filepath = Path(filepath)
        
        # Convert cards to nodes
        nodes = []
        for i, card in enumerate(cards):
            node = DiagramMapper.card_to_node(card, node_id=f"node_{i}")
            nodes.append(node)
        
        # Create diagram (connections empty for now)
        diagram = UMLDiagram(
            name=diagram_name,
            nodes=nodes,
            connections=[]
        )
        
        # Save to JSON
        filepath.write_text(
            diagram.model_dump_json(indent=2),
            encoding="utf-8"
        )

    @staticmethod
    def load_diagram(
        filepath: Path | str,
        on_select=None,
        on_move=None
    ) -> tuple[list[UMLCard], str]:
        """Load diagram from JSON file and return list of UMLCards."""
        filepath = Path(filepath)
        
        # Load from JSON
        data = json.loads(filepath.read_text(encoding="utf-8"))
        diagram = UMLDiagram.model_validate(data)
        
        # Convert nodes to cards
        cards = []
        for node in diagram.nodes:
            card = DiagramMapper.node_to_card(node, on_select, on_move)
            cards.append(card)
        
        return cards, diagram.name


def save_diagram(
    cards: list[UMLCard],
    filepath: Path | str,
    diagram_name: str = "Untitled"
) -> None:
    """Convenience function to save diagram."""
    DiagramIO.save_diagram(cards, filepath, diagram_name)


def load_diagram(
    filepath: Path | str,
    on_select=None,
    on_move=None
) -> tuple[list[UMLCard], str]:
    """Convenience function to load diagram."""
    return DiagramIO.load_diagram(filepath, on_select, on_move)
