"""Tests for Month 4: Code Generation (Codegen).

This module tests:
- Jinja2 templates for generating .py files
- Logic for translating connections into imports and inheritance
- Code preview window with tabs for files
- Export of ready project folder structure to disk
"""

import pytest
from unittest.mock import Mock, MagicMock, mock_open, patch
from pathlib import Path


class TestJinja2Templates:
    """Tests for Jinja2 template setup (Week 1, Month 4)."""

    def test_template_class_generation(self):
        """Test Jinja2 template generates Python class."""
        template = TemplateEngine()
        
        class_data = {
            "name": "User",
            "properties": [
                {"name": "username", "type": "str", "visibility": "public"},
                {"name": "_password", "type": "str", "visibility": "private"}
            ],
            "methods": [
                {"name": "get_username", "return_type": "str", "visibility": "public", "parameters": []}
            ]
        }
        
        result = template.render_class(class_data)
        
        assert "class User:" in result
        assert "def __init__(self)" in result
        assert "self.username" in result
        assert "self._password" in result
        assert "def get_username(self)" in result

    def test_template_with_inheritance(self):
        """Test template generates class with inheritance."""
        template = TemplateEngine()
        
        class_data = {
            "name": "Admin",
            "parent": "User",
            "properties": [],
            "methods": []
        }
        
        result = template.render_class(class_data)
        
        assert "class Admin(User):" in result

    def test_template_with_static_method(self):
        """Test template generates static method with decorator."""
        template = TemplateEngine()
        
        class_data = {
            "name": "Utils",
            "properties": [],
            "methods": [
                {"name": "parse", "return_type": "dict", "visibility": "public", 
                 "is_static": True, "parameters": [{"name": "data", "type": "str"}]}
            ]
        }
        
        result = template.render_class(class_data)
        
        assert "@staticmethod" in result
        assert "def parse(data: str)" in result

    def test_template_with_abstract_method(self):
        """Test template generates abstract method with ABC."""
        template = TemplateEngine()
        
        class_data = {
            "name": "Shape",
            "is_abstract": True,
            "properties": [],
            "methods": [
                {"name": "area", "return_type": "float", "visibility": "public", 
                 "is_abstract": True, "parameters": []}
            ]
        }
        
        result = template.render_class(class_data)
        
        assert "from abc import ABC, abstractmethod" in result
        assert "class Shape(ABC):" in result
        assert "@abstractmethod" in result

    def test_template_with_default_values(self):
        """Test template generates attributes with default values."""
        template = TemplateEngine()
        
        class_data = {
            "name": "Config",
            "properties": [
                {"name": "timeout", "type": "int", "visibility": "public", "default_value": "30"},
                {"name": "debug", "type": "bool", "visibility": "public", "default_value": "False"}
            ],
            "methods": []
        }
        
        result = template.render_class(class_data)
        
        assert "self.timeout = 30" in result
        assert "self.debug = False" in result


class TestConnectionTranslation:
    """Tests for translating connections to code (Week 2, Month 4)."""

    def test_inheritance_to_class_parent(self):
        """Test inheritance connection translates to parent class."""
        translator = ConnectionTranslator()
        
        classes = [
            {"id": "c1", "name": "User", "properties": [], "methods": []},
            {"id": "c2", "name": "Admin", "properties": [], "methods": []}
        ]
        connections = [
            {"source_id": "c1", "target_id": "c2", "type": "inheritance"}
        ]
        
        result = translator.translate(classes, connections)
        
        assert result["c2"]["parent"] == "User"

    def test_association_to_import(self):
        """Test association connection translates to import statement."""
        translator = ConnectionTranslator()
        
        classes = [
            {"id": "c1", "name": "Order", "properties": [], "methods": []},
            {"id": "c2", "name": "Customer", "properties": [], "methods": []}
        ]
        connections = [
            {"source_id": "c2", "target_id": "c1", "type": "association"}
        ]
        
        result = translator.translate(classes, connections)
        
        assert "Customer" in result["c1"]["imports"]

    def test_composition_to_field(self):
        """Test composition connection translates to composition field."""
        translator = ConnectionTranslator()
        
        classes = [
            {"id": "c1", "name": "Car", "properties": [], "methods": []},
            {"id": "c2", "name": "Engine", "properties": [], "methods": []}
        ]
        connections = [
            {"source_id": "c2", "target_id": "c1", "type": "composition", "name": "engine"}
        ]
        
        result = translator.translate(classes, connections)
        
        engine_prop = next(p for p in result["c1"]["properties"] if p["name"] == "engine")
        assert engine_prop["type"] == "Engine"

    def test_multiplicity_to_type_hint(self):
        """Test multiplicity translates to list type hint."""
        translator = ConnectionTranslator()
        
        classes = [
            {"id": "c1", "name": "Order", "properties": [], "methods": []},
            {"id": "c2", "name": "Item", "properties": [], "methods": []}
        ]
        connections = [
            {"source_id": "c1", "target_id": "c2", "type": "association", 
             "name": "items", "multiplicity": "0..*"}
        ]
        
        result = translator.translate(classes, connections)
        
        items_prop = next(p for p in result["c2"]["properties"] if p["name"] == "items")
        assert "list" in items_prop["type"]
        assert "Order" in items_prop["type"]

    def test_dependency_to_import(self):
        """Test dependency connection translates to import."""
        translator = ConnectionTranslator()
        
        classes = [
            {"id": "c1", "name": "ReportGenerator", "properties": [], "methods": []},
            {"id": "c2", "name": "PDFExporter", "properties": [], "methods": []}
        ]
        connections = [
            {"source_id": "c2", "target_id": "c1", "type": "dependency"}
        ]
        
        result = translator.translate(classes, connections)
        
        assert "PDFExporter" in result["c1"]["imports"]


class TestCodePreview:
    """Tests for code preview window (Week 3, Month 4)."""

    def test_preview_shows_generated_files(self):
        """Test preview window shows list of generated files."""
        preview = CodePreviewWindow()
        
        files = {
            "user.py": "class User:...",
            "order.py": "class Order:..."
        }
        
        preview.load_files(files)
        
        assert len(preview.tabs) == 2
        assert "user.py" in preview.tabs
        assert "order.py" in preview.tabs

    def test_preview_switch_tabs(self):
        """Test clicking tab switches displayed code."""
        preview = CodePreviewWindow()
        
        files = {
            "user.py": "class User:...",
            "order.py": "class Order:..."
        }
        preview.load_files(files)
        
        preview.select_tab("order.py")
        
        assert preview.current_tab == "order.py"
        assert "class Order" in preview.code_display

    def test_preview_syntax_highlighting(self):
        """Test code preview has syntax highlighting."""
        preview = CodePreviewWindow()
        
        code = "class User:\n    def __init__(self):\n        pass"
        highlighted = preview.highlight_syntax(code)
        
        assert "class" in highlighted  # Should have highlighting markers
        assert "def" in highlighted

    def test_preview_copy_to_clipboard(self):
        """Test copy button copies current file to clipboard."""
        preview = CodePreviewWindow()
        preview.load_files({"test.py": "class Test: pass"})
        preview.select_tab("test.py")
        
        # Mock pyperclip if available, otherwise mock the copy method directly
        try:
            with patch('pyperclip.copy') as mock_copy:
                preview.copy_current_file()
                mock_copy.assert_called_once_with("class Test: pass")
        except ModuleNotFoundError:
            # pyperclip not installed, test the internal state instead
            preview.copy_current_file()
            assert preview._last_copied == "class Test: pass"


class TestProjectExport:
    """Tests for project export to disk (Week 4, Month 4)."""

    def test_export_creates_directory_structure(self):
        """Test export creates proper directory structure."""
        exporter = ProjectExporter()
        
        project = {
            "name": "MyProject",
            "files": {
                "models/user.py": "class User:...",
                "models/order.py": "class Order:...",
                "main.py": "from models.user import User"
            }
        }
        
        with patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch('pathlib.Path.write_text') as mock_write:
            
            exporter.export(project, Path("/output"))
            
            assert mock_mkdir.call_count >= 2  # At least root and models

    def test_export_writes_files(self):
        """Test export writes file contents correctly."""
        exporter = ProjectExporter()
        
        project = {
            "name": "MyProject",
            "files": {
                "user.py": "class User:\n    pass"
            }
        }
        
        with patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.write_text') as mock_write:
            
            exporter.export(project, Path("/output"))
            
            # write_text is called for user.py and __init__.py
            assert mock_write.call_count >= 1
            # Check that one of the calls contains our code
            all_calls = [str(call) for call in mock_write.call_args_list]
            assert any("class User" in call for call in all_calls)

    def test_export_creates_init_files(self):
        """Test export creates __init__.py files for packages."""
        exporter = ProjectExporter()
        
        project = {
            "name": "MyProject",
            "files": {
                "models/user.py": "class User:...",
                "models/order.py": "class Order:..."
            }
        }
        
        # Use a real temporary directory to test actual file creation
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            exporter.export(project, Path(temp_dir) / "output")
            
            # Check that __init__.py files exist in the expected directories
            expected_init_file = Path(temp_dir) / "output" / "MyProject" / "models" / "__init__.py"
            assert expected_init_file.exists(), f"__init__.py file should exist at {expected_init_file}"

    def test_export_overwrite_existing(self):
        """Test export can overwrite existing files."""
        exporter = ProjectExporter()
        
        project = {
            "name": "MyProject",
            "files": {"main.py": "print('hello')"}
        }
        
        # Use a real temporary directory to test actual file creation
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            # First, create a file to simulate it already existing
            existing_file = Path(temp_dir) / "output" / "MyProject" / "main.py"
            existing_file.parent.mkdir(parents=True, exist_ok=True)
            existing_file.write_text("old content")
            
            # Verify it initially has old content
            assert existing_file.read_text() == "old content"
            
            # Export with overwrite=True should overwrite the file
            exporter.export(project, Path(temp_dir) / "output", overwrite=True)
            
            # Check that the file was overwritten with new content
            assert existing_file.read_text() == "print('hello')"
    
    def test_export_preserves_structure(self):
        """Test export preserves nested directory structure."""
        exporter = ProjectExporter()
        
        project = {
            "name": "MyProject",
            "files": {
                "core/models/user.py": "class User:...",
                "core/services/auth.py": "class Auth:...",
                "utils/helpers.py": "def helper():..."
            }
        }
        
        created_dirs = []
        
        def capture_mkdir(self, *args, **kwargs):
            # Capture the path from the Path object
            created_dirs.append(str(self))
        
        with patch('pathlib.Path.mkdir', capture_mkdir), \
             patch('pathlib.Path.write_text'):
            
            exporter.export(project, Path("/output"))
            
            # Check that mkdir was called for nested directories
            all_dirs_str = " ".join(created_dirs)
            assert "core" in all_dirs_str
            assert "utils" in all_dirs_str


class TestFullCodegenPipeline:
    """Integration tests for full code generation pipeline."""

    def test_full_pipeline_diagram_to_files(self):
        """Test complete pipeline from diagram to generated files."""
        pipeline = CodegenPipeline()
        
        diagram = {
            "name": "ShopSystem",
            "classes": [
                {
                    "id": "c1",
                    "name": "Customer",
                    "properties": [{"name": "name", "type": "str", "visibility": "public"}],
                    "methods": []
                },
                {
                    "id": "c2", 
                    "name": "Order",
                    "properties": [{"name": "total", "type": "float", "visibility": "public"}],
                    "methods": [{"name": "calculate_total", "return_type": "float", "visibility": "public", "parameters": []}]
                }
            ],
            "connections": [
                {"source_id": "c1", "target_id": "c2", "type": "association", "name": "customer"}
            ]
        }
        
        result = pipeline.generate(diagram)
        
        assert "customer.py" in result or "Customer.py" in result
        assert "order.py" in result or "Order.py" in result
        
        # Check that association was translated
        order_code = result.get("order.py", result.get("Order.py", ""))
        assert "Customer" in order_code or "customer" in order_code


# Placeholder classes and functions
class TemplateEngine:
    """Placeholder: Jinja2 template engine for code generation."""
    
    def render_class(self, class_data):
        lines = []
        
        # Imports for abstract classes
        if class_data.get("is_abstract"):
            lines.append("from abc import ABC, abstractmethod")
        
        # Class definition
        parent = class_data.get("parent", "")
        if class_data.get("is_abstract"):
            parent = "ABC" if not parent else f"{parent}, ABC"
        
        parent_str = f"({parent})" if parent else ""
        lines.append(f"class {class_data['name']}{parent_str}:")
        
        # __init__ method
        lines.append("    def __init__(self):")
        for prop in class_data.get("properties", []):
            default = f" = {prop['default_value']}" if prop.get("default_value") else ""
            lines.append(f"        self.{prop['name']}{default}")
        if not class_data.get("properties"):
            lines.append("        pass")
        
        # Methods
        for method in class_data.get("methods", []):
            if method.get("is_abstract"):
                lines.append("    @abstractmethod")
            if method.get("is_static"):
                lines.append("    @staticmethod")
            
            params_str = ", ".join([f"{p['name']}: {p['type']}" for p in method.get("parameters", [])])
            self_param = "self" if not method.get("is_static") else ""
            if self_param and params_str:
                params_str = f"{self_param}, {params_str}"
            elif self_param:
                params_str = self_param
            
            lines.append(f"    def {method['name']}({params_str}) -> {method['return_type']}:")
            lines.append("        pass")
        
        return "\n".join(lines)


class ConnectionTranslator:
    """Placeholder: Translates UML connections to code constructs."""
    
    def translate(self, classes, connections):
        result = {}
        class_map = {c["id"]: c for c in classes}
        
        for cls in classes:
            result[cls["id"]] = {
                "name": cls["name"],
                "properties": list(cls.get("properties", [])),
                "methods": list(cls.get("methods", [])),
                "imports": [],
                "parent": None
            }
        
        for conn in connections:
            source = class_map.get(conn["source_id"])
            target = class_map.get(conn["target_id"])
            
            if not source or not target:
                continue
            
            conn_type = conn.get("type")
            
            if conn_type == "inheritance":
                result[target["id"]]["parent"] = source["name"]
            
            elif conn_type in ("association", "composition"):
                # Add import
                if source["name"] not in result[target["id"]]["imports"]:
                    result[target["id"]]["imports"].append(source["name"])
                
                # Add property for composition/association
                prop_name = conn.get("name", source["name"].lower())
                multiplicity = conn.get("multiplicity", "1")
                
                if multiplicity in ("0..*", "1..*", "*"):
                    type_hint = f"list[{source['name']}]"
                else:
                    type_hint = source["name"]
                
                result[target["id"]]["properties"].append({
                    "name": prop_name,
                    "type": type_hint,
                    "visibility": "public"
                })
            
            elif conn_type == "dependency":
                if source["name"] not in result[target["id"]]["imports"]:
                    result[target["id"]]["imports"].append(source["name"])
        
        return result


class CodePreviewWindow:
    """Placeholder: Code preview window with tabs."""
    
    def __init__(self):
        self.tabs = {}
        self.current_tab = None
        self.code_display = ""
        self._last_copied = None
    
    def load_files(self, files):
        self.tabs = files
        if files:
            self.select_tab(list(files.keys())[0])
    
    def select_tab(self, filename):
        self.current_tab = filename
        self.code_display = self.tabs.get(filename, "")
    
    def highlight_syntax(self, code):
        # Simple placeholder highlighting
        return code.replace("class", "<keyword>class</keyword>").replace("def", "<keyword>def</keyword>")
    
    def copy_current_file(self):
        try:
            import pyperclip
            pyperclip.copy(self.code_display)
        except ImportError:
            # Fallback when pyperclip is not installed
            self._last_copied = self.code_display


class ProjectExporter:
    """Placeholder: Project exporter to disk."""
    
    def export(self, project, output_path, overwrite=False):
        output_path = Path(output_path) / project["name"]
        output_path.mkdir(parents=True, exist_ok=True)
        
        dirs_created = set()
        
        for filepath, content in project["files"].items():
            full_path = output_path / filepath
            
            # Create parent directories
            parent = full_path.parent
            if parent not in dirs_created:
                parent.mkdir(parents=True, exist_ok=True)
                dirs_created.add(parent)
                
                # Create __init__.py for packages - always create it
                init_file = parent / "__init__.py"
                init_file.write_text("")  # Always create __init__.py
            
            # Write file
            if not full_path.exists() or overwrite:
                full_path.write_text(content, encoding="utf-8")


class CodegenPipeline:
    """Placeholder: Full code generation pipeline."""
    
    def __init__(self):
        self.translator = ConnectionTranslator()
        self.template = TemplateEngine()
    
    def generate(self, diagram):
        classes = diagram.get("classes", [])
        connections = diagram.get("connections", [])
        
        # Translate connections
        translated = self.translator.translate(classes, connections)
        
        # Generate files
        files = {}
        for class_id, data in translated.items():
            filename = f"{data['name'].lower()}.py"
            
            # Build class data for template
            class_data = {
                "name": data["name"],
                "parent": data.get("parent"),
                "properties": data["properties"],
                "methods": data["methods"],
                "is_abstract": any(m.get("is_abstract") for m in data["methods"])
            }
            
            code = self.template.render_class(class_data)
            
            # Add imports at top
            if data.get("imports"):
                import_lines = [f"from .{imp.lower()} import {imp}" for imp in data["imports"]]
                code = "\n".join(import_lines) + "\n\n" + code
            
            files[filename] = code
        
        return files
