"""Конфигурация шаблонов для генерации кода"""

from typing import Dict, Any

# Настройки для разных языков программирования
LANGUAGE_CONFIGS = {
    "python": {
        "extension": ".py",
        "template": "python_class.j2",
        "type_mappings": {
            "string": "str",
            "integer": "int", 
            "boolean": "bool",
            "float": "float",
            "list": "List",
            "dict": "Dict"
        },
        "default_values": {
            "str": '""',
            "int": "0",
            "bool": "False",
            "float": "0.0",
            "List": "[]",
            "Dict": "{}"
        }
    },
    
    "java": {
        "extension": ".java",
        "template": "java_class.j2", 
        "type_mappings": {
            "string": "String",
            "integer": "int",
            "boolean": "boolean", 
            "float": "double",
            "list": "List<Object>",
            "dict": "Map<String, Object>"
        },
        "default_values": {
            "String": '""',
            "int": "0",
            "boolean": "false",
            "double": "0.0",
            "List<Object>": "new ArrayList<>()",
            "Map<String, Object>": "new HashMap<>()"
        }
    },
    
    "javascript": {
        "extension": ".js",
        "template": "javascript_class.j2",
        "type_mappings": {
            "string": "string",
            "integer": "number",
            "boolean": "boolean",
            "float": "number", 
            "list": "Array",
            "dict": "Object"
        },
        "default_values": {
            "string": '""',
            "number": "0",
            "boolean": "false",
            "Array": "[]",
            "Object": "{}"
        }
    },
    
    "typescript": {
        "extension": ".ts",
        "template": "typescript_class.j2",
        "type_mappings": {
            "string": "string",
            "integer": "number", 
            "boolean": "boolean",
            "float": "number",
            "list": "Array<any>",
            "dict": "Record<string, any>"
        },
        "default_values": {
            "string": '""',
            "number": "0", 
            "boolean": "false",
            "Array<any>": "[]",
            "Record<string, any>": "{}"
        }
    },
    
    "csharp": {
        "extension": ".cs",
        "template": "csharp_class.j2",
        "type_mappings": {
            "string": "string",
            "integer": "int",
            "boolean": "bool",
            "float": "double",
            "list": "List<object>",
            "dict": "Dictionary<string, object>"
        },
        "default_values": {
            "string": '""',
            "int": "0",
            "bool": "false", 
            "double": "0.0",
            "List<object>": "new List<object>()",
            "Dictionary<string, object>": "new Dictionary<string, object>()"
        }
    }
}

# Настройки стилей кода
CODE_STYLES = {
    "indentation": {
        "python": "    ",  # 4 пробела
        "java": "    ",    # 4 пробела
        "javascript": "  ", # 2 пробела
        "typescript": "  ", # 2 пробела
        "csharp": "    "   # 4 пробела
    },
    
    "naming_conventions": {
        "python": {
            "class": "PascalCase",
            "method": "snake_case", 
            "property": "snake_case",
            "constant": "UPPER_SNAKE_CASE"
        },
        "java": {
            "class": "PascalCase",
            "method": "camelCase",
            "property": "camelCase", 
            "constant": "UPPER_SNAKE_CASE"
        },
        "javascript": {
            "class": "PascalCase",
            "method": "camelCase",
            "property": "camelCase",
            "constant": "UPPER_SNAKE_CASE"
        },
        "typescript": {
            "class": "PascalCase", 
            "method": "camelCase",
            "property": "camelCase",
            "constant": "UPPER_SNAKE_CASE"
        },
        "csharp": {
            "class": "PascalCase",
            "method": "PascalCase",
            "property": "PascalCase",
            "constant": "PascalCase"
        }
    }
}

def get_language_config(language: str) -> Dict[str, Any]:
    """Получить конфигурацию для языка"""
    return LANGUAGE_CONFIGS.get(language, LANGUAGE_CONFIGS["python"])

def get_supported_languages() -> list[str]:
    """Получить список поддерживаемых языков"""
    return list(LANGUAGE_CONFIGS.keys())

def map_type(original_type: str, target_language: str) -> str:
    """Преобразовать тип из UML в тип целевого языка"""
    config = get_language_config(target_language)
    return config["type_mappings"].get(original_type.lower(), original_type)

def get_default_value(type_name: str, target_language: str) -> str:
    """Получить значение по умолчанию для типа"""
    config = get_language_config(target_language)
    return config["default_values"].get(type_name, "null")