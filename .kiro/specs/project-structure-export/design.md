# Design Document

## Overview

Система экспорта проектов LogicCraft представляет собой расширение существующей архитектуры для создания полноценных структур проектов с правильной организацией папок, конфигурационными файлами и настройками генерации кода. Система интегрируется с существующим MVC паттерном и использует PyQt6 для UI компонентов.

Основная цель - предоставить пользователям возможность экспортировать UML диаграммы не просто как набор файлов с кодом, а как готовые к разработке проекты с правильной структурой папок, конфигурационными файлами, тестами и документацией для различных языков программирования и архитектурных паттернов.

## Architecture

### Высокоуровневая архитектура

Система экспорта проектов следует существующей архитектуре LogicCraft и расширяет её новыми компонентами:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Presentation Layer                         │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │ ProjectExportDialog │ │ StructurePreview │                  │
│  │                  │  │ Widget           │                    │
│  └──────────────────┘  └──────────────────┘                    │
├─────────────────────────────────────────────────────────────────┤
│                      Controller Layer                           │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │ProjectExportCtrl │  │TemplateController│                    │
│  │                  │  │                  │                    │
│  └──────────────────┘  └──────────────────┘                    │
├─────────────────────────────────────────────────────────────────┤
│                       Service Layer                             │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │ProjectExporter   │  │TemplateEngine    │                    │
│  │(Enhanced)        │  │                  │                    │
│  ├──────────────────┤  ├──────────────────┤                    │
│  │ConfigGenerator   │  │ProfileManager    │                    │
│  └──────────────────┘  └──────────────────┘                    │
├─────────────────────────────────────────────────────────────────┤
│                        Model Layer                              │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │ProjectSettings   │  │StructureTemplate │                    │
│  ├──────────────────┤  ├──────────────────┤                    │
│  │ExportProfile     │  │ProjectStructure  │                    │
│  └──────────────────┘  └──────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

### Интеграция с существующей системой

Новые компоненты интегрируются с существующими:

- **CodeGenerator** расширяется для поддержки настроек стиля кода
- **DiagramController** получает новые методы для экспорта проектов
- **MainWindow** добавляет новые пункты меню для экспорта проектов
- **FileController** расширяется для работы с профилями экспорта

## Components and Interfaces

### 1. ProjectExportDialog (Presentation Layer)

Главный диалог настройки экспорта проекта.

```python
class ProjectExportDialog(QDialog):
    """Диалог настройки экспорта проекта"""
    
    def __init__(self, diagram: UMLDiagram, parent=None):
        super().__init__(parent)
        self.diagram = diagram
        self.settings = ProjectSettings()
        self.preview_widget = StructurePreviewWidget()
        
    def _setup_ui(self):
        """Настройка интерфейса с вкладками"""
        # Основные настройки
        # Структура проекта  
        # Генерация кода
        # Дополнительные файлы
        # Предпросмотр
        
    def _update_preview(self):
        """Обновление предпросмотра в реальном времени"""
        
    def _validate_settings(self) -> List[str]:
        """Валидация настроек перед экспортом"""
```

### 2. StructurePreviewWidget (Presentation Layer)

Виджет предпросмотра структуры проекта.

```python
class StructurePreviewWidget(QWidget):
    """Виджет предпросмотра структуры проекта"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tree_widget = QTreeWidget()
        self.stats_label = QLabel()
        
    def update_preview(self, structure: ProjectStructure):
        """Обновление дерева файлов и статистики"""
        
    def _build_tree_item(self, item: StructureItem) -> QTreeWidgetItem:
        """Построение элемента дерева"""
```

### 3. ProjectExportController (Controller Layer)

Контроллер управления экспортом проектов.

```python
class ProjectExportController(QObject):
    """Контроллер экспорта проектов"""
    
    export_started = pyqtSignal()
    export_progress = pyqtSignal(int, str)  # progress, message
    export_completed = pyqtSignal(dict)     # result info
    export_failed = pyqtSignal(str)         # error message
    
    def __init__(self, diagram_controller: DiagramController):
        super().__init__()
        self.diagram_controller = diagram_controller
        self.exporter = ProjectExporter()
        self.profile_manager = ProfileManager()
        
    def export_project(self, settings: ProjectSettings, export_path: str):
        """Экспорт проекта с прогрессом"""
        
    def save_profile(self, profile: ExportProfile):
        """Сохранение профиля экспорта"""
        
    def load_profile(self, profile_name: str) -> ExportProfile:
        """Загрузка профиля экспорта"""
```

### 4. TemplateController (Controller Layer)

Контроллер управления шаблонами проектов.

```python
class TemplateController(QObject):
    """Контроллер шаблонов проектов"""
    
    def __init__(self):
        super().__init__()
        self.template_engine = TemplateEngine()
        
    def get_available_templates(self, language: str) -> List[StructureTemplate]:
        """Получение доступных шаблонов для языка"""
        
    def create_custom_template(self, template: StructureTemplate):
        """Создание пользовательского шаблона"""
```

### 5. ProjectExporter (Service Layer - Enhanced)

Расширенный сервис экспорта проектов.

```python
class ProjectExporter:
    """Расширенный экспортер проектов"""
    
    def __init__(self):
        self.generator = CodeGenerator()
        self.config_generator = ConfigGenerator()
        self.template_engine = TemplateEngine()
        
    def export_project(self, diagram: UMLDiagram, settings: ProjectSettings, 
                      export_path: str, progress_callback=None) -> ExportResult:
        """Экспорт проекта с прогрессом и валидацией"""
        
    def preview_structure(self, settings: ProjectSettings) -> ProjectStructure:
        """Предпросмотр структуры без создания файлов"""
        
    def validate_export_path(self, path: str, settings: ProjectSettings) -> ValidationResult:
        """Валидация пути экспорта"""
```

### 6. ConfigGenerator (Service Layer)

Генератор конфигурационных файлов.

```python
class ConfigGenerator:
    """Генератор конфигурационных файлов проекта"""
    
    def generate_package_config(self, settings: ProjectSettings) -> str:
        """Генерация package.json, requirements.txt, pom.xml и т.д."""
        
    def generate_build_config(self, settings: ProjectSettings) -> str:
        """Генерация конфигурации сборки"""
        
    def generate_ide_config(self, settings: ProjectSettings) -> Dict[str, str]:
        """Генерация конфигурации IDE (.vscode, .idea)"""
        
    def generate_ci_config(self, settings: ProjectSettings) -> Dict[str, str]:
        """Генерация CI/CD конфигурации"""
```

### 7. TemplateEngine (Service Layer)

Движок шаблонов проектов.

```python
class TemplateEngine:
    """Движок шаблонов проектов"""
    
    def __init__(self):
        self.jinja_env = Environment(
            loader=FileSystemLoader(self._get_templates_dir()),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
    def render_template(self, template_name: str, context: dict) -> str:
        """Рендеринг шаблона с контекстом"""
        
    def get_template_structure(self, template: StructureTemplate, 
                             settings: ProjectSettings) -> ProjectStructure:
        """Получение структуры проекта из шаблона"""
        
    def register_custom_template(self, template: StructureTemplate):
        """Регистрация пользовательского шаблона"""
```

### 8. ProfileManager (Service Layer)

Менеджер профилей экспорта.

```python
class ProfileManager:
    """Менеджер профилей экспорта"""
    
    def __init__(self):
        self.profiles_dir = Path.home() / ".logiccraft" / "export_profiles"
        
    def save_profile(self, profile: ExportProfile):
        """Сохранение профиля"""
        
    def load_profile(self, name: str) -> ExportProfile:
        """Загрузка профиля"""
        
    def get_available_profiles(self) -> List[str]:
        """Список доступных профилей"""
        
    def get_default_profiles(self) -> List[ExportProfile]:
        """Профили по умолчанию"""
```

## Data Models

### ProjectSettings

```python
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
```

### CodeStyleSettings

```python
@dataclass
class CodeStyleSettings:
    """Настройки стиля кода"""
    indentation: str = "    "  # 4 пробела по умолчанию
    naming_convention: Dict[str, str] = field(default_factory=dict)
    include_constructors: bool = True
    include_getters_setters: bool = False
    include_docstrings: bool = True
    include_type_hints: bool = True
    max_line_length: int = 88
```

### StructureTemplate

```python
@dataclass
class StructureTemplate:
    """Шаблон структуры проекта"""
    name: str
    language: str
    framework: Optional[str]
    description: str
    structure: Dict[str, Any]  # Дерево файлов и папок
    dependencies: List[str] = field(default_factory=list)
    dev_dependencies: List[str] = field(default_factory=list)
    scripts: Dict[str, str] = field(default_factory=dict)
    is_custom: bool = False
```

### ProjectStructure

```python
@dataclass
class ProjectStructure:
    """Структура проекта для предпросмотра"""
    root_path: Path
    items: List[StructureItem]
    total_files: int
    total_directories: int
    estimated_size: int  # в байтах
    
@dataclass
class StructureItem:
    """Элемент структуры проекта"""
    name: str
    type: str  # "file" или "directory"
    path: Path
    content: Optional[str] = None
    size: int = 0
    children: List['StructureItem'] = field(default_factory=list)
    will_overwrite: bool = False
```

### ExportProfile

```python
@dataclass
class ExportProfile:
    """Профиль настроек экспорта"""
    name: str
    description: str
    settings: ProjectSettings
    created_at: datetime
    version: str = "1.0"
    
    def to_dict(self) -> dict:
        """Сериализация в словарь"""
        
    @classmethod
    def from_dict(cls, data: dict) -> 'ExportProfile':
        """Десериализация из словаря"""
```

### ExportResult

```python
@dataclass
class ExportResult:
    """Результат экспорта проекта"""
    success: bool
    project_path: Path
    files_created: List[str]
    files_overwritten: List[str]
    errors: List[str]
    warnings: List[str]
    duration: float  # в секундах
    total_size: int  # в байтах
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

После анализа всех требований в prework, выявлены следующие группы свойств, которые можно объединить для устранения избыточности:

- Свойства 1.5 и 2.6 можно объединить в одно свойство о размещении элементов в соответствующих местах
- Свойства 3.7, 4.6, 6.3, 7.5, 10.4 можно объединить в одно свойство о применении настроек ко всем элементам
- Свойства 5.2, 6.2, 6.4, 6.5, 6.6 можно объединить в одно свойство о сохранении структуры и связей
- Свойства 9.4 и предпросмотр можно объединить в одно свойство о точности предпросмотра

### Property 1: Package Manager Language Consistency

*For any* supported programming language, the Export_Dialog should provide only the package managers that are appropriate for that specific language (pip/poetry for Python, npm/yarn for JS/TS, Maven/Gradle for Java, NuGet for C#).

**Validates: Requirements 1.5**

### Property 2: Project Structure Generation

*For any* valid combination of language and structure type, the Project_Exporter should create a directory structure that follows the conventions and standards for that language and architecture pattern, with generated classes placed in the appropriate folders.

**Validates: Requirements 2.6**

### Property 3: Configuration File Metadata Inclusion

*For any* generated configuration file (requirements.txt, package.json, pom.xml, etc.), the file should contain all specified project metadata (name, author, version, description) in the format appropriate for that configuration type.

**Validates: Requirements 3.7**

### Property 4: Universal Settings Application

*For any* project export with custom settings (code style, generation options, user preferences), these settings should be consistently applied to all generated files and components throughout the entire project structure.

**Validates: Requirements 4.6, 6.3, 7.5, 10.4**

### Property 5: Language-Specific Gitignore Generation

*For any* supported programming language, the Project_Exporter should create a .gitignore file containing rules and patterns that are specific and appropriate for that language's ecosystem.

**Validates: Requirements 5.2**

### Property 6: Class Relationship Preservation

*For any* UML diagram containing class relationships (inheritance, associations, dependencies), the Project_Exporter should generate code that maintains correct imports, references, and structural relationships between classes regardless of their placement in different modules or packages within the project structure.

**Validates: Requirements 6.2, 6.4, 6.5, 6.6**

### Property 7: Error Recovery and Cleanup

*For any* export operation that fails due to an error, the Project_Exporter should clean up all partially created files and directories, leaving the target location in its original state.

**Validates: Requirements 7.4**

### Property 8: Framework Template Integration

*For any* selected framework template, the Project_Exporter should include all framework-specific dependencies, configuration files, and directory structures that are required for that particular framework.

**Validates: Requirements 8.6**

### Property 9: Real-time Preview Accuracy

*For any* changes made to export settings in the Export_Dialog, the preview should immediately and accurately reflect the exact files and directories that would be created during the actual export process.

**Validates: Requirements 9.4**

### Property 10: Profile Completeness and Compatibility

*For any* export profile that is saved and later loaded, all settings should be restored to their exact state at the time of saving, and the profile should remain functional across different application sessions and compatible versions.

**Validates: Requirements 10.4, 10.6**

## Error Handling

### Validation Errors

1. **Project Name Validation**
   - Проверка на недопустимые символы
   - Проверка на зарезервированные имена
   - Предложение исправлений

2. **Path Validation**
   - Проверка доступности для записи
   - Проверка существования файлов
   - Предупреждения о перезаписи

3. **Diagram Validation**
   - Проверка наличия классов
   - Валидация связей между классами
   - Предупреждения о неполных данных

### Runtime Errors

1. **File System Errors**
   - Недостаток места на диске
   - Ошибки доступа к файлам
   - Прерывание операций

2. **Template Errors**
   - Отсутствующие шаблоны
   - Ошибки рендеринга
   - Некорректные зависимости

3. **Recovery Mechanisms**
   - Откат частично созданных файлов
   - Сохранение состояния для повтора
   - Детальные логи ошибок

### Error Reporting

```python
class ExportError(Exception):
    """Базовый класс ошибок экспорта"""
    
    def __init__(self, message: str, error_code: str, details: dict = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}

class ValidationError(ExportError):
    """Ошибки валидации настроек"""
    pass

class FileSystemError(ExportError):
    """Ошибки файловой системы"""
    pass

class TemplateError(ExportError):
    """Ошибки шаблонов"""
    pass
```

## Testing Strategy

### Unit Testing

**Компоненты для unit тестирования:**

1. **ConfigGenerator** - тестирование генерации конфигурационных файлов
2. **TemplateEngine** - тестирование рендеринга шаблонов
3. **ProfileManager** - тестирование сохранения/загрузки профилей
4. **ProjectSettings** - тестирование валидации настроек
5. **StructureTemplate** - тестирование шаблонов структур

**Примеры unit тестов:**

```python
def test_config_generator_python_requirements():
    """Тест генерации requirements.txt для Python"""
    generator = ConfigGenerator()
    settings = ProjectSettings(
        name="test_project",
        language="python",
        include_tests=True
    )
    
    content = generator.generate_package_config(settings)
    
    assert "pytest" in content
    assert "# Test dependencies" in content

def test_template_engine_mvc_structure():
    """Тест генерации MVC структуры"""
    engine = TemplateEngine()
    settings = ProjectSettings(
        name="test_app",
        language="python",
        structure_type="mvc"
    )
    
    structure = engine.get_template_structure(
        StructureTemplate.get_builtin("python_mvc"),
        settings
    )
    
    assert any(item.name == "models" for item in structure.items)
    assert any(item.name == "views" for item in structure.items)
    assert any(item.name == "controllers" for item in structure.items)
```

### Property-Based Testing

**Библиотека:** Hypothesis для Python

**Конфигурация:** Минимум 100 итераций на тест

**Теги:** Feature: project-structure-export, Property {number}: {property_text}

```python
from hypothesis import given, strategies as st

@given(
    language=st.sampled_from(["python", "java", "javascript", "typescript", "csharp"]),
    structure_type=st.sampled_from(["simple", "mvc", "layered", "clean_architecture"]),
    project_name=st.text(min_size=1, max_size=50).filter(str.isidentifier)
)
def test_property_project_structure_generation(language, structure_type, project_name):
    """
    Feature: project-structure-export, Property 3: For any valid combination of 
    language and structure type, the Project_Exporter should create a directory 
    structure that follows the conventions and standards for that language and 
    architecture pattern.
    """
    settings = ProjectSettings(
        name=project_name,
        language=language,
        structure_type=structure_type
    )
    
    exporter = ProjectExporter()
    structure = exporter.preview_structure(settings)
    
    # Проверяем, что структура соответствует языку
    if language == "python":
        assert any("__init__.py" in item.name for item in structure.items)
    elif language == "java":
        assert any("src/main/java" in str(item.path) for item in structure.items)
    elif language in ["javascript", "typescript"]:
        assert any("package.json" in item.name for item in structure.items)
    elif language == "csharp":
        assert any(".csproj" in item.name for item in structure.items)

@given(
    settings=st.builds(ProjectSettings),
    diagram=st.builds(UMLDiagram)
)
def test_property_code_integration_preservation(settings, diagram):
    """
    Feature: project-structure-export, Property 7: For any UML diagram with class 
    relationships, the Project_Exporter should generate code files that maintain 
    correct imports, dependencies, and references between classes regardless of 
    their placement in the project structure.
    """
    # Добавляем связи между классами
    if len(diagram.nodes) >= 2:
        connection = UMLConnection(
            source_id=diagram.nodes[0].id,
            target_id=diagram.nodes[1].id,
            type=ConnectionType.inheritance
        )
        diagram.connections.append(connection)
    
    exporter = ProjectExporter()
    result = exporter.export_project(diagram, settings, "/tmp/test_export")
    
    # Проверяем, что импорты корректны
    for file_path in result.files_created:
        if file_path.endswith(('.py', '.java', '.js', '.ts', '.cs')):
            with open(file_path, 'r') as f:
                content = f.read()
                # Проверяем наличие корректных импортов
                # (специфичная логика для каждого языка)
```

### Integration Testing

**Тестирование интеграции между компонентами:**

1. **UI → Controller → Service** интеграция
2. **Template Engine → File System** интеграция  
3. **Profile Manager → Settings** интеграция
4. **Code Generator → Project Exporter** интеграция

```python
def test_full_export_workflow():
    """Интеграционный тест полного процесса экспорта"""
    # Создаем диаграмму
    diagram = UMLDiagram(name="TestDiagram")
    diagram.nodes.append(UMLNode(name="TestClass", x=0, y=0))
    
    # Настройки экспорта
    settings = ProjectSettings(
        name="test_project",
        language="python",
        structure_type="mvc",
        include_tests=True,
        include_docs=True
    )
    
    # Экспорт
    controller = ProjectExportController(None)
    result = controller.export_project(settings, "/tmp/integration_test")
    
    # Проверки
    assert result.success
    assert Path(result.project_path).exists()
    assert len(result.files_created) > 0
    assert "requirements.txt" in [Path(f).name for f in result.files_created]
```

### UI Testing

**Тестирование пользовательского интерфейса:**

```python
def test_export_dialog_ui():
    """Тест UI диалога экспорта"""
    app = QApplication([])
    diagram = UMLDiagram(name="TestDiagram")
    
    dialog = ProjectExportDialog(diagram)
    dialog.show()
    
    # Проверяем наличие основных элементов
    assert dialog.language_combo is not None
    assert dialog.structure_combo is not None
    assert dialog.preview_widget is not None
    
    # Тестируем изменение настроек
    dialog.language_combo.setCurrentText("python")
    dialog.structure_combo.setCurrentText("mvc")
    
    # Проверяем обновление предпросмотра
    assert dialog.preview_widget.tree_widget.topLevelItemCount() > 0
```

Эта стратегия тестирования обеспечивает комплексную проверку функциональности системы экспорта проектов на всех уровнях - от отдельных компонентов до полной интеграции.