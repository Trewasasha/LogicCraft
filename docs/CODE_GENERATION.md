# 🔧 Генерация кода в LogicCraft

Система генерации кода LogicCraft использует шаблоны Jinja2 для создания исходного кода на различных языках программирования из UML диаграмм.

## 📋 Поддерживаемые языки

- **Python** (.py) - с поддержкой абстрактных классов, типизации
- **Java** (.java) - с модификаторами доступа, наследованием
- **JavaScript** (.js) - ES6 классы
- **TypeScript** (.ts) - с типизацией и интерфейсами
- **C#** (.cs) - с properties и модификаторами

## 🏗️ Архитектура системы

### Основные компоненты

1. **CodeGenerator** - основной класс для генерации кода
2. **Jinja2 шаблоны** - файлы `.j2` для каждого языка
3. **Конфигурация** - настройки типов и стилей кода
4. **Карта наследования** - обработка связей между классами

### Структура файлов

```
src/logiccraft/
├── services/
│   └── code_generator.py      # Основной генератор
├── templates/
│   ├── __init__.py
│   ├── config.py              # Конфигурация языков
│   ├── python_class.j2        # Шаблон Python
│   ├── java_class.j2          # Шаблон Java
│   ├── javascript_class.j2    # Шаблон JavaScript
│   ├── typescript_class.j2    # Шаблон TypeScript
│   └── csharp_class.j2        # Шаблон C#
```

## 🚀 Использование

### Базовая генерация

```python
from logiccraft.services.code_generator import CodeGenerator
from logiccraft.models.diagram import UMLDiagram

# Создание генератора
generator = CodeGenerator()

# Генерация всех классов в один файл
code = generator.generate(diagram, language="python")

# Генерация отдельных файлов для каждого класса
files = generator.generate_files(diagram, language="java")
```

### Поддерживаемые языки

```python
# Получить список поддерживаемых языков
languages = generator.get_supported_languages()
print(languages)  # ['python', 'java', 'javascript', 'typescript', 'csharp']
```

## 📝 Шаблоны Jinja2

### Переменные шаблона

Все шаблоны получают следующие переменные:

- `diagram_name` - имя диаграммы
- `nodes` - список UML классов
- `inheritance_map` - карта наследования классов
- `has_abstract_classes` - есть ли абстрактные классы (для Python)
- `language` - целевой язык

### Функции-помощники

- `get_python_visibility(visibility)` - преобразование видимости для Python
- `get_java_visibility(visibility)` - преобразование видимости для Java
- `generate_method_params(method)` - генерация параметров метода

### Пример шаблона (Python)

```jinja2
"""Generated from UML Diagram: {{ diagram_name }}"""
from typing import List, Optional
{% if has_abstract_classes %}
from abc import ABC, abstractmethod
{% endif %}

{% for node in nodes %}
{% if node.is_abstract %}
class {{ node.name }}(ABC):
{% else %}
class {{ node.name }}:
{% endif %}
    """{{ node.stereotype or "Class generated from UML diagram" }}"""
    
    # ... остальной код класса
{% endfor %}
```

## ⚙️ Конфигурация

### Настройки языков

Файл `templates/config.py` содержит конфигурацию для каждого языка:

```python
LANGUAGE_CONFIGS = {
    "python": {
        "extension": ".py",
        "template": "python_class.j2",
        "type_mappings": {
            "string": "str",
            "integer": "int",
            # ...
        },
        "default_values": {
            "str": '""',
            "int": "0",
            # ...
        }
    }
}
```

### Стили кода

```python
CODE_STYLES = {
    "indentation": {
        "python": "    ",  # 4 пробела
        "java": "    ",    # 4 пробела
        # ...
    },
    "naming_conventions": {
        "python": {
            "class": "PascalCase",
            "method": "snake_case",
            # ...
        }
    }
}
```

## 🔄 Обработка связей

### Карта наследования

Система автоматически строит карту наследования из связей диаграммы:

```python
def _build_inheritance_map(self, diagram: UMLDiagram) -> Dict[str, List[str]]:
    inheritance_map = {}
    
    for node in diagram.nodes:
        inheritance_map[node.name] = []
    
    for connection in diagram.connections:
        if connection.type.value == "inheritance":
            # Добавляем связь наследования
            source_node = find_node_by_id(connection.source_id)
            target_node = find_node_by_id(connection.target_id)
            inheritance_map[source_node.name].append(target_node.name)
    
    return inheritance_map
```

### Типы связей

- **inheritance** - наследование классов
- **composition** - композиция (планируется)
- **aggregation** - агрегация (планируется)
- **association** - ассоциация (планируется)

## 📊 Примеры генерации

### Python класс

```python
"""Generated from UML Diagram: MyDiagram"""
from typing import List, Optional

class User:
    """User entity class"""
    
    # Attributes
    __id: int = 0
    name: str = ""
    
    def __init__(self):
        self.id = 0
        self.name = ""
    
    # Methods
    def get_id(self) -> int:
        pass
    
    def set_name(self, value: str) -> None:
        pass
```

### Java класс

```java
public class User {
    
    // Attributes
    private int id;
    public String name;
    
    // Constructor
    public User() {
        // TODO: Initialize attributes
    }
    
    // Methods
    public int getId() {
        // TODO: Implement method
    }
    
    public void setName(String value) {
        // TODO: Implement method
    }
}
```

## 🛠️ Расширение системы

### Добавление нового языка

1. Создать шаблон `new_language_class.j2`
2. Добавить конфигурацию в `config.py`
3. Шаблон автоматически станет доступен

### Кастомизация шаблонов

Шаблоны можно модифицировать для:
- Изменения стиля кода
- Добавления комментариев
- Генерации дополнительных методов
- Поддержки новых UML элементов

### Функции-помощники

Можно добавить новые функции в `env.globals`:

```python
self.env.globals.update({
    'custom_formatter': self._custom_formatter,
    'type_converter': self._type_converter,
})
```

## 🧪 Тестирование

### Unit тесты

```python
def test_python_generation():
    generator = CodeGenerator()
    diagram = create_test_diagram()
    
    code = generator.generate(diagram, "python")
    
    assert "class TestClass:" in code
    assert "def __init__(self):" in code
```

### Интеграционные тесты

```python
def test_all_languages():
    generator = CodeGenerator()
    diagram = create_complex_diagram()
    
    for language in generator.get_supported_languages():
        code = generator.generate(diagram, language)
        assert len(code) > 0
        assert "class" in code.lower()
```

## 📈 Планы развития

### Ближайшие улучшения

- [ ] Генерация интерфейсов
- [ ] Поддержка generic типов
- [ ] Генерация конструкторов с параметрами
- [ ] Документация в коде (JSDoc, docstrings)

### Долгосрочные планы

- [ ] Обратная инженерия (код → диаграмма)
- [ ] Настраиваемые шаблоны через UI
- [ ] Плагины для кастомных языков
- [ ] Генерация тестов

## 🔧 Отладка

### Логирование

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# В CodeGenerator
logger.debug(f"Generating {language} code for {len(diagram.nodes)} classes")
```

### Проверка шаблонов

```python
# Проверить синтаксис шаблона
try:
    template = env.get_template('python_class.j2')
except TemplateError as e:
    print(f"Template error: {e}")
```

## 📚 Ресурсы

- [Документация Jinja2](https://jinja.palletsprojects.com/)
- [UML спецификация](https://www.omg.org/spec/UML/)
- [Примеры шаблонов](../src/logiccraft/templates/)

---

**Система генерации кода LogicCraft обеспечивает гибкое и расширяемое решение для создания исходного кода из UML диаграмм!** 🎯✨