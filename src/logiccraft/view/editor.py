import flet as ft
from pathlib import Path
from logiccraft.view.widgets import UMLCard
from logiccraft.view.connections import ConnectionManager, ConnectionLine
from logiccraft.utils.diagram_io import save_diagram, load_diagram
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
        
        # Connection mode
        self._connecting = False
        self._connection_source = None
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the editor UI"""
        # File picker for save/load
        self.file_picker = ft.FilePicker(
            on_result=self._on_file_picked
        )
        
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
                        "💾 Save",
                        on_click=self._save_diagram,
                        bgcolor=ft.Colors.GREEN_600,
                        color=ft.Colors.WHITE
                    ),
                    ft.ElevatedButton(
                        "📂 Load",
                        on_click=self._load_diagram,
                        bgcolor=ft.Colors.ORANGE_600,
                        color=ft.Colors.WHITE
                    ),
                    ft.ElevatedButton(
                        "🔗 Connect",
                        on_click=self._toggle_connect_mode,
                        bgcolor=ft.Colors.PURPLE_600,
                        color=ft.Colors.WHITE
                    ),
                    ft.ElevatedButton(
                        "🗑️ Clear All",
                        on_click=self._clear_all,
                        bgcolor=ft.Colors.RED_600,
                        color=ft.Colors.WHITE
                    ),
                    ft.Text("Cards: 0 | Mode: select", ref=ft.Ref())
                ],
                spacing=10
            ),
            padding=10,
            bgcolor=ft.Colors.BLUE_GREY_100
        )
        
        # Canvas area with connections
        self.canvas_stack = ft.Stack(
            [],
            expand=True
        )
        self.connection_manager = ConnectionManager(self.canvas_stack)
        
        self.canvas = ft.GestureDetector(
            content=self.canvas_stack,
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
            ),
            self.file_picker
        ]
        
        # Track file picker mode
        self._file_picker_mode = None  # 'save' or 'load'
    
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
        self.canvas_stack.controls.append(card)
        self.card_counter += 1
        
        self._update_counter()
        self.update()
    
    def _clear_all(self, e=None):
        """Remove all cards from canvas"""
        self.cards.clear()
        self.canvas_stack.controls.clear()
        self.connection_manager.clear_all()
        self.card_counter = 0
        self.selected_card = None
        self._connecting = False
        self._connection_source = None
        self._update_counter()
        self.update()
    
    def _on_card_select(self, card: UMLCard):
        """Handle card selection or connection"""
        # Connection mode
        if self._connecting:
            if self._connection_source is None:
                # First card selected - set as source
                self._connection_source = card
                print(f"Connection source: {card.card_name}")
            elif self._connection_source != card:
                # Second card selected - create connection
                self.connection_manager.add_connection(
                    self._connection_source, 
                    card, 
                    "association"
                )
                print(f"Connected {self._connection_source.card_name} -> {card.card_name}")
                # Reset connection mode
                self._connecting = False
                self._connection_source = None
                self._update_mode_text()
            return
        
        # Normal selection mode
        # Deselect previous
        if self.selected_card and self.selected_card != card:
            self.selected_card.selected = False
            self.selected_card._update_border()
            self.selected_card.update()
        
        self.selected_card = card if card.selected else None
        print(f"Selected: {card.card_name if card.selected else 'None'}")
    
    def _on_card_move(self, card: UMLCard, x: float, y: float):
        """Handle card movement"""
        # Update all connection lines when card moves
        self.connection_manager.update_all_connections()
        self.update()
        print(f"Moved {card.card_name} to ({x:.0f}, {y:.0f})")
    
    def _toggle_connect_mode(self, e=None):
        """Toggle connection mode"""
        self._connecting = not self._connecting
        self._connection_source = None
        self._update_mode_text()
        mode = "connect" if self._connecting else "select"
        print(f"Mode: {mode}")
    
    def _update_mode_text(self):
        """Update toolbar text with current mode"""
        for control in self.toolbar.content.controls:
            if isinstance(control, ft.Text):
                mode = "connect" if self._connecting else "select"
                control.value = f"Cards: {len(self.cards)} | Mode: {mode}"
                break
        self.update()
    
    def _save_diagram(self, e=None):
        """Open save dialog"""
        self._file_picker_mode = 'save'
        self.file_picker.save_file(
            dialog_title="Save Diagram",
            file_name="diagram.json",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["json"]
        )
    
    def _load_diagram(self, e=None):
        """Open load dialog"""
        self._file_picker_mode = 'load'
        self.file_picker.pick_files(
            dialog_title="Load Diagram",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["json"],
            allow_multiple=False
        )
    
    def _on_file_picked(self, e: ft.FilePickerResultEvent):
        """Handle file picker result"""
        if not e.path and not e.files:
            return
        
        if self._file_picker_mode == 'save':
            # Save diagram
            filepath = e.path
            if not filepath.endswith('.json'):
                filepath += '.json'
            try:
                save_diagram(self.cards, filepath)
                print(f"Diagram saved to {filepath}")
            except Exception as ex:
                print(f"Error saving diagram: {ex}")
        
        elif self._file_picker_mode == 'load':
            # Load diagram
            if e.files:
                filepath = e.files[0].path
                try:
                    self._clear_all()
                    loaded_cards, diagram_name = load_diagram(
                        filepath,
                        on_select=self._on_card_select,
                        on_move=self._on_card_move
                    )
                    for card in loaded_cards:
                        self.cards.append(card)
                        self.canvas.content.controls.append(card)
                    self.card_counter = len(self.cards)
                    self._update_counter()
                    self.update()
                    print(f"Diagram '{diagram_name}' loaded from {filepath}")
                except Exception as ex:
                    print(f"Error loading diagram: {ex}")
    
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
        self._update_mode_text()