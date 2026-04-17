"""Виджеты для UML редактора"""

from .uml_card import UMLCard
from .connection_line import ConnectionLine
from .anchor_point import AnchorPoint
from .arrow_head import ArrowHead, ConnectionType

__all__ = [
    "UMLCard",
    "ConnectionLine",
    "AnchorPoint",
    "ArrowHead",
    "ConnectionType"
]