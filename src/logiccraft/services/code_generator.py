"""Генерация кода из диаграммы"""
from typing import List, Dict, Optional
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, ChoiceLoader
from ..models.diagram import UMLDiagram, UMLNode, UMLProperty, UMLMethod, NodeType
from ..templates.config import get_language_config, get_supported_languages, map_type

class CodeGenerator:
    """Генератор кода на разных языках"""
    def __init__(self):
        self.language = "python"
        templates_dir = Path(__file__).parent.parent / "templates"
        user_templates_dir = Path.home() / ".logiccraft" / "templates"
        user_templates_dir.mkdir(parents=True, exist_ok=True)

        self.env = Environment(
            loader=ChoiceLoader([
                FileSystemLoader(user_templates_dir),
                FileSystemLoader(templates_dir)
            ]),
            trim_blocks=True,
            lstrip_blocks=True
        )

        self.env.globals.update({
            'get_python_visibility': self._get_python_visibility,
            'get_java_visibility': self._get_java_visibility,
            'generate_method_params': self._generate_method_params,
        })

    def generate(self, diagram: UMLDiagram, language: str = "python", custom_template: str = None) -> str:
        if language not in get_supported_languages():
            raise ValueError(f"Unsupported language: {language}. Supported: {get_supported_languages()}")

        self.language = language
        config = get_language_config(language)

        if custom_template:
            try:
                template = self.env.get_template(f"{custom_template}.j2")
            except Exception:
                template = self.env.get_template(config["template"])
        else:
            template = self.env.get_template(config["template"])

        inheritance_map = self._build_inheritance_map(diagram)

        has_abstract_classes = any(node.is_abstract or node.node_type.value == 'abstract_class' for node in diagram.nodes)
        has_interfaces = any(node.node_type.value == 'interface' for node in diagram.nodes)
        has_enums = any(node.node_type.value == 'enum' for node in diagram.nodes)

        return template.render(
            diagram_name=diagram.name,
            nodes=diagram.nodes,
            inheritance_map=inheritance_map,
            has_abstract_classes=has_abstract_classes,
            has_interfaces=has_interfaces,
            has_enums=has_enums,
            language=language
        )

    def generate_files(self, diagram: UMLDiagram, language: str = "python") -> Dict[str, str]:
        if language not in get_supported_languages():
            raise ValueError(f"Unsupported language: {language}. Supported: {get_supported_languages()}")

        files = {}
        config = get_language_config(language)

        for node in diagram.nodes:
            filename = f"{node.name}{config['extension']}"
            content = self._generate_single_class(node, diagram, language)
            files[filename] = content

        return files

    def get_supported_languages(self) -> List[str]:
        return get_supported_languages()

    def _generate_single_class(self, node: UMLNode, diagram: UMLDiagram, language: str) -> str:
        config = get_language_config(language)
        template = self.env.get_template(config["template"])
        inheritance_map = self._build_inheritance_map(diagram)

        return template.render(
            diagram_name=diagram.name,
            nodes=[node],
            inheritance_map=inheritance_map,
            has_abstract_classes=node.is_abstract,
            language=language
        )

    def _build_inheritance_map(self, diagram: UMLDiagram) -> Dict[str, List[str]]:
        inheritance_map = {}
        for node in diagram.nodes:
            inheritance_map[node.name] = []

        if hasattr(diagram, 'connections'):
            for connection in diagram.connections:
                if connection.type.value == "inheritance":
                    source_node = next((n for n in diagram.nodes if n.id == connection.source_id), None)
                    target_node = next((n for n in diagram.nodes if n.id == connection.target_id), None)
                    if source_node and target_node:
                        inheritance_map[source_node.name].append(target_node.name)

        return inheritance_map

    def _generate_method_params(self, method: UMLMethod) -> str:
        params = []
        for param in method.parameters:
            params.append(f"{param.name}: {param.type}")
        return ", ".join(params)

    def _get_python_visibility(self, visibility: str) -> str:
        if visibility == "private":
            return "__"
        elif visibility == "protected":
            return "_"
        else:
            return ""

    def _get_java_visibility(self, visibility: str) -> str:
        if visibility == "private":
            return "private"
        elif visibility == "protected":
            return "protected"
        else:
            return "public"