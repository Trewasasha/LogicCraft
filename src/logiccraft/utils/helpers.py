"""Вспомогательные функции"""

import os
import json
from pathlib import Path
from typing import Any, Dict, List


def ensure_dir(path: str) -> Path:
    """Создать директорию если не существует"""
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def format_visibility(visibility: str) -> str:
    """Форматировать видимость для отображения"""
    symbols = {
        "public": "+",
        "private": "-",
        "protected": "#"
    }
    return symbols.get(visibility, visibility)


def parse_attribute(attr_str: str) -> Dict[str, Any]:
    """Парсит строку атрибута"""
    visibility = "public"
    attr_str = attr_str.strip()

    if attr_str.startswith("+"):
        visibility = "public"
        attr_str = attr_str[1:]
    elif attr_str.startswith("-"):
        visibility = "private"
        attr_str = attr_str[1:]
    elif attr_str.startswith("#"):
        visibility = "protected"
        attr_str = attr_str[1:]

    if ":" in attr_str:
        name, type_str = attr_str.split(":", 1)
        name = name.strip()
        type_str = type_str.strip()
    else:
        name = attr_str
        type_str = "Any"

    return {
        "name": name,
        "type": type_str,
        "visibility": visibility
    }


def parse_method(method_str: str) -> Dict[str, Any]:
    """Парсит строку метода"""
    visibility = "public"
    method_str = method_str.strip()

    if method_str.startswith("+"):
        visibility = "public"
        method_str = method_str[1:]
    elif method_str.startswith("-"):
        visibility = "private"
        method_str = method_str[1:]
    elif method_str.startswith("#"):
        visibility = "protected"
        method_str = method_str[1:]

    if "(" in method_str and ")" in method_str:
        name_part = method_str[:method_str.index("(")]
        return_part = method_str[method_str.index(")")+1:]
        if return_part.startswith(":"):
            return_type = return_part[1:].strip()
        else:
            return_type = "void"

        # Парсим параметры
        params_str = method_str[method_str.index("(")+1:method_str.index(")")]
        params = []
        if params_str:
            for param in params_str.split(","):
                param = param.strip()
                if param:
                    if ":" in param:
                        param_name, param_type = param.split(":", 1)
                        params.append({
                            "name": param_name.strip(),
                            "type": param_type.strip()
                        })
                    else:
                        params.append({
                            "name": param,
                            "type": "Any"
                        })

        return {
            "name": name_part.strip(),
            "return_type": return_type,
            "visibility": visibility,
            "parameters": params
        }
    else:
        return {
            "name": method_str,
            "return_type": "void",
            "visibility": visibility,
            "parameters": []
        }