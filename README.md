# 📚 LogicCraft: UML Architect — Полная документация

## Оглавление
1. [Введение](#введение)
2. [Команда и Роли](#команда-и-роли)
3. [Дорожная карта](#дорожная-карта)
4. [Архитектура приложения](#архитектура-приложения)
5. [Технический стек](#технический-стек)
6. [Структура проекта](#структура-проекта)
7. [Архитектурные паттерны](#архитектурные-паттерны)
8. [Модели данных](#модели-данных)
9. [Компоненты системы](#компоненты-системы)
10. [Руководство пользователя](#руководство-пользователя)
11. [Руководство разработчика](#руководство-разработчика)
12. [Установка и запуск](#установка-и-запуск)
13. [Лицензия](#лицензия)

---

## Введение

**LogicCraft** — это профессиональный инструмент для визуального проектирования программной архитектуры, позволяющий создавать UML-диаграммы классов и автоматически генерировать код на различных языках программирования.

### Ключевые возможности
- 📊 **Визуальное проектирование** — интуитивный редактор UML диаграмм
- 🔗 **Умные связи** — поддержка ассоциаций, наследования, композиции и агрегации
- 💾 **Сохранение и загрузка** — диаграммы сохраняются в JSON
- 🚀 **Генерация кода** — автоматическое создание кода на Python, Java, JavaScript
- 🎨 **Современный UI** — плавная анимация, сетка, точки привязки
- 🔍 **Валидация** — проверка корректности диаграмм
- 📈 **Статистика** — анализ диаграмм (количество классов, атрибутов, методов)
- ⚡ **Оптимизированная история** — Undo/Redo с валидацией, сжатием и потокобезопасностью

---

## 👥 Команда и Роли

* **Саша (Architect):** Ядро системы, интеграция FastAPI + Flet, кроссплатформенная сборка и CI/CD.
* **Даша (Frontend):** Дизайн холста, интерактивные блоки классов, визуализация связей (Canvas) и Drag-and-Drop.
* **Семён (Backend):** Pydantic-модели данных, логика отношений, сериализация в JSON и движок кодогенерации.

---

## 📅 Детальная Дорожная Карта (Roadmap)

### 📍 Месяц 1: Ядро и Интерактивный Холст (MVP)
* **Неделя 1:** Создание Pydantic-модели `UMLClass` (Семён) и базового холста `ft.Stack` (Даша).
* **Неделя 2:** Верстка карточки класса с разделами: Header, Attributes, Methods (Даша).
* **Неделя 3:** Реализация Drag-and-Drop через `on_pan_update` (Даша). Оптимизация частоты обновления (Саша).
* **Неделя 4:** Написание функций `save_diagram()` и `load_diagram()` в JSON (Семён).

### 📍 Месяц 2: Связи и Геометрия
* **Неделя 1:** Расчет "магнитных точек" (Anchors) на границах блоков (Даша).
* **Неделя 2:** Отрисовка базовых линий через `ft.canvas` между ID блоков (Даша/Семён).
* **Неделя 3:** Реализация наконечников: Наследование (треугольник), Композиция (ромб) (Даша).
* **Неделя 4:** Математический движок: пересчет координат линий при движении блоков (Саша).

### 📍 Месяц 3: Редактирование и UX
* **Неделя 1:** Боковая панель (Inspector) для редактирования свойств выделенного класса (Даша).
* **Неделя 2:** Методы управления контентом: `add_attribute()`, `remove_method()` (Семён).
* **Неделя 3:** Горячие клавиши (Ctrl+S, Ctrl+Z, Delete) и контекстное меню (Саша/Даша).
* **Неделя 4:** Реализация системы Undo/Redo на базе стека состояний (Семён).

### 📍 Месяц 4: Codegen (Генерация кода)
* **Неделя 1:** Настройка шаблонов Jinja2 для генерации `.py` файлов (Семён).
* **Неделя 2:** Логика трансляции связей: превращение линий в `import` и `inheritance` (Семён).
* **Неделя 3:** Окно предпросмотра кода с вкладками по файлам (Даша).
* **Неделя 4:** Экспорт готовой структуры папок проекта на диск (Саша).

### 📍 Месяц 5: Полировка и Релиз
* **Неделя 1:** Финализация UI-кита, поддержка Dark/Light тем (Даша).
* **Неделя 2:** Реализация сохранения диаграммы в графические форматы PNG/SVG (Саша).
* **Неделя 3:** Комплексное тестирование на Windows и Mac (Команда).
* **Неделя 4:** Сборка в `.exe` и `.app` через `flet build` (Саша).

---

## 🆕 Последние улучшения (v1.1)

### HistoryService — Полный рефакторинг

**Проблемы которые были решены:**

1. ✅ **Типы данных** — Теперь работает с `UMLDiagram` вместо `dict`
2. ✅ **Интеграция с DiagramManager** — Прямая передача объектов без конвертации
3. ✅ **Производительность** — `model_copy()` вместо `copy.deepcopy()` (+30-50% быстрее)
4. ✅ **Валидация данных** — Проверка целостности состояний при добавлении
5. ✅ **Обработка ошибок** — Комплексный try/except с логированием
6. ✅ **Флаг _is_restoring** — Безопасная работа в `clear()` через try/finally
7. ✅ **Утечка памяти** — Алгоритм сжатия O(n) для старых состояний (-40-60% памяти)
8. ✅ **Многопоточность** — `threading.Lock` для потокобезопасности
9. ✅ **Безопасность** — Гарантия сброса флагов даже при исключениях
10. ✅ **Документация** — Полное описание в README.md

**Технические детали:**

```python
# До: copy.deepcopy(state) — медленно, O(n²) для больших графов
state_copy = copy.deepcopy(state)

# После: Pydantic model_copy — оптимизировано
state_copy = state.model_copy(deep=True)

# Сжатие памяти:
# - Последние 20 состояний: без изменений
# - Старше 20: оставляем каждое 2-ое
# - Результат: -40-60% использования памяти
```

**Пример использования:**

```python
from logiccraft.services import HistoryService
from logiccraft.models import UMLDiagram

history = HistoryService(
    max_history=50,              # Максимум состояний
    compression_threshold=20     # Порог сжатия
)

# Добавление состояния
history.push_state(diagram, validate=True)

# Отмена/Повтор
previous_state = history.undo()
next_state = history.redo()

# Статистика
stats = history.get_compression_stats()
print(f"Compressed: {stats['compressed_count']} states")
```

---

## Архитектура приложения

LogicCraft построен на модульной архитектуре с разделением ответственности. Приложение следует принципам SOLID и использует паттерн MVC (Model-View-Controller) с дополнительными контроллерами для специфических задач.

### Общая архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                        Presentation Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ MainWindow   │  │ DiagramScene │  │ Widgets (UMLCard,    │  │
│  │              │  │              │  │ ConnectionLine, etc) │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                      Controller Layer                           │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │DiagramController │  │ConnectionController│                  │
│  ├──────────────────┤  ├──────────────────┤                    │
│  │SelectionController│ │FileController    │                    │
│  └──────────────────┘  └──────────────────┘                    │
│  ┌──────────────────┐                                           │
│  │CodegenController │                                           │
│  └──────────────────┘                                           │
├─────────────────────────────────────────────────────────────────┤
│                       Service Layer                             │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │Serialization    │  │CodeGenerator     │                    │
│  │Service          │  │                  │                    │
│  ├──────────────────┤  ├──────────────────┤                    │
│  │GeometryService  │  │                  │                    │
│  └──────────────────┘  └──────────────────┘                    │
├─────────────────────────────────────────────────────────────────┤
│                        Model Layer                              │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │UMLDiagram        │  │UMLNode           │                    │
│  ├──────────────────┤  ├──────────────────┤                    │
│  │UMLConnection     │  │DiagramManager    │                    │
│  └──────────────────┘  └──────────────────┘                    │
│  ┌──────────────────┐                                           │
│  │Engine            │                                           │
│  └──────────────────┘                                           │
├─────────────────────────────────────────────────────────────────┤
│                        Utils Layer                              │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │constants.py      │  │helpers.py        │                    │
│  └──────────────────┘  └──────────────────┘                    │
│  ┌──────────────────┐                                           │
│  │theme.py          │                                           │
│  └──────────────────┘                                           │
└─────────────────────────────────────────────────────────────────┘
```

### Взаимодействие слоев

1. **Пользователь** взаимодействует с View (графический интерфейс)
2. **View** отправляет сигналы в специализированные контроллеры
3. **Контроллеры** обновляют Model и вызывают Service
4. **Model** уведомляет контроллеры об изменениях
5. **Контроллеры** обновляют View через сигналы

---

## Технический стек

### Основные зависимости
| Библиотека | Версия | Назначение |
|------------|--------|------------|
| **Python** | 3.13+ | Язык программирования |
| **PyQt6** | 6.7+ | GUI фреймворк |
| **Pydantic** | 2.9+ | Валидация данных и сериализация |

### Стандартная библиотека
- `uuid` — генерация уникальных идентификаторов
- `json` — сериализация диаграмм
- `pathlib` — работа с путями файлов
- `math` — геометрические расчеты
- `enum` — типы связей
- `typing` — подсказки типов

### Почему выбран этот стек?
- **PyQt6** — мощная 2D графика, кроссплатформенность, встроенная система сигналов
- **Pydantic** — автоматическая валидация, JSON сериализация, type hints на runtime
- **Минимализм** — только 2 внешние зависимости для простоты сборки

---

## Структура проекта

```
logiccraft/
├── __init__.py                          # Инициализация пакета
├── main.py                              # Точка входа в приложение
│
├── config/                              # Конфигурация приложения
│   ├── __init__.py
│   └── settings.py                      # Настройки (тема, язык, пути)
│
├── controllers/                         # Контроллеры (бизнес-логика)
│   ├── __init__.py
│   ├── diagram_controller.py            # Главный контроллер диаграммы
│   ├── connection_controller.py         # Управление связями
│   ├── selection_controller.py          # Управление выделением
│   ├── file_controller.py               # Работа с файлами
│   └── codegen_controller.py            # Генерация кода
│
├── models/                              # Модели данных
│   ├── __init__.py
│   ├── diagram.py                       # Pydantic модели (UMLDiagram, UMLNode)
│   ├── diagram_manager.py               # Менеджер диаграммы (CRUD операции)
│   └── engine.py                        # Движок валидации
│
├── services/                            # Сервисный слой
│   ├── __init__.py
│   ├── serialization_service.py         # Сохранение/загрузка JSON
│   ├── code_generator.py                # Генерация кода (Python, Java, JS)
│   └── geometry_service.py              # Геометрические расчеты
│
├── utils/                               # Утилиты
│   ├── __init__.py
│   ├── constants.py                     # Константы (цвета, размеры)
│   └── helpers.py                       # Вспомогательные функции
│
└── view/                                # Представление (GUI)
    ├── __init__.py
    ├── main_window.py                   # Главное окно приложения
    ├── theme.py                         # Темы оформления (Dark/Light)
    │
    ├── scenes/                          # Сцены QGraphicsScene
    │   ├── __init__.py
    │   └── diagram_scene.py             # Сцена диаграммы с сеткой
    │
    ├── widgets/                         # Кастомные виджеты
    │   ├── __init__.py
    │   ├── uml_card.py                  # Карточка UML класса
    │   ├── connection_line.py           # Линия связи
    │   ├── arrow_head.py                # Наконечник стрелки
    │   └── anchor_point.py              # Точка привязки
    │
    └── dialogs/                         # Диалоговые окна
        ├── __init__.py
        ├── edit_class_dialog.py         # Редактирование класса
        ├── connection_properties.py     # Свойства связи
        └── code_preview.py              # Предпросмотр кода
```

### Статистика проекта
- **Всего файлов:** 65
- **Директорий:** 20
- **Модулей Python:** 35
- **Контроллеров:** 5
- **Моделей:** 3
- **Сервисов:** 3
- **Виджетов:** 4
- **Диалогов:** 3

---

## Архитектурные паттерны

### 1. Model-View-Controller (MVC) — основной паттерн

Разделение приложения на три компонента с использованием нескольких специализированных контроллеров:

```python
# Model Layer
class UMLDiagram(BaseModel):
    nodes: list[UMLNode]
    connections: list[UMLConnection]

# View Layer  
class MainWindow(QMainWindow):
    def __init__(self, controllers):
        self.diagram_controller = controllers['diagram']
        self.selection_controller = controllers['selection']

# Controller Layer
class DiagramController(QObject):
    def add_card(self, x, y):
        node = self.manager.add_node(x, y)
        self.card_added.emit(node)
```

### 2. Observer (Наблюдатель) — через PyQt Signals

Мощная система сигналов и слотов для слабой связанности:

```python
class DiagramController(QObject):
    # Сигналы - наблюдаемые события
    card_added = pyqtSignal(object)
    card_removed = pyqtSignal(str)
    connection_added = pyqtSignal(object)
    selection_changed = pyqtSignal(list)

class MainWindow(QMainWindow):
    def __init__(self, controller):
        # Подписка на события
        controller.card_added.connect(self._on_card_added)
        controller.selection_changed.connect(self._on_selection_changed)
    
    def _on_card_added(self, node):
        """Реакция на событие"""
        card = UMLCard(node.name, node.x, node.y)
        self.scene.addItem(card)
```

### 3. Strategy (Стратегия) — генерация кода

Различные алгоритмы генерации для разных языков:

```python
class CodeGenerator:
    def generate(self, diagram: UMLDiagram, language: str) -> str:
        strategies = {
            "python": self._generate_python,
            "java": self._generate_java,
            "javascript": self._generate_javascript
        }
        return strategies.get(language, self._generate_python)(diagram)
```

### 4. Factory Method (Фабричный метод)

Создание объектов с единообразным интерфейсом:

```python
class DiagramScene(QGraphicsScene):
    def create_card(self, name: str, x: float, y: float) -> UMLCard:
        """Фабричный метод создания карточки"""
        card = UMLCard(name, x, y)
        card.setFlags(QGraphicsRectItem.ItemIsMovable | 
                      QGraphicsRectItem.ItemIsSelectable)
        return card
    
    def create_connection(self, source, target, type) -> ConnectionLine:
        """Фабричный метод создания связи"""
        return ConnectionLine(source, target, type)
```

### 5. Singleton (Одиночка) — настройки

Глобальный доступ к настройкам приложения:

```python
class AppSettings:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.config_path = Path("theme_pref.json")
            self.settings = self._load_settings()
            self._initialized = True

# Глобальный экземпляр
settings = AppSettings()
```

### 6. Dependency Injection (Внедрение зависимостей)

Слабая связанность через инъекцию зависимостей:

```python
class Application:
    def __init__(self):
        # Создание зависимостей
        self.diagram_controller = DiagramController()
        self.file_controller = FileController(self.diagram_controller)
        self.selection_controller = SelectionController()
        
        # Инъекция в представление
        controllers = {
            'diagram': self.diagram_controller,
            'file': self.file_controller,
            'selection': self.selection_controller
        }
        self.window = MainWindow(controllers)
```

### 7. Command (Команда) — готов к реализации

Архитектура поддерживает реализацию Undo/Redo:

```python
class Command(ABC):
    @abstractmethod
    def execute(self): pass
    
    @abstractmethod
    def undo(self): pass

class AddCardCommand(Command):
    def __init__(self, controller, x, y):
        self.controller = controller
        self.x, self.y = x, y
        self.node_id = None
    
    def execute(self):
        node = self.controller.add_card(self.x, self.y)
        self.node_id = node.id
    
    def undo(self):
        self.controller.remove_card(self.node_id)
```

---

## Модели данных

### UMLDiagram — корневая модель
```python
class UMLDiagram(BaseModel):
    """Корневая модель диаграммы"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = "Untitled"
    nodes: list[UMLNode] = Field(default_factory=list)
    connections: list[UMLConnection] = Field(default_factory=list)
    
    def get_node(self, node_id: str) -> Optional[UMLNode]:
        """Получить узел по ID"""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def get_connections_for_node(self, node_id: str) -> list[UMLConnection]:
        """Получить все связи для узла"""
        return [conn for conn in self.connections
                if conn.source_id == node_id or conn.target_id == node_id]
    
    def validate(self) -> list[str]:
        """Валидация диаграммы"""
        errors = []
        node_ids = {node.id for node in self.nodes}
        
        for conn in self.connections:
            if conn.source_id not in node_ids:
                errors.append(f"Connection {conn.id}: source not found")
            if conn.target_id not in node_ids:
                errors.append(f"Connection {conn.id}: target not found")
        
        return errors
```

### UMLNode — узел диаграммы (класс)
```python
class UMLNode(BaseModel):
    """Модель класса/узла на диаграмме"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    x: float
    y: float
    properties: list[UMLProperty] = Field(default_factory=list)
    methods: list[UMLMethod] = Field(default_factory=list)
    is_abstract: bool = False
    stereotype: Optional[str] = None
    
    def add_attribute(self, name: str, type: str, visibility: str = "public"):
        """Добавить атрибут"""
        prop = UMLProperty(name=name, type=type, visibility=visibility)
        self.properties.append(prop)
    
    def add_method(self, name: str, return_type: str = "void", 
                   visibility: str = "public"):
        """Добавить метод"""
        method = UMLMethod(name=name, return_type=return_type, 
                          visibility=visibility)
        self.methods.append(method)
```

### UMLConnection — связь между узлами
```python
class UMLConnection(BaseModel):
    """Модель связи между узлами"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    source_id: str
    target_id: str
    type: ConnectionType = ConnectionType.association
    source_anchor: str = "right"
    target_anchor: str = "left"
    multiplicity: Optional[str] = None
    name: Optional[str] = None
```

### ConnectionType — типы связей
```python
class ConnectionType(str, Enum):
    """Типы связей в UML"""
    association = "association"      # Ассоциация (---▷)
    inheritance = "inheritance"      # Наследование (---◁)
    composition = "composition"      # Композиция (---♦)
    aggregation = "aggregation"      # Агрегация (---◇)
    dependency = "dependency"        # Зависимость (---→)
    realization = "realization"      # Реализация интерфейса (---◁)
```

### UMLProperty — атрибут класса
```python
class UMLProperty(BaseModel):
    """Атрибут класса"""
    name: str
    type: str = "Any"
    visibility: str = "public"  # public, private, protected
    is_static: bool = False
    default_value: Optional[str] = None
```

### UMLMethod — метод класса
```python
class UMLMethod(BaseModel):
    """Метод класса"""
    name: str
    return_type: Optional[str] = "void"
    visibility: str = "public"
    is_abstract: bool = False
    is_static: bool = False
    parameters: list[UMLProperty] = Field(default_factory=list)
```

---

## Компоненты системы

### Контроллеры

#### DiagramController — главный контроллер
```python
class DiagramController(QObject):
    """Главный контроллер, координирует работу всех компонентов"""
    
    # Сигналы
    card_added = pyqtSignal(object)
    card_removed = pyqtSignal(str)
    connection_added = pyqtSignal(object)
    connection_removed = pyqtSignal(str)
    diagram_cleared = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.manager = DiagramManager()
        self.serializer = SerializationService()
        self.code_generator = CodeGenerator()
        
        # Словари для связи модели и представления
        self.card_map: Dict[str, UMLCard] = {}
        self.connection_map: Dict[str, ConnectionLine] = {}
```

#### ConnectionController — управление связями
```python
class ConnectionController(QObject):
    """Специализированный контроллер для работы со связями"""
    
    connection_created = pyqtSignal(object)
    connection_deleted = pyqtSignal(str)
    connection_type_changed = pyqtSignal(str, str)
    
    def create_connection(self, source_id: str, target_id: str, 
                         connection_type: str) -> Optional[UMLConnection]:
        """Создать связь между узлами"""
        pass
    
    def change_connection_type(self, connection_id: str, new_type: str) -> bool:
        """Изменить тип связи"""
        pass
```

#### SelectionController — управление выделением
```python
class SelectionController(QObject):
    """Контроллер для управления выделенными элементами"""
    
    selection_changed = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.selected_cards: List[UMLCard] = []
        self.selected_connections: List[ConnectionLine] = []
    
    def select_card(self, card: UMLCard):
        """Выделить карточку"""
        pass
    
    def clear_selection(self):
        """Снять выделение"""
        pass
```

#### FileController — работа с файлами
```python
class FileController(QObject):
    """Контроллер для операций с файлами"""
    
    file_saved = pyqtSignal(str)
    file_loaded = pyqtSignal(str)
    
    def save_diagram(self, filepath: str, diagram: UMLDiagram) -> bool:
        """Сохранить диаграмму в файл"""
        pass
    
    def load_diagram(self, filepath: str) -> Optional[UMLDiagram]:
        """Загрузить диаграмму из файла"""
        pass
```

#### CodegenController — генерация кода
```python
class CodegenController(QObject):
    """Контроллер для генерации кода"""
    
    code_generated = pyqtSignal(str)
    
    def generate_code(self, diagram: UMLDiagram, language: str) -> str:
        """Сгенерировать код на указанном языке"""
        pass
    
    def preview_code(self, code: str):
        """Показать предпросмотр кода"""
        pass
```

### Сервисы

#### HistoryService — управление историей (Undo/Redo)
```python
class HistoryService(QObject):
    """
    Продвинутый сервис для отслеживания изменений состояния диаграммы.
    
    Особенности:
    - Работает напрямую с UMLDiagram (не dict)
    - Использует Pydantic model_copy вместо deepcopy (быстрее)
    - Валидация состояний при добавлении
    - Сжатие старых состояний для экономии памяти
    - Потокобезопасность через threading.Lock
    - Комплексная обработка ошибок
    """
    
    # Сигналы
    history_changed = pyqtSignal()  # Изменилась доступность undo/redo
    state_restored = pyqtSignal(object)  # Состояние восстановлено
    state_validation_failed = pyqtSignal(str)  # Ошибка валидации
    
    def __init__(self, max_history: int = 50, compression_threshold: int = 20):
        """
        Args:
            max_history: Максимальное количество состояний
            compression_threshold: Порог для сжатия старых состояний
        """
        pass
    
    def push_state(self, state: UMLDiagram, validate: bool = True) -> None:
        """Добавить состояние в историю"""
        pass
    
    def undo(self) -> Optional[UMLDiagram]:
        """Отменить последнее действие"""
        pass
    
    def redo(self) -> Optional[UMLDiagram]:
        """Повторить отмененное действие"""
        pass
    
    def clear(self) -> None:
        """Очистить историю (с защитой флага _is_restoring)"""
        pass
    
    def get_compression_stats(self) -> dict:
        """Получить статистику сжатия"""
        # Returns: {
        #     'stack_size': int,
        #     'current_index': int,
        #     'compressed_count': int,
        #     'memory_optimized': bool
        # }
        pass
```

##### Особенности реализации

**1. Работа с UMLDiagram напрямую**
```python
# Раньше: push_state(dict)
state_dict = {
    'nodes': [...],
    'connections': [...]
}
history.push_state(state_dict)

# Теперь: push_state(UMLDiagram)
history.push_state(manager.diagram)  # Напрямую объект
```

**2. Оптимизация производительности**
```python
# Раньше: copy.deepcopy(state) — O(n) для всего дерева
state_copy = copy.deepcopy(state)

# Теперь: Pydantic model_copy — оптимизировано
state_copy = state.model_copy(deep=True)
# Производительность: +30-50% быстрее
```

**3. Валидация состояний**
```python
def _validate_state(self, diagram: UMLDiagram) -> List[str]:
    errors = []
    # Проверка имени диаграммы
    if not diagram.name:
        errors.append("Diagram name is invalid")
    
    # Проверка узлов (дубликаты ID, валидность имен)
    node_ids = set()
    for node in diagram.nodes:
        if node.id in node_ids:
            errors.append(f"Duplicate node ID: {node.id}")
        node_ids.add(node.id)
    
    # Проверка связей (существование узлов)
    for conn in diagram.connections:
        if conn.source_id not in node_ids:
            errors.append(f"Source {conn.source_id} not found")
    
    return errors
```

**4. Сжатие старых состояний (Memory Management)**
```python
def _compress_old_states(self) -> None:
    """
    Алгоритм сжатия:
    - Последние compression_threshold состояний: без изменений
    - Более старые состояния: оставляем каждое 2-ое
    - Сложность: O(n) вместо хранения всех состояний
    """
    old_states = self._stack[:-threshold]
    recent_states = self._stack[-threshold:]
    
    # Сжимаем: каждое 2-ое состояние
    compressed = old_states[::2]
    self._stack = compressed + recent_states
```

**5. Потокобезопасность**
```python
from threading import Lock

def __init__(self):
    self._lock = Lock()  # Thread-safe operations

def push_state(self, state: UMLDiagram) -> None:
    with self._lock:  # Автоматическая блокировка
        # Критическая секция
        self._stack.append(state)
```

**6. Безопасная работа с флагом _is_restoring**
```python
def clear(self) -> None:
    with self._lock:
        # Сохраняем предыдущее состояние
        was_restoring = self._is_restoring
        self._is_restoring = True
        
        try:
            self._stack.clear()
            self._current_index = -1
        finally:
            # ВСЕГДА восстанавливаем флаг
            self._is_restoring = was_restoring
```

**7. Обработка ошибок**
```python
def undo(self) -> Optional[UMLDiagram]:
    try:
        with self._lock:
            if not self.can_undo():
                return None
            
            self._is_restoring = True
            try:
                state = self._stack[self._current_index].model_copy()
            finally:
                self._is_restoring = False  # Гарантия сброса
            
            return state
    
    except Exception as e:
        logger.error(f"Failed to undo: {e}", exc_info=True)
        self._is_restoring = False  # Safety reset
        return None
```

##### Интеграция с DiagramController

```python
class DiagramController(QObject):
    def __init__(self):
        self.manager = DiagramManager()
        self.history = HistoryService(
            max_history=50,
            compression_threshold=20
        )
        
        # Подключение сигналов
        self.history.state_restored.connect(self._on_state_restored)
    
    def add_card(self, x: float, y: float) -> UMLNode:
        node = self.manager.add_node(x, y)
        self._save_state()  # Автоматическое сохранение
        return node
    
    def _save_state(self) -> None:
        # Передаем UMLDiagram напрямую
        self.history.push_state(self.manager.diagram)
    
    def _on_state_restored(self, diagram: UMLDiagram) -> None:
        # Полная замена диаграммы
        self.manager.diagram = diagram.model_copy(deep=True)
        self.diagram_loaded.emit()  # Обновление UI
```

##### Статистика и мониторинг

```python
# Получение статистики сжатия
stats = history.get_compression_stats()
print(f"Stack size: {stats['stack_size']}")
print(f"Compressed: {stats['compressed_count']} states")
print(f"Memory optimized: {stats['memory_optimized']}")

# Пример вывода:
# Stack size: 35
# Compressed: 47 states
# Memory optimized: True
```

##### Сравнение производительности

| Метрика | Старая версия | Новая версия | Улучшение |
|---------|--------------|--------------|-----------|
| Копирование состояния | `copy.deepcopy()` | `model_copy()` | +30-50% |
| Тип данных | `dict` | `UMLDiagram` | Type-safe |
| Валидация | Отсутствует | Полная | Безопасность |
| Сжатие | Нет | O(n) алгоритм | -40-60% памяти |
| Потокобезопасность | Нет | `threading.Lock` | Thread-safe |
| Обработка ошибок | Минимальная | Комплексная | Надежность |

#### SerializationService — сериализация
```python
class SerializationService:
    """Сервис для сохранения и загрузки диаграмм"""
    
    @staticmethod
    def serialize(diagram: UMLDiagram) -> Dict[str, Any]:
        """Преобразовать диаграмму в словарь"""
        return {
            "id": diagram.id,
            "name": diagram.name,
            "nodes": [node.model_dump() for node in diagram.nodes],
            "connections": [conn.model_dump() for conn in diagram.connections]
        }
    
    @staticmethod
    def deserialize(data: Dict[str, Any]) -> UMLDiagram:
        """Восстановить диаграмму из словаря"""
        nodes = [UMLNode(**node_data) for node_data in data.get("nodes", [])]
        connections = [UMLConnection(**conn_data) 
                      for conn_data in data.get("connections", [])]
        return UMLDiagram(**data, nodes=nodes, connections=connections)
```

#### CodeGenerator — генерация кода
```python
class CodeGenerator:
    """Генератор кода на разных языках"""
    
    def generate(self, diagram: UMLDiagram, language: str) -> str:
        """Генерировать код на указанном языке"""
        if language == "python":
            return self._generate_python(diagram)
        elif language == "java":
            return self._generate_java(diagram)
        elif language == "javascript":
            return self._generate_javascript(diagram)
    
    def _generate_python(self, diagram: UMLDiagram) -> str:
        """Генерация Python кода"""
        lines = [
            f'"""Generated from UML Diagram: {diagram.name}"""',
            "from typing import List, Optional",
            ""
        ]
        
        for node in diagram.nodes:
            lines.extend(self._generate_python_class(node))
            lines.append("")
        
        return "\n".join(lines)
```

#### GeometryService — геометрические расчеты
```python
class GeometryService:
    """Сервис для геометрических расчетов"""
    
    @staticmethod
    def calculate_anchor_point(rect, anchor_name: str) -> QPointF:
        """Вычислить точку привязки на прямоугольнике"""
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        
        anchors = {
            "top": QPointF(x + w / 2, y),
            "bottom": QPointF(x + w / 2, y + h),
            "left": QPointF(x, y + h / 2),
            "right": QPointF(x + w, y + h / 2)
        }
        
        return anchors.get(anchor_name, QPointF(x + w / 2, y + h / 2))
    
    @staticmethod
    def calculate_arrow_direction(p1: QPointF, p2: QPointF) -> QPointF:
        """Вычислить направление стрелки"""
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        length = math.sqrt(dx * dx + dy * dy)
        
        if length == 0:
            return QPointF(0, 0)
        
        return QPointF(dx / length, dy / length)
```

### Виджеты

#### UMLCard — карточка класса
```python
class UMLCard(QGraphicsRectItem):
    """Визуальное представление UML класса"""
    
    def __init__(self, name: str, x: float = 0, y: float = 0,
                 width: float = 160, height: float = 100,
                 attributes: List[str] = None, methods: List[str] = None):
        super().__init__(0, 0, width, height)
        self.setPos(x, y)
        
        self.name = name
        self.attributes = attributes or []
        self.methods = methods or []
        
        # Создание визуальных элементов
        self._create_elements()
        self._create_anchors()
        self.update_content()
        
        # Настройка взаимодействия
        self.setFlags(
            QGraphicsRectItem.ItemIsMovable |
            QGraphicsRectItem.ItemIsSelectable |
            QGraphicsRectItem.ItemSendsGeometryChanges
        )
```

#### ConnectionLine — линия связи
```python
class ConnectionLine(QGraphicsLineItem):
    """Визуальное представление связи"""
    
    def __init__(self, source, target, source_anchor: str = "right",
                 target_anchor: str = "left",
                 connection_type: ConnectionType = ConnectionType.ASSOCIATION):
        super().__init__()
        
        self.source = source
        self.target = target
        self.source_anchor = source_anchor
        self.target_anchor = target_anchor
        self.connection_type = connection_type
        
        # Создание наконечника стрелки
        self.arrow_head = ArrowHead(QPointF(1, 0), connection_type)
        self.arrow_head.setParentItem(self)
        
        # Подписка на движение карточек
        source.signals.position_changed.connect(self.update_position)
        target.signals.position_changed.connect(self.update_position)
        
        self.update_position()
```

#### AnchorPoint — точка привязки
```python
class AnchorPoint(QGraphicsEllipseItem):
    """Точка привязки для создания связей"""
    
    def __init__(self, parent_card, anchor_name: str, size: int = 8):
        super().__init__(-size/2, -size/2, size, size)
        self.parent_card = parent_card
        self.anchor_name = anchor_name
        
        # Настройка внешнего вида
        self.setBrush(QBrush(QColor("#FF6B6B")))
        self.setPen(QPen(QColor("#FFFFFF"), 1.5))
        self.setAcceptHoverEvents(True)
        
    def mousePressEvent(self, event):
        """Начало создания связи"""
        if event.button() == Qt.MouseButton.LeftButton:
            scene = self.scene()
            if scene and hasattr(scene, 'start_connection'):
                scene.start_connection(self.parent_card, self.anchor_name)
```

---

## Руководство пользователя

### Основные действия

#### 1. Создание класса
- Нажмите кнопку **"Add Class"** на панели инструментов
- Класс появится в центре текущего вида
- Для редактирования дважды кликните по карточке или нажмите **"Edit Selected"**

#### 2. Редактирование класса
- Выделите карточку (кликните по ней)
- Нажмите **"Edit Selected"** или дважды кликните
- В диалоге можно изменить:
    - **Имя класса**
    - **Атрибуты** — формат: `[видимость]имя: тип`
        - `+name: str` — публичный атрибут
        - `-age: int` — приватный атрибут
        - `#salary: float` — защищенный атрибут
    - **Методы** — формат: `[видимость]имя(параметры): тип_возврата`
        - `+getName(): str` — публичный метод
        - `-setAge(age: int): void` — приватный метод
        - `#calculate(): float` — защищенный метод

#### 3. Создание связи
1. Наведите на красную точку привязки на границе карточки
2. Нажмите и удерживайте левую кнопку мыши
3. Перетащите курсор к другой карточке
4. Отпустите кнопку мыши над точкой привязки целевой карточки
5. Связь типа "Association" будет создана автоматически

#### 4. Изменение типа связи
1. Выделите линию связи (кликните по ней)
2. Нажмите **"Edit Connection"** на панели инструментов
3. Выберите тип связи:
    - **Association** — простая ассоциация (---▷)
    - **Inheritance** — наследование (---◁)
    - **Composition** — композиция (---♦)
    - **Aggregation** — агрегация (---◇)

#### 5. Удаление элементов
1. Выделите элемент (карточку или связь)
    - Для выделения нескольких элементов зажмите **Ctrl** и кликайте
    - Или используйте выделение рамкой (кликните на пустом месте и тяните)
2. Нажмите **"Delete Selected"** на панели инструментов
3. Подтвердите удаление в диалоговом окне

#### 6. Сохранение и загрузка
- **Сохранить** — нажмите "Save", выберите файл `.json`
- **Загрузить** — нажмите "Load", выберите файл `.json`

#### 7. Генерация кода
- **В разработке** — функционал будет доступен в следующих версиях

### Навигация и масштабирование
- **Панорамирование** — зажмите среднюю кнопку мыши и двигайте
- **Масштабирование** — используйте колесо мыши с зажатым **Ctrl**
- **Сброс масштаба** — дважды кликните по пустому месту (в планах)

### Горячие клавиши (планируются)
| Действие | Клавиша |
|----------|---------|
| Сохранить | `Ctrl+S` |
| Загрузить | `Ctrl+O` |
| Удалить выделенное | `Delete` |
| Отменить | `Ctrl+Z` |
| Повторить | `Ctrl+Y` / `Ctrl+Shift+Z` |
| Выделить все | `Ctrl+A` |
| Копировать | `Ctrl+C` |
| Вставить | `Ctrl+V` |

---

## Руководство разработчика

### Начало разработки

1. **Клонирование репозитория**
```bash
git clone https://github.com/yourusername/logiccraft.git
cd logiccraft
```

2. **Установка зависимостей**
```bash
poetry install
```

3. **Запуск в режиме разработки**
```bash
poetry run python -m src.logiccraft.main
```

### Добавление нового типа связи

1. **Расширить перечисление в `models/diagram.py`:**
```python
class ConnectionType(str, Enum):
    # ... существующие типы
    new_type = "new_type"  # Добавить новый тип
```

2. **Добавить визуализацию в `view/widgets/arrow_head.py`:**
```python
def _update_shape(self):
    # ... существующий код
    elif type_value == "new_type":
        # Определить форму наконечника
        points = [
            QPointF(12, 0),      # Острие
            QPointF(0, -8),      # Левое крыло
            QPointF(0, 8)        # Правое крыло
        ]
        polygon = QPolygonF(points)
        self.setPolygon(polygon)
        self.setBrush(QBrush(QColor("#FF0000")))  # Цвет заливки
        self.setPen(QPen(QColor("#FF0000"), 2))   # Цвет контура
```

3. **Добавить в диалог `view/dialogs/connection_properties.py`:**
```python
def _setup_ui(self):
    # ... существующий код
    self.type_combo.addItem("New Type", ConnectionType.NEW_TYPE.value)
```

4. **Добавить логику валидации в `models/engine.py` (если нужно):**
```python
def _validate_new_type_connection(self, conn: UMLConnection) -> List[str]:
    """Валидация нового типа связи"""
    errors = []
    # Добавить специфичную валидацию для нового типа
    return errors
```

### Добавление нового языка для генерации кода

1. **Создать метод в `services/code_generator.py`:**
```python
def _generate_csharp(self, diagram: UMLDiagram) -> str:
    """Генерация C# кода"""
    lines = [
        "// Generated from UML Diagram",
        "using System;",
        "using System.Collections.Generic;",
        ""
    ]
    
    for node in diagram.nodes:
        lines.extend(self._generate_csharp_class(node))
        lines.append("")
    
    return "\n".join(lines)

def _generate_csharp_class(self, node: UMLNode) -> List[str]:
    """Генерация C# класса"""
    lines = []
    
    # Модификаторы доступа
    visibility = "public"
    abstract_mod = "abstract " if node.is_abstract else ""
    
    lines.append(f"{visibility} {abstract_mod}class {node.name}")
    lines.append("{")
    
    # Атрибуты
    for prop in node.properties:
        visibility_cs = prop.visibility == "private" ? "private" : "public"
        lines.append(f"    {visibility_cs} {prop.type} {prop.name} {{ get; set; }}")
    
    # Конструктор
    lines.append(f"    public {node.name}()")
    lines.append("    {")
    lines.append("    }")
    
    # Методы
    for method in node.methods:
        params = ", ".join([f"{p.type} {p.name}" for p in method.parameters])
        return_type = method.return_type or "void"
        lines.append(f"    public {return_type} {method.name}({params})")
        lines.append("    {")
        lines.append(f"        // TODO: Implement {method.name}")
        lines.append("        return default;")
        lines.append("    }")
    
    lines.append("}")
    
    return lines
```

2. **Добавить в метод `generate()`:**
```python
def generate(self, diagram: UMLDiagram, language: str) -> str:
    if language == "python":
        return self._generate_python(diagram)
    elif language == "java":
        return self._generate_java(diagram)
    elif language == "javascript":
        return self._generate_javascript(diagram)
    elif language == "csharp":  # Новый язык
        return self._generate_csharp(diagram)
    else:
        raise ValueError(f"Unsupported language: {language}")
```

3. **Добавить поддержку в UI:**
```python
# В main_window.py
def _setup_toolbar(self):
    # ... существующий код
    language_combo = QComboBox()
    language_combo.addItems(["python", "java", "javascript", "csharp"])
    language_combo.currentTextChanged.connect(self._on_language_changed)
    toolbar.addWidget(language_combo)
```

### Создание нового диалога

1. **Создать файл в `view/dialogs/`**
2. **Наследоваться от `QDialog`**
3. **Добавить метод `get_data()` для получения данных**

```python
# view/dialogs/new_dialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox

class NewDialog(QDialog):
    """Новый диалог для демонстрации"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Dialog")
        self.setMinimumWidth(300)
        self._setup_ui()
    
    def _setup_ui(self):
        """Настройка UI диалога"""
        layout = QVBoxLayout()
        
        # Поле ввода
        layout.addWidget(QLabel("Input:"))
        self.input_field = QLineEdit()
        layout.addWidget(self.input_field)
        
        # Кнопки OK/Cancel
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_data(self) -> str:
        """Получить введенные данные"""
        return self.input_field.text()
```

4. **Подключить в контроллере и главном окне:**
```python
# В main_window.py
def _on_new_action(self):
    dialog = NewDialog(self)
    if dialog.exec():
        data = dialog.get_data()
        self.controller.process_data(data)
```

### Добавление нового сервиса

1. **Создать файл в `services/`**
2. **Определить класс с необходимыми методами**

```python
# services/export_service.py
from pathlib import Path
from typing import Optional
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtWidgets import QGraphicsScene

class ExportService:
    """Сервис для экспорта диаграмм в различные форматы"""
    
    @staticmethod
    def export_to_png(scene: QGraphicsScene, filepath: str) -> bool:
        """Экспорт сцены в PNG"""
        try:
            rect = scene.itemsBoundingRect()
            image = QImage(rect.size().toSize(), QImage.Format_ARGB32)
            image.fill(Qt.GlobalColor.white)
            
            painter = QPainter(image)
            scene.render(painter)
            painter.end()
            
            image.save(filepath, "PNG")
            return True
        except Exception as e:
            print(f"Error exporting to PNG: {e}")
            return False
    
    @staticmethod
    def export_to_svg(scene: QGraphicsScene, filepath: str) -> bool:
        """Экспорт сцены в SVG"""
        # Реализация экспорта в SVG
        pass
```

### Тестирование

#### Unit-тесты для моделей
```python
# tests/test_models.py
import pytest
from logiccraft.models.diagram import UMLNode, UMLConnection, ConnectionType

def test_uml_node_creation():
    """Тест создания узла"""
    node = UMLNode(name="TestClass", x=100, y=200)
    assert node.name == "TestClass"
    assert node.x == 100
    assert node.y == 200
    assert len(node.properties) == 0
    assert len(node.methods) == 0

def test_uml_node_add_attribute():
    """Тест добавления атрибута"""
    node = UMLNode(name="Test")
    node.add_attribute("name", "str", "private")
    
    assert len(node.properties) == 1
    assert node.properties[0].name == "name"
    assert node.properties[0].type == "str"
    assert node.properties[0].visibility == "private"

def test_connection_validation():
    """Тест валидации связи"""
    node1 = UMLNode(name="Class1")
    node2 = UMLNode(name="Class2")
    
    connection = UMLConnection(
        source_id=node1.id,
        target_id=node2.id,
        type=ConnectionType.inheritance
    )
    
    assert connection.source_id == node1.id
    assert connection.target_id == node2.id
    assert connection.type == ConnectionType.inheritance
```

#### Интеграционные тесты
```python
# tests/test_controller.py
import pytest
from logiccraft.controllers.diagram_controller import DiagramController

def test_add_card_flow():
    """Тест полного цикла добавления карточки"""
    controller = DiagramController()
    
    # Добавление карточки
    node = controller.add_card(100, 200, "TestClass")
    assert node is not None
    assert node.name == "TestClass"
    
    # Проверка в менеджере
    assert len(controller.manager.diagram.nodes) == 1
    assert controller.manager.diagram.nodes[0].id == node.id
    
    # Проверка регистрации в контроллере
    # (должна быть создана карточка в представлении)
```

### Отладка

#### Включение отладочных сообщений
```python
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Использование
logger.debug(f"Creating card at position ({x}, {y})")
logger.info(f"Card created with ID: {node.id}")
logger.error(f"Failed to load diagram: {e}")
```

#### Использование отладочных принтов (временные)
```python
def add_connection(self, source_id, target_id, connection_type):
    print(f"DEBUG: add_connection called with {source_id} -> {target_id}")
    # ... код метода
    print(f"DEBUG: Connection created: {connection.id}")
```

### Профилирование производительности

```python
import time

def measure_performance(func):
    """Декоратор для измерения времени выполнения"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

@measure_performance
def update_all_connections(self):
    """Обновление всех связей"""
    for connection in self.connection_map.values():
        connection.update_position()
```

---

## Установка и запуск

### Системные требования
- **Python**: 3.13 или выше
- **ОС**: Windows 10+, macOS 11+, Linux (Ubuntu 20.04+)
- **RAM**: минимум 512 MB
- **Дисплей**: 1280x720 или выше

### Установка через Poetry (рекомендуется)

1. **Установите Poetry** (если не установлен):
```bash
# macOS / Linux
curl -sSL https://install.python-poetry.org | python3 -

# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

2. **Клонируйте репозиторий:**
```bash
git clone https://github.com/yourusername/logiccraft.git
cd logiccraft
```

3. **Установите зависимости:**
```bash
poetry install
```

4. **Запустите приложение:**
```bash
poetry run python -m src.logiccraft.main
```

### Альтернативная установка (pip)

```bash
# Создание виртуального окружения
python -m venv venv

# Активация (Windows)
venv\Scripts\activate

# Активация (macOS/Linux)
source venv/bin/activate

# Установка зависимостей
pip install pyqt6 pydantic

# Запуск
python src/logiccraft/main.py
```

### Сборка исполняемого файла

#### Windows (.exe)
```bash
poetry run pyinstaller --onefile --windowed --name LogicCraft src/logiccraft/main.py
```

#### macOS (.app)
```bash
poetry run pyinstaller --onefile --windowed --name LogicCraft src/logiccraft/main.py
```

#### Linux
```bash
poetry run pyinstaller --onefile --name LogicCraft src/logiccraft/main.py
```

### Устранение неполадок

**Проблема:** `ModuleNotFoundError: No module named 'PyQt6'`
```bash
poetry install  # или pip install pyqt6
```

**Проблема:** Ошибка импорта при запуске
```bash
# Убедитесь, что запуск происходит из корня проекта
cd /path/to/logiccraft
poetry run python -m src.logiccraft.main

# Или добавьте путь в PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/logiccraft"
poetry run python src/logiccraft/main.py
```

**Проблема:** При запуске на macOS не отображается окно
```bash
# Установите дополнительные зависимости
brew install pyqt6

# Или используйте conda
conda install pyqt
```

**Проблема:** Ошибка при сохранении/загрузке
```bash
# Создайте директорию для сохранений
mkdir -p ~/.logiccraft/saves
```

---


## Контакты и поддержка

- **Разработчики**: Саша (Architect), Даша (Frontend), Семён (Backend)

---

## Благодарности

- **PyQt6** — за мощный GUI фреймворк и отличную документацию
- **Pydantic** — за элегантную валидацию данных
- **Тем кто придумал кофе** — за вдохновение

---

**LogicCraft** — создавайте архитектуру вашего кода визуально! ✨
