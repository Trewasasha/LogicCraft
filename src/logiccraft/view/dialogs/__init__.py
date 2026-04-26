"""Диалоговые окна"""

from .edit_class_dialog import EditClassDialog
from .connection_properties import ConnectionPropertiesDialog
from .code_generation_dialog import CodeGenerationDialog
from .project_export_dialog import ProjectExportDialog
from .welcome_dialog import WelcomeDialog

__all__ = [
    "EditClassDialog",
    "ConnectionPropertiesDialog",
    "CodeGenerationDialog",
    "ProjectExportDialog",
    "WelcomeDialog",
]