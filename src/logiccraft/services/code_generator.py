"""Генерация кода из диаграммы"""
from typing import List, Dict, Optional
from ..models.diagram import UMLDiagram, UMLNode, UMLProperty, UMLMethod


class CodeGenerator:
    """Генератор кода на разных языках"""

    def __init__(self):
        self.language = "python"

    def generate(self, diagram: UMLDiagram, language: str = "python") -> str:
        """Сгенерировать код для диаграммы"""
        self.language = language

        if language == "python":
            return self._generate_python(diagram)
        elif language == "java":
            return self._generate_java(diagram)
        elif language == "javascript":
            return self._generate_javascript(diagram)
        else:
            raise ValueError(f"Unsupported language: {language}")

    def _generate_python(self, diagram: UMLDiagram) -> str:
        """Генерация Python кода"""
        lines = [
            f'"""Generated from UML Diagram: {diagram.name}"""',
            "from typing import List, Optional",
            "",
            ""
        ]

        for node in diagram.nodes:
            lines.extend(self._generate_python_class(node))
            lines.append("")

        return "\n".join(lines)

    def _generate_python_class(self, node: UMLNode) -> List[str]:
        """Генерация Python класса"""
        lines = []

        # Аннотация для абстрактного класса
        if node.is_abstract:
            lines.append("from abc import ABC, abstractmethod")
            lines.append("")
            class_line = f"class {node.name}(ABC):"
        else:
            class_line = f"class {node.name}:"

        lines.append(class_line)

        # Docstring
        if node.stereotype:
            lines.append(f'    """{node.stereotype}"""')
        else:
            lines.append('    """Class generated from UML diagram"""')

        # Атрибуты
        if node.properties:
            lines.append("")
            lines.append("    # Attributes")
            for prop in node.properties:
                visibility = self._get_python_visibility(prop.visibility)
                default = f" = {prop.default_value}" if prop.default_value else ""
                lines.append(f"    {visibility}{prop.name}: {prop.type}{default}")

        # Конструктор
        lines.append("")
        lines.append("    def __init__(self):")

        # Инициализация атрибутов в конструкторе
        for prop in node.properties:
            if prop.default_value:
                lines.append(f"        self.{prop.name} = {prop.default_value}")
            else:
                lines.append(f"        self.{prop.name} = None")

        # Методы
        if node.methods:
            lines.append("")
            lines.append("    # Methods")
            for method in node.methods:
                params = self._generate_method_params(method)
                return_type = method.return_type or "None"

                # Декораторы
                if method.is_abstract:
                    lines.append("    @abstractmethod")
                elif method.is_static:
                    lines.append("    @staticmethod")

                # Сигнатура метода
                if method.is_static:
                    signature = f"    def {method.name}({params}) -> {return_type}:"
                else:
                    signature = f"    def {method.name}(self{', ' + params if params else ''}) -> {return_type}:"

                lines.append(signature)

                # Тело метода
                if method.is_abstract:
                    lines.append("        raise NotImplementedError")
                else:
                    lines.append("        pass")

                lines.append("")

        return lines

    def _generate_method_params(self, method: UMLMethod) -> str:
        """Генерация параметров метода"""
        params = []
        for param in method.parameters:
            params.append(f"{param.name}: {param.type}")
        return ", ".join(params)

    def _get_python_visibility(self, visibility: str) -> str:
        """Преобразовать видимость в Python"""
        if visibility == "private":
            return "__"
        elif visibility == "protected":
            return "_"
        else:  # public
            return ""

    def _generate_java(self, diagram: UMLDiagram) -> str:
        """Генерация Java кода"""
        lines = []

        for node in diagram.nodes:
            lines.extend(self._generate_java_class(node))
            lines.append("")

        return "\n".join(lines)

    def _generate_java_class(self, node: UMLNode) -> List[str]:
        """Генерация Java класса"""
        lines = []

        # Модификаторы
        modifiers = []
        if node.is_abstract:
            modifiers.append("abstract")

        class_declaration = f"public {' '.join(modifiers)} class {node.name}"

        # Наследование
        inherits_from = []
        for conn in self._get_inheritance_connections(node):
            inherits_from.append(conn.target_id)

        if inherits_from:
            class_declaration += f" extends {inherits_from[0]}"

        lines.append(class_declaration + " {")

        # Атрибуты
        for prop in node.properties:
            visibility = self._get_java_visibility(prop.visibility)
            static_mod = " static" if prop.is_static else ""
            lines.append(f"    {visibility}{static_mod} {prop.type} {prop.name};")

        # Конструктор
        if node.properties:
            lines.append("")
            lines.append(f"    public {node.name}() {{")
            lines.append("        // TODO: Initialize attributes")
            lines.append("    }")

        # Методы
        for method in node.methods:
            lines.append("")
            visibility = self._get_java_visibility(method.visibility)
            abstract_mod = " abstract" if method.is_abstract else ""
            static_mod = " static" if method.is_static else ""

            params = []
            for param in method.parameters:
                params.append(f"{param.type} {param.name}")

            params_str = ", ".join(params)
            return_type = method.return_type or "void"

            signature = f"    {visibility}{abstract_mod}{static_mod} {return_type} {method.name}({params_str})"

            if method.is_abstract:
                lines.append(signature + ";")
            else:
                lines.append(signature + " {")
                lines.append("        // TODO: Implement method")
                lines.append("    }")

        lines.append("}")

        return lines

    def _get_java_visibility(self, visibility: str) -> str:
        """Преобразовать видимость в Java"""
        if visibility == "private":
            return "private"
        elif visibility == "protected":
            return "protected"
        else:  # public
            return "public"

    def _generate_javascript(self, diagram: UMLDiagram) -> str:
        """Генерация JavaScript кода"""
        lines = []

        for node in diagram.nodes:
            lines.extend(self._generate_javascript_class(node))
            lines.append("")

        return "\n".join(lines)

    def _generate_javascript_class(self, node: UMLNode) -> List[str]:
        """Генерация JavaScript класса (ES6)"""
        lines = []

        lines.append(f"class {node.name} {{")

        # Конструктор
        if node.properties:
            lines.append("    constructor() {")
            for prop in node.properties:
                lines.append(f"        this.{prop.name} = null;")
            lines.append("    }")

        # Методы
        for method in node.methods:
            lines.append("")
            params = []
            for param in method.parameters:
                params.append(param.name)

            params_str = ", ".join(params)
            lines.append(f"    {method.name}({params_str}) {{")

            if method.return_type and method.return_type != "void":
                lines.append("        // TODO: Implement method")
                lines.append(f"        return null; // Return type: {method.return_type}")
            else:
                lines.append("        // TODO: Implement method")

            lines.append("    }")

        lines.append("}")

        return lines

    def _get_inheritance_connections(self, node: UMLNode) -> List:
        """Получить связи наследования для узла"""
        # Этот метод будет вызываться из контроллера
        # Здесь нужно получать связи из диаграммы
        # В реальной реализации нужно передавать диаграмму
        return []