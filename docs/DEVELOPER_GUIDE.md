# 🛠️ Руководство разработчика LogicCraft

Добро пожаловать в команду разработчиков LogicCraft! Это руководство поможет вам быстро начать участвовать в развитии проекта.

## Содержание

1. [Настройка окружения](#настройка-окружения)
2. [Архитектура проекта](#архитектура-проекта)
3. [Стандарты кодирования](#стандарты-кодирования)
4. [Добавление новых функций](#добавление-новых-функций)
5. [Тестирование](#тестирование)
6. [Отладка](#отладка)
7. [Сборка и развертывание](#сборка-и-развертывание)

## Настройка окружения

### Требования

- **Python**: 3.13+
- **Poetry**: для управления зависимостями
- **Git**: для контроля версий
- **IDE**: PyCharm, VS Code или аналогичная

### Установка

```bash
# 1. Клонирование репозитория
git clone https://github.com/yourusername/logiccraft.git
cd logiccraft

# 2. Установка Poetry (если не установлен)
curl -sSL https://install.python-poetry.org | python3 -

# 3. Установка зависимостей
poetry install --with dev

# 4. Активация виртуального окружения
poetry shell

# 5. Проверка установки
poetry run python -m src.logiccraft.main
```

### Настройка IDE

#### VS Code
Установите расширения:
- Python
- Pylance
- Black Formatter
- isort

Настройки (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true
}
```

#### PyCharm
1. Откройте проект в PyCharm
2. File → Settings → Project → Python Interpreter
3. Выберите Poetry Environment
4. Настройте Code Style → Python → Black

## Архитектура проекта

### Структура директорий

```
src/logiccraft/
├── main.py                    # Точка входа
├── config/                    # Конфигурация
├── controllers/               # Бизнес-логика (MVC)
├── models/                    # Модели данных (Pydantic)
├── services/                  # Сервисный слой
├── utils/                     # Утилиты и константы
└── view/                      # Представление (PyQt6)
    ├── dialogs/              # Диалоговые окна
    ├── scenes/               # Сцены QGraphicsScene
    └── widgets/              # Кастомные виджеты
```

### Архитектурные принципы

1. **MVC Pattern** — разделение Model, View, Controller
2. **Dependency Injection** — слабая связанность компонентов
3. **Observer Pattern** — через PyQt сигналы/слоты
4. **Single Responsibility** — каждый класс имеет одну ответственность
5. **Open/Closed Principle** — открыт для расширения, закрыт для изменения

### Поток данных

```
User Input → View → Controller → Service → Model → Controller → View
```

## Стандарты кодирования

### Python Style Guide

Мы следуем **PEP 8** с некоторыми дополнениями:

```python
# Импорты
from typing import List, Optional, Dict
from PyQt6.QtWidgets import QWidget
from ..models.diagram import UMLNode

# Классы - PascalCase
class DiagramController:
    pass

# Методы и переменные - snake_case
def add_card(self, x: float, y: float) -> UMLNode:
    node_id = str(uuid4())
    return node

# Константы - UPPER_CASE
MAX_HISTORY_SIZE = 50
DEFAULT_CARD_WIDTH = 160

# Приватные методы - префикс _
def _validate_connection(self, conn: UMLConnection) -> bool:
    pass
```

### Документация

Используйте **Google Style** docstrings:

```python
def create_connection(self, source_id: str, target_id: str, 
                     connection_type: str) -> Optional[UMLConnection]:
    """Создает связь между двумя узлами.
    
    Args:
        source_id: ID исходного узла
        target_id: ID целевого узла
        connection_type: Тип связи (association, inheritance, etc.)
        
    Returns:
        Созданная связь или None при ошибке
        
    Raises:
        ValueError: Если узлы не найдены
        
    Example:
        >>> controller = DiagramController()
        >>> conn = controller.create_connection("id1", "id2", "inheritance")
    """
```

### Type Hints

Обязательно используйте аннотации типов:

```python
from typing import List, Optional, Dict, Union

def process_nodes(self, nodes: List[UMLNode]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    node_count: int = len(nodes)
    return result
```

## Добавление новых функций

### 1. Добавление нового типа связи

#### Шаг 1: Обновить модель
```python
# models/diagram.py
class ConnectionType(str, Enum):
    association = "association"
    inheritance = "inheritance"
    composition = "composition"
    aggregation = "aggregation"
    dependency = "dependency"      # Новый тип
    realization = "realization"    # Новый тип
```

#### Шаг 2: Обновить визуализацию
```python
# view/widgets/arrow_head.py
def _update_shape(self):
    if type_value == "dependency":
        # Пунктирная стрелка
        points = [QPointF(12, 0), QPointF(0, -6), QPointF(0, 6)]
        self.setPolygon(QPolygonF(points))
        self.setPen(QPen(QColor("#666666"), 2, Qt.PenStyle.DashLine))
```

#### Шаг 3: Обновить UI
```python
# view/dialogs/connection_properties.py
def _setup_ui(self):
    self.type_combo.addItem("Dependency", ConnectionType.dependency.value)
    self.type_combo.addItem("Realization", ConnectionType.realization.value)
```

### 2. Добавление нового языка генерации

#### Шаг 1: Создать генератор
```python
# services/code_generator.py
def _generate_csharp(self, diagram: UMLDiagram) -> str:
    """Генерация C# кода"""
    lines = ["using System;", "using System.Collections.Generic;", ""]
    
    for node in diagram.nodes:
        lines.extend(self._generate_csharp_class(node))
        lines.append("")
    
    return "\n".join(lines)

def _generate_csharp_class(self, node: UMLNode) -> List[str]:
    lines = [f"public class {node.name}", "{"]
    
    # Свойства
    for prop in node.properties:
        visibility = "public" if prop.visibility == "public" else "private"
        lines.append(f"    {visibility} {prop.type} {prop.name} {{ get; set; }}")
    
    lines.append("}")
    return lines
```

#### Шаг 2: Зарегистрировать язык
```python
def generate(self, diagram: UMLDiagram, language: str) -> str:
    generators = {
        "python": self._generate_python,
        "java": self._generate_java,
        "javascript": self._generate_javascript,
        "csharp": self._generate_csharp,  # Новый язык
    }
    
    generator = generators.get(language)
    if not generator:
        raise ValueError(f"Unsupported language: {language}")
    
    return generator(diagram)
```

### 3. Добавление нового диалога

#### Создание диалога
```python
# view/dialogs/export_dialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QDialogButtonBox

class ExportDialog(QDialog):
    """Диалог экспорта диаграммы"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Diagram")
        self.setMinimumWidth(300)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        # Выбор формата
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "SVG", "PDF"])
        layout.addWidget(self.format_combo)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_format(self) -> str:
        return self.format_combo.currentText().lower()
```

#### Интеграция в контроллер
```python
# controllers/diagram_controller.py
def export_diagram(self, format: str, filepath: str) -> bool:
    """Экспорт диаграммы в указанный формат"""
    try:
        if format == "png":
            return self._export_to_png(filepath)
        elif format == "svg":
            return self._export_to_svg(filepath)
        # ...
    except Exception as e:
        self.error_occurred.emit(f"Export failed: {e}")
        return False
```

## Тестирование

### Структура тестов

```
tests/
├── unit/                      # Модульные тесты
│   ├── test_models.py
│   ├── test_controllers.py
│   └── test_services.py
├── integration/               # Интеграционные тесты
│   ├── test_diagram_flow.py
│   └── test_file_operations.py
└── fixtures/                  # Тестовые данные
    ├── sample_diagram.json
    └── test_classes.py
```

### Написание тестов

#### Unit тесты
```python
# tests/unit/test_models.py
import pytest
from src.logiccraft.models.diagram import UMLNode, UMLConnection

class TestUMLNode:
    def test_node_creation(self):
        """Тест создания узла"""
        node = UMLNode(name="TestClass", x=100, y=200)
        
        assert node.name == "TestClass"
        assert node.x == 100
        assert node.y == 200
        assert len(node.properties) == 0
        assert len(node.methods) == 0
    
    def test_add_attribute(self):
        """Тест добавления атрибута"""
        node = UMLNode(name="Test")
        node.add_attribute("name", "str", "public")
        
        assert len(node.properties) == 1
        assert node.properties[0].name == "name"
        assert node.properties[0].type == "str"
        assert node.properties[0].visibility == "public"
    
    @pytest.mark.parametrize("name,expected", [
        ("ValidName", True),
        ("", False),
        ("123Invalid", False),
    ])
    def test_name_validation(self, name, expected):
        """Тест валидации имени"""
        node = UMLNode(name=name)
        assert node.is_valid_name() == expected
```

#### Integration тесты
```python
# tests/integration/test_diagram_flow.py
import pytest
from src.logiccraft.controllers.diagram_controller import DiagramController

class TestDiagramFlow:
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.controller = DiagramController()
    
    def test_add_card_and_connection(self):
        """Тест полного цикла: создание карточек и связи"""
        # Создание двух карточек
        node1 = self.controller.add_card(100, 100, "Class1")
        node2 = self.controller.add_card(300, 100, "Class2")
        
        assert len(self.controller.manager.diagram.nodes) == 2
        
        # Создание связи
        connection = self.controller.add_connection(
            node1.id, node2.id, "inheritance"
        )
        
        assert connection is not None
        assert len(self.controller.manager.diagram.connections) == 1
        assert connection.source_id == node1.id
        assert connection.target_id == node2.id
```

### Запуск тестов

```bash
# Все тесты
poetry run pytest

# Конкретный файл
poetry run pytest tests/unit/test_models.py

# С покрытием кода
poetry run pytest --cov=src/logiccraft

# Только быстрые тесты
poetry run pytest -m "not slow"

# Подробный вывод
poetry run pytest -v
```

### Фикстуры

```python
# tests/conftest.py
import pytest
from src.logiccraft.models.diagram import UMLDiagram, UMLNode

@pytest.fixture
def sample_diagram():
    """Создает тестовую диаграмму"""
    diagram = UMLDiagram(name="Test Diagram")
    
    node1 = UMLNode(name="User", x=100, y=100)
    node1.add_attribute("name", "str", "public")
    node1.add_method("get_name", "str", "public")
    
    node2 = UMLNode(name="Admin", x=300, y=100)
    
    diagram.nodes = [node1, node2]
    return diagram

@pytest.fixture
def controller():
    """Создает контроллер для тестов"""
    return DiagramController()
```

## Отладка

### Логирование

```python
import logging

# Настройка логгера
logger = logging.getLogger(__name__)

class DiagramController:
    def add_card(self, x: float, y: float) -> UMLNode:
        logger.debug(f"Adding card at position ({x}, {y})")
        
        try:
            node = self.manager.add_node(x, y)
            logger.info(f"Card created with ID: {node.id}")
            return node
        except Exception as e:
            logger.error(f"Failed to add card: {e}", exc_info=True)
            raise
```

### Отладочные принты

Для временной отладки используйте префикс `DEBUG`:

```python
def _on_connection_added(self, connection):
    print(f"DEBUG: Connection added - {connection.id}")
    print(f"DEBUG: Source: {connection.source_id}")
    print(f"DEBUG: Target: {connection.target_id}")
    
    # Основной код...
```

### Профилирование

```python
import time
import functools

def measure_time(func):
    """Декоратор для измерения времени выполнения"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

@measure_time
def update_all_connections(self):
    """Обновление всех связей"""
    for connection in self.connection_map.values():
        connection.update_position()
```

### Отладка PyQt

```python
# Включение отладки Qt
import os
os.environ['QT_LOGGING_RULES'] = 'qt.qpa.*.debug=true'

# Отладка сигналов
from PyQt6.QtCore import QObject

class DebugObject(QObject):
    def __init__(self):
        super().__init__()
        # Подключение ко всем сигналам для отладки
        self.destroyed.connect(lambda: print("Object destroyed"))
```

## Сборка и развертывание

### Локальная сборка

```bash
# Проверка кода
poetry run black src/ tests/
poetry run isort src/ tests/
poetry run pylint src/

# Запуск тестов
poetry run pytest

# Сборка wheel пакета
poetry build
```

### Создание исполняемого файла

```bash
# Установка PyInstaller
poetry add --group dev pyinstaller

# Сборка для текущей платформы
poetry run pyinstaller --onefile --windowed \
    --name LogicCraft \
    --icon assets/icon.ico \
    src/logiccraft/main.py

# Результат в dist/LogicCraft.exe (Windows) или dist/LogicCraft (Linux/macOS)
```

### Настройка CI/CD

#### GitHub Actions (`.github/workflows/ci.yml`)
```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.13, 3.14]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install Poetry
      uses: snok/install-poetry@v1
    
    - name: Install dependencies
      run: poetry install --with dev
    
    - name: Run tests
      run: poetry run pytest --cov=src/logiccraft
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### Релиз

1. **Обновите версию** в `pyproject.toml`
2. **Создайте changelog** в `CHANGELOG.md`
3. **Создайте git tag**: `git tag v1.2.0`
4. **Push tag**: `git push origin v1.2.0`
5. **GitHub Actions** автоматически создаст релиз

## Участие в проекте

### Workflow

1. **Fork** репозитория
2. **Создайте ветку** для новой функции: `git checkout -b feature/new-feature`
3. **Внесите изменения** и добавьте тесты
4. **Запустите тесты**: `poetry run pytest`
5. **Создайте Pull Request**

### Код ревью

Перед мержем PR проверяется:

- ✅ Все тесты проходят
- ✅ Покрытие кода не уменьшилось
- ✅ Код соответствует стандартам
- ✅ Добавлена документация
- ✅ Нет breaking changes (или они документированы)

### Коммиты

Используйте [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add support for C# code generation
fix: resolve connection line positioning bug
docs: update installation instructions
test: add unit tests for UMLNode class
refactor: extract connection validation logic
```

---

Добро пожаловать в команду! 🚀 Если у вас есть вопросы, создайте Issue или обратитесь к мейнтейнерам.