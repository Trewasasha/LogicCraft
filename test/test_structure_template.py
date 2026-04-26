"""Тесты для модели StructureTemplate"""

import pytest
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from logiccraft.models.structure_template import StructureTemplate


class TestStructureTemplate:
    """Тесты для StructureTemplate"""

    def test_create_basic_template(self):
        """Тест создания базового шаблона"""
        template = StructureTemplate(
            name="Test Template",
            language="python",
            framework=None,
            description="A test template",
            structure={
                "main.py": "print('Hello World')",
                "src": {
                    "__init__.py": "",
                    "models.py": "# Models here"
                }
            }
        )
        
        assert template.name == "Test Template"
        assert template.language == "python"
        assert template.framework is None
        assert template.description == "A test template"
        assert not template.is_custom
        assert template.get_file_count() == 3
        assert template.get_directory_count() == 1

    def test_template_validation(self):
        """Тест валидации шаблона"""
        # Валидный шаблон
        template = StructureTemplate(
            name="Valid Template",
            language="python",
            framework="django",
            description="Valid template",
            structure={"main.py": "print('test')"}
        )
        
        errors = template.validate()
        assert len(errors) == 0

    def test_invalid_template_validation(self):
        """Тест валидации невалидного шаблона"""
        # Пустое имя
        with pytest.raises(ValueError):
            StructureTemplate(
                name="",
                language="python",
                framework=None,
                description="Test",
                structure={"main.py": "test"}
            )

    def test_file_operations(self):
        """Тест операций с файлами"""
        template = StructureTemplate(
            name="File Test",
            language="python",
            framework=None,
            description="Test file operations",
            structure={
                "main.py": "print('Hello')",
                "src": {
                    "models.py": "# Models"
                }
            }
        )
        
        # Проверка наличия файлов
        assert template.has_file("main.py")
        assert template.has_file("src/models.py")
        assert not template.has_file("nonexistent.py")
        
        # Получение содержимого
        assert template.get_file_content("main.py") == "print('Hello')"
        assert template.get_file_content("src/models.py") == "# Models"
        assert template.get_file_content("nonexistent.py") is None
        
        # Установка содержимого
        template.set_file_content("new_file.py", "# New file")
        assert template.has_file("new_file.py")
        assert template.get_file_content("new_file.py") == "# New file"

    def test_dependency_operations(self):
        """Тест операций с зависимостями"""
        template = StructureTemplate(
            name="Dependency Test",
            language="python",
            framework=None,
            description="Test dependencies",
            structure={"main.py": "test"}
        )
        
        # Добавление зависимостей
        template.add_dependency("requests")
        template.add_dependency("pytest", is_dev=True)
        
        assert "requests" in template.dependencies
        assert "pytest" in template.dev_dependencies
        
        # Удаление зависимостей
        template.remove_dependency("requests")
        assert "requests" not in template.dependencies

    def test_script_operations(self):
        """Тест операций со скриптами"""
        template = StructureTemplate(
            name="Script Test",
            language="python",
            framework=None,
            description="Test scripts",
            structure={"main.py": "test"}
        )
        
        # Добавление скриптов
        template.add_script("test", "python -m pytest")
        template.add_script("run", "python main.py")
        
        assert template.scripts["test"] == "python -m pytest"
        assert template.scripts["run"] == "python main.py"
        
        # Удаление скриптов
        template.remove_script("test")
        assert "test" not in template.scripts

    def test_serialization(self):
        """Тест сериализации и десериализации"""
        original = StructureTemplate(
            name="Serialization Test",
            language="python",
            framework="django",
            description="Test serialization",
            structure={"main.py": "test"},
            dependencies=["django"],
            dev_dependencies=["pytest"],
            scripts={"test": "pytest"}
        )
        
        # Сериализация в словарь
        data = original.to_dict()
        assert data["name"] == "Serialization Test"
        assert data["language"] == "python"
        
        # Десериализация из словаря
        restored = StructureTemplate.from_dict(data)
        assert restored.name == original.name
        assert restored.language == original.language
        assert restored.structure == original.structure
        assert restored.dependencies == original.dependencies

    def test_builtin_templates(self):
        """Тест встроенных шаблонов"""
        # Получение всех встроенных шаблонов
        templates = StructureTemplate.get_all_builtin_templates()
        assert len(templates) > 0
        
        # Проверка Django шаблона
        django_template = StructureTemplate.get_builtin_template("django")
        assert django_template is not None
        assert django_template.name == "Django Project"
        assert django_template.language == "python"
        assert django_template.framework == "django"
        
        # Проверка шаблонов для Python
        python_templates = StructureTemplate.get_builtin_templates_for_language("python")
        assert len(python_templates) >= 1
        assert all(t.language == "python" for t in python_templates)

    def test_template_merge(self):
        """Тест слияния шаблонов"""
        template1 = StructureTemplate(
            name="Template 1",
            language="python",
            framework=None,
            description="First template",
            structure={"file1.py": "content1"},
            dependencies=["dep1"]
        )
        
        template2 = StructureTemplate(
            name="Template 2",
            language="python",
            framework=None,
            description="Second template",
            structure={"file2.py": "content2"},
            dependencies=["dep2"]
        )
        
        merged = template1.merge_with(template2)
        
        assert merged.has_file("file1.py")
        assert merged.has_file("file2.py")
        assert "dep1" in merged.dependencies
        assert "dep2" in merged.dependencies
        assert merged.is_custom

    def test_template_compatibility(self):
        """Тест совместимости шаблонов"""
        template = StructureTemplate(
            name="Python Template",
            language="python",
            framework=None,
            description="Python template",
            structure={"main.py": "test"}
        )
        
        assert template.is_compatible_with_language("python")
        assert not template.is_compatible_with_language("java")

    def test_template_clone(self):
        """Тест клонирования шаблона"""
        original = StructureTemplate(
            name="Original",
            language="python",
            framework=None,
            description="Original template",
            structure={"main.py": "test"},
            dependencies=["requests"]
        )
        
        cloned = original.clone()
        
        assert cloned.name == original.name
        assert cloned.structure == original.structure
        assert cloned.dependencies == original.dependencies
        
        # Изменение клона не должно влиять на оригинал
        cloned.add_dependency("pytest")
        assert "pytest" not in original.dependencies

    def test_estimated_size(self):
        """Тест оценки размера проекта"""
        template = StructureTemplate(
            name="Size Test",
            language="python",
            framework=None,
            description="Test size estimation",
            structure={
                "small.py": "x = 1",
                "large.py": "# " + "x" * 1000,
                "empty.py": ""
            }
        )
        
        size = template.get_estimated_size()
        assert size > 0
        assert size > 1000  # Should account for the large file

    def test_string_representations(self):
        """Тест строковых представлений"""
        template = StructureTemplate(
            name="String Test",
            language="python",
            framework="django",
            description="Test string representations",
            structure={"main.py": "test"}
        )
        
        str_repr = str(template)
        assert "String Test" in str_repr
        assert "python" in str_repr
        assert "django" in str_repr
        
        repr_str = repr(template)
        assert "StructureTemplate" in repr_str
        assert "String Test" in repr_str