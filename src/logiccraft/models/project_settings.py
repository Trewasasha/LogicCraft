"""Модели настроек проекта для экспорта"""

import re
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import json


@dataclass
class CodeStyleSettings:
    """Настройки стиля кода"""
    indentation: str = "    "  # 4 пробела по умолчанию
    naming_convention: Dict[str, str] = field(default_factory=lambda: {
        "class": "PascalCase",
        "method": "camelCase", 
        "variable": "camelCase",
        "constant": "UPPER_CASE"
    })
    include_constructors: bool = True
    include_getters_setters: bool = False
    include_docstrings: bool = True
    include_type_hints: bool = True
    max_line_length: int = 88

    def validate(self) -> List[str]:
        """Валидация настроек стиля кода"""
        errors = []
        
        # Проверка отступов
        if not self.indentation or len(self.indentation) == 0:
            errors.append("Indentation cannot be empty")
        
        # Проверка длины строки
        if self.max_line_length < 50 or self.max_line_length > 200:
            errors.append("Max line length must be between 50 and 200")
            
        # Проверка соглашений именования
        valid_conventions = {"camelCase", "snake_case", "PascalCase", "UPPER_CASE"}
        for element, convention in self.naming_convention.items():
            if convention not in valid_conventions:
                errors.append(f"Invalid naming convention '{convention}' for {element}")
                
        return errors

    def apply_language_defaults(self, language: str):
        """Применение настроек по умолчанию для языка"""
        if language == "python":
            self.naming_convention = {
                "class": "PascalCase",
                "method": "snake_case",
                "variable": "snake_case", 
                "constant": "UPPER_CASE",
                "property": "snake_case",
                "parameter": "snake_case"
            }
            self.indentation = "    "  # 4 spaces for Python (PEP 8)
            self.max_line_length = 88  # Black formatter default
            self.include_type_hints = True
            self.include_docstrings = True
        elif language in ["java", "csharp"]:
            self.naming_convention = {
                "class": "PascalCase",
                "method": "camelCase",
                "variable": "camelCase",
                "constant": "UPPER_CASE",
                "property": "PascalCase",
                "parameter": "camelCase"
            }
            self.indentation = "    "  # 4 spaces for Java/C#
            self.max_line_length = 120 if language == "csharp" else 100
            self.include_type_hints = False
            self.include_docstrings = True
        elif language in ["javascript", "typescript"]:
            self.naming_convention = {
                "class": "PascalCase", 
                "method": "camelCase",
                "variable": "camelCase",
                "constant": "UPPER_CASE",
                "property": "camelCase",
                "parameter": "camelCase"
            }
            self.indentation = "  "  # 2 spaces for JS/TS (common convention)
            self.max_line_length = 100
            self.include_type_hints = language == "typescript"
            self.include_docstrings = True

    def get_indentation_type(self) -> str:
        """Получение типа отступа (spaces или tabs)"""
        if self.indentation.startswith('\t'):
            return "tabs"
        else:
            return "spaces"
    
    def get_indentation_size(self) -> int:
        """Получение размера отступа"""
        if self.indentation.startswith('\t'):
            return 1  # One tab
        else:
            return len(self.indentation)
    
    def set_indentation(self, indent_type: str, size: int = 4):
        """Установка отступа по типу и размеру"""
        if indent_type == "tabs":
            self.indentation = "\t"
        elif indent_type == "spaces":
            self.indentation = " " * size
        else:
            raise ValueError("indent_type must be 'tabs' or 'spaces'")
    
    def get_naming_convention_for_element(self, element_type: str) -> str:
        """Получение соглашения именования для конкретного элемента"""
        return self.naming_convention.get(element_type, "camelCase")
    
    def set_naming_convention_for_element(self, element_type: str, convention: str):
        """Установка соглашения именования для конкретного элемента"""
        valid_conventions = {"camelCase", "snake_case", "PascalCase", "UPPER_CASE"}
        if convention not in valid_conventions:
            raise ValueError(f"Invalid naming convention: {convention}")
        self.naming_convention[element_type] = convention
    
    def get_supported_languages(self) -> List[str]:
        """Получение списка поддерживаемых языков"""
        return ["python", "java", "csharp", "javascript", "typescript"]
    
    def is_language_supported(self, language: str) -> bool:
        """Проверка поддержки языка"""
        return language in self.get_supported_languages()
    
    def get_language_specific_settings(self, language: str) -> Dict[str, Any]:
        """Получение настроек по умолчанию для языка без их применения"""
        if not self.is_language_supported(language):
            raise ValueError(f"Unsupported language: {language}")
        
        # Create a temporary instance to get defaults
        temp_settings = CodeStyleSettings()
        temp_settings.apply_language_defaults(language)
        
        return {
            "naming_convention": temp_settings.naming_convention.copy(),
            "indentation": temp_settings.indentation,
            "max_line_length": temp_settings.max_line_length,
            "include_type_hints": temp_settings.include_type_hints,
            "include_docstrings": temp_settings.include_docstrings
        }


@dataclass
class ProjectSettings:
    """Настройки проекта для экспорта"""
    # Основные настройки
    name: str
    language: str
    structure_type: str  # "simple", "mvc", "layered", "clean_architecture"
    framework: Optional[str] = None  # "django", "spring", "express", "react"
    
    # Метаданные
    author: str = ""
    description: str = ""
    version: str = "1.0.0"
    license: Optional[str] = None
    
    # Настройки генерации
    package_manager: Optional[str] = None
    code_style: CodeStyleSettings = field(default_factory=CodeStyleSettings)
    
    # Дополнительные компоненты
    include_tests: bool = False
    include_docs: bool = False
    include_config: bool = True
    include_gitignore: bool = True
    include_readme: bool = True
    include_license: bool = False
    include_ci: bool = False
    
    # Настройки экспорта
    export_path: str = ""
    overwrite_existing: bool = False

    def __post_init__(self):
        """Пост-инициализация для применения настроек по умолчанию"""
        # Применяем настройки стиля по умолчанию для языка
        self.code_style.apply_language_defaults(self.language)
        
        # Устанавливаем пакетный менеджер по умолчанию если не указан
        if not self.package_manager:
            self.package_manager = self._get_default_package_manager()

    def validate(self) -> List[str]:
        """Валидация настроек проекта"""
        errors = []
        
        # Валидация имени проекта
        if not self.name or not self.name.strip():
            errors.append("Project name cannot be empty")
        elif not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', self.name):
            errors.append("Project name must start with a letter and contain only letters, numbers, hyphens, and underscores")
        elif len(self.name) > 50:
            errors.append("Project name cannot exceed 50 characters")
            
        # Валидация языка
        supported_languages = {"python", "java", "javascript", "typescript", "csharp"}
        if self.language not in supported_languages:
            errors.append(f"Unsupported language: {self.language}. Supported: {', '.join(supported_languages)}")
            
        # Валидация типа структуры
        supported_structures = {"simple", "mvc", "layered", "clean_architecture"}
        if self.structure_type not in supported_structures:
            errors.append(f"Unsupported structure type: {self.structure_type}. Supported: {', '.join(supported_structures)}")
            
        # Валидация фреймворка
        if self.framework:
            valid_frameworks = self._get_valid_frameworks_for_language()
            if self.framework not in valid_frameworks:
                errors.append(f"Framework '{self.framework}' is not supported for {self.language}")
                
        # Валидация пакетного менеджера
        if self.package_manager:
            valid_managers = self._get_valid_package_managers_for_language()
            if self.package_manager not in valid_managers:
                errors.append(f"Package manager '{self.package_manager}' is not supported for {self.language}")
                
        # Валидация версии
        if not re.match(r'^\d+\.\d+\.\d+(-\w+)?$', self.version):
            errors.append("Version must follow semantic versioning format (e.g., 1.0.0)")
            
        # Валидация пути экспорта
        if self.export_path:
            try:
                path = Path(self.export_path)
                if path.exists() and not path.is_dir():
                    errors.append("Export path exists but is not a directory")
            except (OSError, ValueError) as e:
                errors.append(f"Invalid export path: {e}")
                
        # Валидация настроек стиля кода
        style_errors = self.code_style.validate()
        errors.extend([f"Code style: {error}" for error in style_errors])
        
        return errors

    def _get_default_package_manager(self) -> str:
        """Получение пакетного менеджера по умолчанию для языка"""
        defaults = {
            "python": "pip",
            "java": "maven", 
            "javascript": "npm",
            "typescript": "npm",
            "csharp": "nuget"
        }
        return defaults.get(self.language, "")

    def _get_valid_frameworks_for_language(self) -> List[str]:
        """Получение списка поддерживаемых фреймворков для языка"""
        frameworks = {
            "python": ["django", "flask", "fastapi"],
            "java": ["spring", "spring-boot"],
            "javascript": ["express", "react", "vue", "angular"],
            "typescript": ["express", "react", "vue", "angular", "nest"],
            "csharp": ["aspnet-core", "blazor"]
        }
        return frameworks.get(self.language, [])

    def _get_valid_package_managers_for_language(self) -> List[str]:
        """Получение списка поддерживаемых пакетных менеджеров для языка"""
        managers = {
            "python": ["pip", "poetry", "pipenv"],
            "java": ["maven", "gradle"],
            "javascript": ["npm", "yarn", "pnpm"],
            "typescript": ["npm", "yarn", "pnpm"],
            "csharp": ["nuget"]
        }
        return managers.get(self.language, [])

    def to_dict(self) -> Dict[str, Any]:
        """Сериализация в словарь"""
        data = asdict(self)
        # Добавляем метаданные сериализации
        data["_serialization_version"] = "1.0"
        data["_created_at"] = datetime.now().isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectSettings':
        """Десериализация из словаря"""
        # Удаляем метаданные сериализации
        clean_data = {k: v for k, v in data.items() if not k.startswith('_')}
        
        # Обрабатываем вложенный объект CodeStyleSettings
        if 'code_style' in clean_data and isinstance(clean_data['code_style'], dict):
            clean_data['code_style'] = CodeStyleSettings(**clean_data['code_style'])
            
        return cls(**clean_data)

    def to_json(self) -> str:
        """Сериализация в JSON"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> 'ProjectSettings':
        """Десериализация из JSON"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def save_to_file(self, file_path: str):
        """Сохранение в файл"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())

    @classmethod
    def load_from_file(cls, file_path: str) -> 'ProjectSettings':
        """Загрузка из файла"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return cls.from_json(f.read())

    def get_package_manager_options(self) -> List[str]:
        """Получение доступных опций пакетного менеджера для текущего языка"""
        return self._get_valid_package_managers_for_language()

    def get_framework_options(self) -> List[str]:
        """Получение доступных опций фреймворка для текущего языка"""
        return self._get_valid_frameworks_for_language()

    def is_compatible_with_language(self, language: str) -> bool:
        """Проверка совместимости настроек с языком"""
        if self.framework:
            valid_frameworks = {
                "python": ["django", "flask", "fastapi"],
                "java": ["spring", "spring-boot"],
                "javascript": ["express", "react", "vue", "angular"],
                "typescript": ["express", "react", "vue", "angular", "nest"],
                "csharp": ["aspnet-core", "blazor"]
            }.get(language, [])
            
            if self.framework not in valid_frameworks:
                return False
                
        if self.package_manager:
            valid_managers = {
                "python": ["pip", "poetry", "pipenv"],
                "java": ["maven", "gradle"],
                "javascript": ["npm", "yarn", "pnpm"],
                "typescript": ["npm", "yarn", "pnpm"],
                "csharp": ["nuget"]
            }.get(language, [])
            
            if self.package_manager not in valid_managers:
                return False
                
        return True

    def clone(self) -> 'ProjectSettings':
        """Создание копии настроек"""
        return ProjectSettings.from_dict(self.to_dict())

    def update_from_dict(self, updates: Dict[str, Any]):
        """Обновление настроек из словаря"""
        for key, value in updates.items():
            if hasattr(self, key):
                if key == 'code_style' and isinstance(value, dict):
                    # Обновляем настройки стиля кода
                    for style_key, style_value in value.items():
                        if hasattr(self.code_style, style_key):
                            setattr(self.code_style, style_key, style_value)
                else:
                    setattr(self, key, value)