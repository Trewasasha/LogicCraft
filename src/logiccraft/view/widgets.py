import flet as ft
import time


class UMLCard(ft.GestureDetector):
    """UML Class Card widget with drag-and-drop support for Flet"""
    
    def __init__(self, x: float, y: float, name: str = "NewClass", 
                 attributes: list = None, methods: list = None,
                 on_select=None, on_move=None):
        super().__init__()
        
        self.card_x = x
        self.card_y = y
        self.card_name = name
        self.attributes = attributes or []
        self.methods = methods or []
        self.selected = False
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.card_start_x = 0
        self.card_start_y = 0
        
        self.on_select_callback = on_select
        self.on_move_callback = on_move
        
        # Throttling для оптимизации частоты обновления
        self._last_update_time = 0
        self._update_interval = 1/60  # 60 FPS максимум
        
        self.width = 160
        self.height = 100
        
        self._build_card()
        
        # Set absolute positioning for Stack
        self.left = self.card_x
        self.top = self.card_y
        
        self.on_pan_start = self._on_drag_start
        self.on_pan_update = self._on_drag_update
        self.on_pan_end = self._on_drag_end
        self.on_tap = self._on_tap
        
        self.mouse_cursor = ft.MouseCursor.MOVE
    
    def _build_card(self):
        """Build the visual representation of the card"""
        # Header with class name
        header = ft.Container(
            content=ft.Text(
                self.card_name,
                color=ft.Colors.WHITE,
                size=10,
                weight=ft.FontWeight.BOLD
            ),
            bgcolor=ft.Colors.BLUE_600,
            padding=ft.padding.symmetric(horizontal=10, vertical=8),
            border_radius=ft.border_radius.only(top_left=5, top_right=5)
        )
        
        # Attributes section
        attr_text = "\n".join(self.attributes) if self.attributes else ""
        attributes = ft.Container(
            content=ft.Text(
                attr_text,
                color=ft.Colors.BLACK,
                size=9,
                font_family="monospace"
            ),
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
            height=30 if self.attributes else 0
        )
        
        # Methods section
        method_text = "\n".join(self.methods) if self.methods else ""
        methods = ft.Container(
            content=ft.Text(
                method_text,
                color=ft.Colors.BLACK,
                size=9,
                font_family="monospace"
            ),
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
            height=30 if self.methods else 0
        )
        
        # Divider lines
        divider1 = ft.Divider(height=1, color=ft.Colors.BLUE_200) if self.attributes else ft.Container()
        divider2 = ft.Divider(height=1, color=ft.Colors.BLUE_200) if self.methods else ft.Container()
        
        # Main card container
        self.card_container = ft.Container(
            content=ft.Column(
                [
                    header,
                    divider1,
                    attributes,
                    divider2,
                    methods
                ],
                spacing=0,
                tight=True
            ),
            width=self.width,
            bgcolor=ft.Colors.BLUE_GREY_50,
            border_radius=5,
            border=ft.border.all(2, ft.Colors.BLUE_600 if not self.selected else ft.Colors.RED_600),
            shadow=ft.BoxShadow(
                blur_radius=5,
                color=ft.Colors.BLACK26,
                offset=ft.Offset(2, 2)
            )
        )
        
        self.content = self.card_container
    
    def _on_tap(self, e: ft.TapEvent):
        """Handle tap/click on card"""
        self.selected = not self.selected
        self._update_border()
        if self.on_select_callback:
            self.on_select_callback(self)
        self.update()
    
    def _on_drag_start(self, e: ft.DragStartEvent):
        """Start dragging"""
        self.dragging = True
        # Store initial position
        self.card_start_x = self.card_x
        self.card_start_y = self.card_y
        
        # Bring to front
        self.card_container.shadow = ft.BoxShadow(
            blur_radius=10,
            color=ft.Colors.BLACK45,
            offset=ft.Offset(4, 4)
        )
        self._update_border()
        self.update()
    
    def _on_drag_update(self, e: ft.DragUpdateEvent):
        """Update position while dragging (с throttling для оптимизации)"""
        if not self.dragging:
            return
        
        # Flet DragUpdateEvent provides local_position with current x, y
        current_x = e.local_position.x
        current_y = e.local_position.y
        
        # Update position relative to start
        self.card_x = max(0, self.card_start_x + current_x)
        self.card_y = max(0, self.card_start_y + current_y)
        
        # Apply position to visual container
        self.left = self.card_x
        self.top = self.card_y
        
        # Throttling: обновляем UI не чаще 60 FPS
        current_time = time.time()
        if current_time - self._last_update_time >= self._update_interval:
            self._last_update_time = current_time
            
            # Callback только при обновлении UI (реже)
            if self.on_move_callback:
                self.on_move_callback(self, self.card_x, self.card_y)
            
            self.update()
    
    def _on_drag_end(self, e: ft.DragEndEvent):
        """End dragging"""
        self.dragging = False
        
        # Restore shadow
        self.card_container.shadow = ft.BoxShadow(
            blur_radius=5,
            color=ft.Colors.BLACK26,
            offset=ft.Offset(2, 2)
        )
        self._update_border()
        self.update()
    
    def _update_border(self):
        """Update border color based on selection state"""
        color = ft.Colors.RED_600 if (self.selected or self.dragging) else ft.Colors.BLUE_600
        self.card_container.border = ft.border.all(3 if self.dragging else 2, color)
    
    def update_content(self, name: str = None, attributes: list = None, methods: list = None):
        """Update card content"""
        if name:
            self.card_name = name
        if attributes is not None:
            self.attributes = attributes
        if methods is not None:
            self.methods = methods
        self._build_card()
        self.update()
