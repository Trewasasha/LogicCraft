"""Тесты для модели ProjectSettings"""

import pytest
import json
import tempfile
from pathlib import Path
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import only the specific modules we need to avoid circular imports
from logiccraft.models.project_settings import ProjectSettings, CodeStyleSettings


class TestCodeStyleSettings:
    """Тесты для CodeStyleSettings"""
    
    def test_default_initialization(self):
        """Тест инициализации по умолчанию"""
        style = CodeStyleSettings()
        
        assert style.indentation == "    "
        assert style.include_constructors is True
        assert style.include_docstrings is True
        assert style.max_line_length == 88
        
    def test_validation_success(self):
        """Тест успешной валидации"""
        style = CodeStyleSettings()
        errors = style.validate()
        
        assert len(errors) == 0
        
    def test_validation_empty_indentation(self):
        """Тест валидации пустого отступа"""
        style = CodeStyleSettings(indentation="")
        errors = style.validate()
        
        assert "Indentation cannot be empty" in errors
        
    def test_validation_invalid_line_length(self):
        """Тест валидации неверной длины строки"""
        style = CodeStyleSettings(max_line_length=30)
        errors = style.validate()
        
        assert any("Max line length must be between 50 and 200" in error for error in errors)
        
    def test_apply_python_defaults(self):
        """Тест применения настроек по умолчанию для Python"""
        style = CodeStyleSettings()
        style.apply_language_defaults("python")
        
        assert style.naming_convention["method"] == "snake_case"
        assert style.naming_convention["class"] == "PascalCase"
        assert style.include_type_hints is True
        
    def test_apply_java_defaults(self):
        """Тест применения настроек по умолчанию для Java"""
        style = CodeStyleSettings()
        style.apply_language_defaults("java")
        
        assert style.naming_convention["method"] == "camelCase"
        assert style.naming_convention["class"] == "PascalCase"
        assert style.include_type_hints is False

    def test_get_indentation_type_spaces(self):
        """Тест определения типа отступа - пробелы"""
        style = CodeStyleSettings(indentation="    ")
        assert style.get_indentation_type() == "spaces"
        
    def test_get_indentation_type_tabs(self):
        """Тест определения типа отступа - табы"""
        style = CodeStyleSettings(indentation="\t")
        assert style.get_indentation_type() == "tabs"
        
    def test_get_indentation_size_spaces(self):
        """Тест определения размера отступа - пробелы"""
        style = CodeStyleSettings(indentation="  ")
        assert style.get_indentation_size() == 2
        
    def test_get_indentation_size_tabs(self):
        """Тест определения размера отступа - табы"""
        style = CodeStyleSettings(indentation="\t")
        assert style.get_indentation_size() == 1
        
    def test_set_indentation_spaces(self):
        """Тест установки отступа пробелами"""
        style = CodeStyleSettings()
        style.set_indentation("spaces", 2)
        assert style.indentation == "  "
        
    def test_set_indentation_tabs(self):
        """Тест установки отступа табами"""
        style = CodeStyleSettings()
        style.set_indentation("tabs")
        assert style.indentation == "\t"
        
    def test_set_indentation_invalid_type(self):
        """Тест установки неверного типа отступа"""
        style = CodeStyleSettings()
        with pytest.raises(ValueError, match="indent_type must be 'tabs' or 'spaces'"):
            style.set_indentation("invalid")
            
    def test_get_naming_convention_for_element(self):
        """Тест получения соглашения именования для элемента"""
        style = CodeStyleSettings()
        assert style.get_naming_convention_for_element("class") == "PascalCase"
        assert style.get_naming_convention_for_element("nonexistent") == "camelCase"
        
    def test_set_naming_convention_for_element(self):
        """Тест установки соглашения именования для элемента"""
        style = CodeStyleSettings()
        style.set_naming_convention_for_element("method", "snake_case")
        assert style.naming_convention["method"] == "snake_case"
        
    def test_set_naming_convention_invalid(self):
        """Тест установки неверного соглашения именования"""
        style = CodeStyleSettings()
        with pytest.raises(ValueError, match="Invalid naming convention"):
            style.set_naming_convention_for_element("method", "invalid_convention")
            
    def test_get_supported_languages(self):
        """Тест получения поддерживаемых языков"""
        style = CodeStyleSettings()
        languages = style.get_supported_languages()
        assert "python" in languages
        assert "java" in languages
        assert "typescript" in languages
        
    def test_is_language_supported(self):
        """Тест проверки поддержки языка"""
        style = CodeStyleSettings()
        assert style.is_language_supported("python") is True
        assert style.is_language_supported("unsupported") is False
        
    def test_get_language_specific_settings(self):
        """Тест получения настроек для конкретного языка"""
        style = CodeStyleSettings()
        python_settings = style.get_language_specific_settings("python")
        
        assert python_settings["naming_convention"]["method"] == "snake_case"
        assert python_settings["include_type_hints"] is True
        assert python_settings["max_line_length"] == 88
        
    def test_get_language_specific_settings_unsupported(self):
        """Тест получения настроек для неподдерживаемого языка"""
        style = CodeStyleSettings()
        with pytest.raises(ValueError, match="Unsupported language"):
            style.get_language_specific_settings("unsupported")
            
    def test_apply_typescript_defaults(self):
        """Тест применения настроек по умолчанию для TypeScript"""
        style = CodeStyleSettings()
        style.apply_language_defaults("typescript")
        
        assert style.naming_convention["method"] == "camelCase"
        assert style.indentation == "  "  # 2 spaces
        assert style.include_type_hints is True
        assert style.max_line_length == 100
        
    def test_apply_csharp_defaults(self):
        """Тест применения настроек по умолчанию для C#"""
        style = CodeStyleSettings()
        style.apply_language_defaults("csharp")
        
        assert style.naming_convention["property"] == "PascalCase"
        assert style.max_line_length == 120
        assert style.include_type_hints is False


class TestProjectSettings:
    """Тесты для ProjectSettings"""
    
    def test_basic_initialization(self):
        """Тест базовой инициализации"""
        settings = ProjectSettings(
            name="test_project",
            language="python",
            structure_type="simple"
        )
        
        assert settings.name == "test_project"
        assert settings.language == "python"
        assert settings.structure_type == "simple"
        assert settings.version == "1.0.0"
        assert settings.package_manager == "pip"  # default for python
        
    def test_post_init_package_manager(self):
        """Тест автоматической установки пакетного менеджера"""
        settings = ProjectSettings(
            name="test_project",
            language="java",
            structure_type="simple"
        )
        
        assert settings.package_manager == "maven"
        
    def test_validation_success(self):
        """Тест успешной валидации"""
        settings = ProjectSettings(
            name="valid_project",
            language="python",
            structure_type="mvc"
        )
        
        errors = settings.validate()
        assert len(errors) == 0
        
    def test_validation_empty_name(self):
        """Тест валидации пустого имени"""
        settings = ProjectSettings(
            name="",
            language="python",
            structure_type="simple"
        )
        
        errors = settings.validate()
        assert any("Project name cannot be empty" in error for error in errors)
        
    def test_validation_invalid_name(self):
        """Тест валидации неверного имени проекта"""
        settings = ProjectSettings(
            name="123invalid",
            language="python",
            structure_type="simple"
        )
        
        errors = settings.validate()
        assert any("must start with a letter" in error for error in errors)
        
    def test_validation_unsupported_language(self):
        """Тест валидации неподдерживаемого языка"""
        settings = ProjectSettings(
            name="test_project",
            language="unsupported",
            structure_type="simple"
        )
        
        errors = settings.validate()
        assert any("Unsupported language" in error for error in errors)
        
    def test_validation_invalid_framework(self):
        """Тест валидации неподдерживаемого фреймворка"""
        settings = ProjectSettings(
            name="test_project",
            language="python",
            structure_type="simple",
            framework="invalid_framework"
        )
        
        errors = settings.validate()
        assert any("is not supported for python" in error for error in errors)
        
    def test_validation_invalid_version(self):
        """Тест валидации неверного формата версии"""
        settings = ProjectSettings(
            name="test_project",
            language="python",
            structure_type="simple",
            version="invalid_version"
        )
        
        errors = settings.validate()
        assert any("Version must follow semantic versioning" in error for error in errors)
        
    def test_serialization_to_dict(self):
        """Тест сериализации в словарь"""
        settings = ProjectSettings(
            name="test_project",
            language="python",
            structure_type="mvc",
            author="Test Author"
        )
        
        data = settings.to_dict()
        
        assert data["name"] == "test_project"
        assert data["language"] == "python"
        assert data["author"] == "Test Author"
        assert "_serialization_version" in data
        assert "_created_at" in data
        
    def test_deserialization_from_dict(self):
        """Тест десериализации из словаря"""
        data = {
            "name": "test_project",
            "language": "java",
            "structure_type": "simple",
            "author": "Test Author",
            "code_style": {
                "indentation": "  ",
                "max_line_length": 100
            }
        }
        
        settings = ProjectSettings.from_dict(data)
        
        assert settings.name == "test_project"
        assert settings.language == "java"
        assert settings.author == "Test Author"
        # Note: indentation will be overridden by language defaults in __post_init__
        assert settings.code_style.indentation == "    "  # Java default is 4 spaces
        assert settings.code_style.max_line_length == 100
        
    def test_json_serialization(self):
        """Тест JSON сериализации"""
        settings = ProjectSettings(
            name="test_project",
            language="typescript",
            structure_type="mvc"
        )
        
        json_str = settings.to_json()
        loaded_settings = ProjectSettings.from_json(json_str)
        
        assert loaded_settings.name == settings.name
        assert loaded_settings.language == settings.language
        assert loaded_settings.structure_type == settings.structure_type
        
    def test_file_operations(self):
        """Тест операций с файлами"""
        settings = ProjectSettings(
            name="test_project",
            language="csharp",
            structure_type="layered",
            description="Test project description"
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
            
        try:
            settings.save_to_file(temp_path)
            loaded_settings = ProjectSettings.load_from_file(temp_path)
            
            assert loaded_settings.name == settings.name
            assert loaded_settings.language == settings.language
            assert loaded_settings.description == settings.description
        finally:
            Path(temp_path).unlink(missing_ok=True)
            
    def test_get_package_manager_options(self):
        """Тест получения опций пакетного менеджера"""
        settings = ProjectSettings(
            name="test_project",
            language="python",
            structure_type="simple"
        )
        
        options = settings.get_package_manager_options()
        
        assert "pip" in options
        assert "poetry" in options
        assert "pipenv" in options
        
    def test_get_framework_options(self):
        """Тест получения опций фреймворка"""
        settings = ProjectSettings(
            name="test_project",
            language="javascript",
            structure_type="simple"
        )
        
        options = settings.get_framework_options()
        
        assert "express" in options
        assert "react" in options
        assert "vue" in options
        
    def test_language_compatibility(self):
        """Тест проверки совместимости с языком"""
        settings = ProjectSettings(
            name="test_project",
            language="python",
            structure_type="simple",
            framework="django",
            package_manager="pip"
        )
        
        assert settings.is_compatible_with_language("python") is True
        assert settings.is_compatible_with_language("java") is False
        
    def test_clone(self):
        """Тест клонирования настроек"""
        original = ProjectSettings(
            name="original_project",
            language="python",
            structure_type="mvc",
            author="Original Author"
        )
        
        cloned = original.clone()
        
        assert cloned.name == original.name
        assert cloned.language == original.language
        assert cloned is not original  # Разные объекты
        assert cloned.code_style is not original.code_style  # Глубокое копирование
        
    def test_update_from_dict(self):
        """Тест обновления из словаря"""
        settings = ProjectSettings(
            name="test_project",
            language="python",
            structure_type="simple"
        )
        
        updates = {
            "author": "New Author",
            "description": "Updated description",
            "code_style": {
                "max_line_length": 120,
                "include_docstrings": False
            }
        }
        
        settings.update_from_dict(updates)
        
        assert settings.author == "New Author"
        assert settings.description == "Updated description"
        assert settings.code_style.max_line_length == 120
        assert settings.code_style.include_docstrings is False