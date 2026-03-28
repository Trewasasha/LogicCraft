"""View layer for LogicCraft UML Editor"""

from .main_window import MainWindow, DiagramView
from .widgets.uml_card import UMLCard
from .widgets.connection_line import ConnectionLine
from .widgets.anchor_point import AnchorPoint
from .widgets.arrow_head import ArrowHead, ConnectionType
from .scenes.diagram_scene import DiagramScene
from .dialogs.edit_class_dialog import EditClassDialog
from .dialogs.connection_properties import ConnectionPropertiesDialog

__all__ = [
    "MainWindow",
    "DiagramView",
    "UMLCard",
    "ConnectionLine",
    "AnchorPoint",
    "ArrowHead",
    "ConnectionType",
    "DiagramScene",
    "EditClassDialog",
    "ConnectionPropertiesDialog"
]