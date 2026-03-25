"""Connection lines and anchors for UML diagrams."""

import flet as ft
from flet.canvas import Canvas, Line
import math
from typing import Callable, Optional, Tuple


class AnchorPoint:
    """Точки привязки на гранях карточки UML."""
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"

    @staticmethod
    def calculate_anchors(card_x: float, card_y: float, width: float, height: float) -> dict:
        return {
            "top": (card_x + width / 2, card_y),
            "bottom": (card_x + width / 2, card_y + height),
            "left": (card_x, card_y + height / 2),
            "right": (card_x + width, card_y + height / 2),
        }


class AnchorHandle(ft.GestureDetector):
    """Интерактивная ручка для изменения точки привязки линии."""

    def __init__(self, card: ft.Control, position: str, on_drag: Callable, size: int = 14):
        super().__init__()
        self.card = card
        self.position = position
        self.on_drag_callback = on_drag
        self.size = size

        self.handle = ft.Container(
            width=size,
            height=size,
            bgcolor=ft.Colors.RED_ACCENT,
            border_radius=ft.BorderRadius.all(size / 2),
            border=ft.border.all(2, ft.Colors.WHITE),
            visible=False,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.BLACK26)
        )
        self.content = self.handle
        self.on_pan_update = self._on_pan_update

    def update_position(self):
        """Синхронизация положения ручки с карточкой."""
        cw = getattr(self.card, "width", 160) or 160
        ch = getattr(self.card, "height", 100) or 100
        cx = getattr(self.card, "left", 0)
        cy = getattr(self.card, "top", 0)

        anchors = AnchorPoint.calculate_anchors(cx, cy, cw, ch)
        coords = anchors.get(self.position)
        if coords:
            self.left = coords[0] - self.size / 2
            self.top = coords[1] - self.size / 2
            if self.page:
                self.update()

    def _on_pan_update(self, e: ft.DragUpdateEvent):
        mx = getattr(e, "global_x", getattr(e, "gx", 0))
        my = getattr(e, "global_y", getattr(e, "gy", 0))
        if self.on_drag_callback:
            self.on_drag_callback(self, mx, my)


class ConnectionLine(ft.Stack):
    """Визуальная линия связи с умным определением клика."""

    def __init__(self, source_card: ft.Control, target_card: ft.Control):
        super().__init__()
        self.pick_self = False
        self.expand = True

        self.source_card = source_card
        self.target_card = target_card
        self.source_pos = "right"
        self.target_pos = "left"
        self.is_selected = False

        self.canvas = Canvas(expand=True)

        # Убрали mouse_cursor, чтобы избежать AttributeError
        self.click_detector = ft.GestureDetector(
            on_tap=self._on_maybe_tap_line,
            expand=True
        )

        self.source_handle = AnchorHandle(source_card, self.source_pos, self._on_source_drag)
        self.target_handle = AnchorHandle(target_card, self.target_pos, self._on_target_drag)

        self.controls = [self.canvas, self.click_detector, self.source_handle, self.target_handle]

    def _on_maybe_tap_line(self, e: ft.TapEvent):
        """Проверка попадания по линии."""
        lx = getattr(e, "local_x", getattr(e, "lx", None))
        ly = getattr(e, "local_y", getattr(e, "ly", None))

        if lx is None or ly is None:
            return

        p1 = self._get_coords(self.source_card, self.source_pos)
        p2 = self._get_coords(self.target_card, self.target_pos)

        dist = self._dist_to_line(lx, ly, p1[0], p1[1], p2[0], p2[1])

        if dist < 20:
            self._toggle_edit_mode()
        elif self.is_selected:
            self._toggle_edit_mode()

    def _dist_to_line(self, px, py, x1, y1, x2, y2):
        l2 = (x1 - x2)**2 + (y1 - y2)**2
        if l2 == 0: return math.sqrt((px - x1)**2 + (py - y1)**2)
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / l2))
        return math.sqrt((px - (x1 + t * (x2 - x1)))**2 + (py - (y1 + t * (y2 - y1)))**2)

    def _get_coords(self, card, pos):
        cw = getattr(card, "width", 160) or 160
        ch = getattr(card, "height", 100) or 100
        cx = getattr(card, "left", 0)
        cy = getattr(card, "top", 0)
        return AnchorPoint.calculate_anchors(cx, cy, cw, ch)[pos]

    def _toggle_edit_mode(self):
        self.is_selected = not self.is_selected
        self.source_handle.handle.visible = self.is_selected
        self.target_handle.handle.visible = self.is_selected
        self.update_line()
        if self.page:
            self.update()

    def _on_source_drag(self, handle, mx, my):
        self.source_pos = self._find_nearest(self.source_card, mx, my)
        self.update_line()

    def _on_target_drag(self, handle, mx, my):
        self.target_pos = self._find_nearest(self.target_card, mx, my)
        self.update_line()

    def _find_nearest(self, card, mx, my) -> str:
        cw = getattr(card, "width", 160) or 160
        ch = getattr(card, "height", 100) or 100
        cx = getattr(card, "left", 0)
        cy = getattr(card, "top", 0)
        anchors = AnchorPoint.calculate_anchors(cx, cy, cw, ch)

        best_name = "top"
        min_dist = float("inf")
        for name, (ax, ay) in anchors.items():
            dist = math.sqrt((ax - mx)**2 + (ay - my)**2)
            if dist < min_dist:
                min_dist, best_name = dist, name
        return best_name

    def update_line(self):
        p1 = self._get_coords(self.source_card, self.source_pos)
        p2 = self._get_coords(self.target_card, self.target_pos)

        self.source_handle.position = self.source_pos
        self.target_handle.position = self.target_pos
        self.source_handle.update_position()
        self.target_handle.update_position()

        color = ft.Colors.BLUE_ACCENT if self.is_selected else ft.Colors.BLUE_GREY_400
        width = 3 if self.is_selected else 2

        self.canvas.shapes = [
            Line(p1[0], p1[1], p2[0], p2[1], paint=ft.Paint(color=color, stroke_width=width))
        ]
        if self.canvas.page:
            self.canvas.update()


class ConnectionManager:
    def __init__(self, canvas_stack: ft.Stack):
        self.canvas_stack = canvas_stack
        self.connections: list[ConnectionLine] = []

    def add_connection(self, source, target, c_type="association"):
        line = ConnectionLine(source, target)
        self.canvas_stack.controls.insert(0, line)
        self.canvas_stack.update()
        line.update_line()
        self.connections.append(line)
        return line

    def update_all_connections(self):
        for conn in self.connections:
            conn.update_line()