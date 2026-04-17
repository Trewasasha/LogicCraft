"""LogicCraft UML Editor - инструмент для визуального проектирования UML диаграмм"""

__version__ = "1.0.0"
__author__ = "LogicCraft Team"

from .main import main
from .controllers.diagram_controller import DiagramController
from .view.main_window import MainWindow
from .models.diagram import UMLDiagram, UMLNode, UMLConnection

__all__ = [
    "main",
    "DiagramController",
    "MainWindow",
    "UMLDiagram",
    "UMLNode",
    "UMLConnection"
]