"""Connection lines and anchors for UML diagrams."""

import flet as ft
import math
from typing import Callable, Optional


class AnchorPoint:
    """Anchor point on the edge of a UML card for connecting lines."""
    
    # Anchor positions
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    
    def __init__(self, position: str, x: float, y: float):
        self.position = position  # top, bottom, left, right
        self.x = x
        self.y = y
    
    @staticmethod
    def calculate_anchors(card_x: float, card_y: float, width: float, height: float) -> dict[str, 'AnchorPoint']:
        """Calculate anchor points for a card."""
        return {
            AnchorPoint.TOP: AnchorPoint(AnchorPoint.TOP, card_x + width / 2, card_y),
            AnchorPoint.BOTTOM: AnchorPoint(AnchorPoint.BOTTOM, card_x + width / 2, card_y + height),
            AnchorPoint.LEFT: AnchorPoint(AnchorPoint.LEFT, card_x, card_y + height / 2),
            AnchorPoint.RIGHT: AnchorPoint(AnchorPoint.RIGHT, card_x + width, card_y + height / 2),
        }
    
    @staticmethod
    def find_best_anchor(card_x: float, card_y: float, width: float, height: float, 
                         target_x: float, target_y: float) -> 'AnchorPoint':
        """Find the best anchor point to connect to a target position."""
        anchors = AnchorPoint.calculate_anchors(card_x, card_y, width, height)
        
        best_anchor = None
        min_distance = float('inf')
        
        for anchor in anchors.values():
            distance = math.sqrt((anchor.x - target_x) ** 2 + (anchor.y - target_y) ** 2)
            if distance < min_distance:
                min_distance = distance
                best_anchor = anchor
        
        return best_anchor


class ConnectionLine(ft.GestureDetector):
    """Visual line connecting two UML cards using ft.canvas."""
    
    def __init__(
        self,
        source_card: ft.Control,
        target_card: ft.Control,
        connection_type: str = "association",
        on_update: Optional[Callable] = None
    ):
        super().__init__()
        self.expand = True
        
        self.source_card = source_card
        self.target_card = target_card
        self.connection_type = connection_type
        self.on_update_callback = on_update
        
        # Line properties
        self.line_color = ft.Colors.BLUE_GREY_700
        self.line_width = 2
        
        # Create canvas for drawing
        self.canvas = ft.Canvas(expand=True)
        self.content = self.canvas
        
        self._draw_line()
    
    def _draw_line(self):
        """Draw the connection line between two cards using canvas."""
        # Get source position
        src_x = getattr(self.source_card, 'card_x', self.source_card.left)
        src_y = getattr(self.source_card, 'card_y', self.source_card.top)
        src_width = getattr(self.source_card, 'width', 160)
        src_height = getattr(self.source_card, 'height', 100)
        
        # Get target position
        tgt_x = getattr(self.target_card, 'card_x', self.target_card.left)
        tgt_y = getattr(self.target_card, 'card_y', self.target_card.top)
        tgt_width = getattr(self.target_card, 'width', 160)
        tgt_height = getattr(self.target_card, 'height', 100)
        
        # Find best anchor points
        src_anchor = AnchorPoint.find_best_anchor(src_x, src_y, src_width, src_height, 
                                                   tgt_x + tgt_width / 2, tgt_y + tgt_height / 2)
        tgt_anchor = AnchorPoint.find_best_anchor(tgt_x, tgt_y, tgt_width, tgt_height,
                                                   src_x + src_width / 2, src_y + src_height / 2)
        
        # Draw line on canvas
        path = ft.canvas.Path()
        path.move_to(src_anchor.x, src_anchor.y)
        path.line_to(tgt_anchor.x, tgt_anchor.y)
        
        self.canvas.shapes = [
            ft.canvas.Path(
                [path],
                paint=ft.Paint(
                    color=self.line_color,
                    stroke_width=self.line_width,
                    style=ft.PaintingStyle.STROKE,
                    stroke_cap=ft.StrokeCap.ROUND,
                ),
            )
        ]
    
    def update_line(self):
        """Update line position when cards move."""
        self._draw_line()
        if self.on_update_callback:
            self.on_update_callback(self)


class ConnectionManager:
    """Manages all connections in the diagram."""
    
    def __init__(self, canvas: ft.Stack):
        self.canvas = canvas
        self.connections: list[ConnectionLine] = []
        self._connection_lines: list[ConnectionLine] = []
    
    def add_connection(
        self,
        source_card: ft.Control,
        target_card: ft.Control,
        connection_type: str = "association"
    ) -> ConnectionLine:
        """Add a new connection between two cards."""
        line = ConnectionLine(source_card, target_card, connection_type)
        self.connections.append(line)
        self._connection_lines.append(line)
        self.canvas.controls.append(line)
        return line
    
    def remove_connection(self, line: ConnectionLine):
        """Remove a connection."""
        if line in self.connections:
            self.connections.remove(line)
            self._connection_lines.remove(line)
            if line in self.canvas.controls:
                self.canvas.controls.remove(line)
    
    def update_all_connections(self):
        """Update all connection lines (call when cards move)."""
        for line in self.connections:
            line.update_line()
    
    def clear_all(self):
        """Remove all connections."""
        for line in self._connection_lines:
            if line in self.canvas.controls:
                self.canvas.controls.remove(line)
        self.connections.clear()
        self._connection_lines.clear()


def get_anchor_positions(card_x: float, card_y: float, width: float = 160, height: float = 100) -> dict:
    """Get dictionary of anchor positions for a card."""
    return {
        'top': (card_x + width / 2, card_y),
        'bottom': (card_x + width / 2, card_y + height),
        'left': (card_x, card_y + height / 2),
        'right': (card_x + width, card_y + height / 2),
    }