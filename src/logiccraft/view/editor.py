import flet as ft
from logiccraft.view.widgets import UMLCard
import random


class DiagramEditor(ft.Column):
    """Main diagram editor with toolbar and canvas"""
    
    def __init__(self):
        super().__init__()
        self.expand = True
        self.spacing = 0
        
        self.cards = []
        self.selected_card = None
        self.card_counter = 0
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the editor UI"""
        # Toolbar
        self.toolbar = ft.Container(
            content=ft.Row(
                [
                    ft.ElevatedButton(
                        "➕ Add Class",
                        on_click=self._add_card,
                        bgcolor=ft.Colors.BLUE_600,
                        color=ft.Colors.WHITE
                    ),
                    ft.ElevatedButton(
                        "🗑️ Clear All",
                        on_click=self._clear_all,
                        bgcolor=ft.Colors.RED_600,
                        color=ft.Colors.WHITE
                    ),
                    ft.Text("Cards: 0", ref=ft.Ref())
                ],
                spacing=10
            ),
            padding=10,
            bgcolor=ft.Colors.BLUE_GREY_100
        )
        
        # Canvas area
        self.canvas = ft.GestureDetector(
            content=ft.Stack(
                [],
                expand=True
            ),
            on_tap_down=self._on_canvas_tap,
            mouse_cursor=ft.MouseCursor.PRECISE
        )
        
        self.controls = [
            self.toolbar,
            ft.Divider(height=1, color=ft.Colors.BLUE_GREY_300),
            ft.Container(
                content=self.canvas,
                expand=True,
                bgcolor=ft.Colors.BLUE_GREY_50
            )
        ]
    
    def _add_card(self, e=None):
        """Add a new UML card to the canvas"""
        x = random.randint(50, 400)
        y = random.randint(50, 300)
        
        card = UMLCard(
            x=x,
            y=y,
            name=f"Class{self.card_counter}",
            attributes=["+ name: str", "- id: int"],
            methods=["+ getName(): str"],
            on_select=self._on_card_select,
            on_move=self._on_card_move
        )
        
        self.cards.append(card)
        self.canvas.content.controls.append(card)
        self.card_counter += 1
        
        self._update_counter()
        self.update()
    
    def _clear_all(self, e=None):
        """Remove all cards from canvas"""
        self.cards.clear()
        self.canvas.content.controls.clear()
        self.card_counter = 0
        self.selected_card = None
        self._update_counter()
        self.update()
    
    def _on_card_select(self, card: UMLCard):
        """Handle card selection"""
        # Deselect previous
        if self.selected_card and self.selected_card != card:
            self.selected_card.selected = False
            self.selected_card._update_border()
            self.selected_card.update()
        
        self.selected_card = card if card.selected else None
        print(f"Selected: {card.card_name if card.selected else 'None'}")
    
    def _on_card_move(self, card: UMLCard, x: float, y: float):
        """Handle card movement"""
        print(f"Moved {card.card_name} to ({x:.0f}, {y:.0f})")
    
    def _on_canvas_tap(self, e: ft.TapEvent):
        """Handle canvas click - deselect all"""
        # Deselect all cards when clicking on empty canvas
        for card in self.cards:
            if card.selected:
                card.selected = False
                card._update_border()
                card.update()
        self.selected_card = None
        self.update()
    
    def _update_counter(self):
        """Update the card counter display"""
        # Update counter text in toolbar
        for control in self.toolbar.content.controls:
            if isinstance(control, ft.Text):
                control.value = f"Cards: {len(self.cards)}"
                break