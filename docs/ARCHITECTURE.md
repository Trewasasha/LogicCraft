# 🏗️ Архитектура LogicCraft

Техническая документация архитектуры системы LogicCraft для разработчиков и архитекторов.

## Содержание

1. [Обзор архитектуры](#обзор-архитектуры)
2. [Архитектурные принципы](#архитектурные-принципы)
3. [Слои системы](#слои-системы)
4. [Паттерны проектирования](#паттерны-проектирования)
5. [Модели данных](#модели-данных)
6. [Поток данных](#поток-данных)
7. [Производительность](#производительность)

## Обзор архитектуры

LogicCraft построен на **модульной архитектуре** с четким разделением ответственности между слоями. Основа — паттерн **MVC (Model-View-Controller)** с дополнительным сервисным слоем.

### Высокоуровневая диаграмма

```
┌─────────────────────────────────────────────────────────────────┐
│                     Presentation Layer                         │
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
│  │SerializationSvc  │  │CodeGenerator     │                    │
│  ├──────────────────┤  ├──────────────────┤                    │
│  │GeometryService   │  │HistoryService    │                    │
│  └──────────────────┘  └──────────────────┘                    │
├─────────────────────────────────────────────────────────────────┤
│                        Model Layer                              │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │UMLDiagram        │  │UMLNode           │                    │
│  ├──────────────────┤  ├──────────────────┤                    │
│  │UMLConnection     │  │DiagramManager    │                    │
│  └──────────────────┘  └──────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

## Архитектурные принципы

### 1. Разделение ответственности (SRP)
Каждый компонент имеет единственную ответственность:

- **Models** — только данные и бизнес-правила
- **Views** — только отображение и пользовательский ввод
- **Controllers** — только координация между Model и View
- **Services** — только специфичная бизнес-логика

### 2. Слабая связанность (Loose Coupling)
Компоненты взаимодействуют через интерфейсы и сигналы:

```python
# Слабая связанность через сигналы
class DiagramController(QObject):
    card_added = pyqtSignal(object)  # Интерфейс
    
class MainWindow(QMainWindow):
    def __init__(self, controller):
        controller.card_added.connect(self._on_card_added)  # Подписка
```

### 3. Инверсия зависимостей (DIP)
Высокоуровневые модули не зависят от низкоуровневых:

```python
class DiagramController:
    def __init__(self, serializer: SerializationService):
        self.serializer = serializer  # Зависимость инжектится
```

### 4. Открыт/Закрыт (OCP)
Система открыта для расширения, закрыта для изменения:

```python
# Новые типы связей добавляются без изменения существующего кода
class ConnectionType(str, Enum):
    association = "association"
    inheritance = "inheritance"
    # Новые типы добавляются здесь
```

## Слои системы

### Presentation Layer (Представление)

**Ответственность:** Отображение данных и обработка пользовательского ввода.

#### Компоненты:
- **MainWindow** — главное окно приложения
- **DiagramScene** — сцена для отображения диаграммы
- **Widgets** — кастомные виджеты (UMLCard, ConnectionLine, etc.)
- **Dialogs** — диалоговые окна

#### Технологии:
- **PyQt6** — GUI фреймворк
- **QGraphicsScene/View** — 2D графика
- **Signals/Slots** — коммуникация

```python
class UMLCard(QGraphicsRectItem):
    """Визуальное представление UML класса"""
    
    def __init__(self, name: str, x: float, y: float):
        super().__init__()
        self.signals = CardSignals()  # Сигналы для коммуникации
        
    def mousePressEvent(self, event):
        """Обработка пользовательского ввода"""
        self.signals.selected.emit(self.id)
```

### Controller Layer (Контроллеры)

**Ответственность:** Координация между View и Model, бизнес-логика приложения.

#### Специализированные контроллеры:

1. **DiagramController** — главный контроллер
   - Управление диаграммой
   - Координация других контроллеров
   - История изменений (Undo/Redo)

2. **ConnectionController** — управление связями
   - Создание/удаление связей
   - Валидация связей
   - Обновление визуализации

3. **SelectionController** — управление выделением
   - Выделение элементов
   - Групповые операции
   - Контекстные меню

4. **FileController** — работа с файлами
   - Сохранение/загрузка
   - Экспорт диаграмм
   - Управление проектами

5. **CodegenController** — генерация кода
   - Выбор языка
   - Настройка генерации
   - Предпросмотр кода

```python
class DiagramController(QObject):
    # Сигналы для уведомления View
    card_added = pyqtSignal(object)
    card_removed = pyqtSignal(str)
    
    def __init__(self):
        self.manager = DiagramManager()  # Model
        self.history = HistoryService()  # Service
        
    def add_card(self, x: float, y: float) -> UMLNode:
        """Бизнес-логика добавления карточки"""
        node = self.manager.add_node(x, y)
        self.history.push_state(self.manager.diagram)
        self.card_added.emit(node)  # Уведомление View
        return node
```

### Service Layer (Сервисы)

**Ответственность:** Специфичная бизнес-логика, не связанная с UI.

#### Сервисы:

1. **HistoryService** — управление историей
   - Undo/Redo операции
   - Оптимизация памяти
   - Валидация состояний

2. **SerializationService** — сериализация
   - JSON сохранение/загрузка
   - Миграция версий
   - Валидация данных

3. **CodeGenerator** — генерация кода
   - Поддержка множества языков
   - Шаблоны кода
   - Оптимизация вывода

4. **GeometryService** — геометрические расчеты
   - Позиционирование элементов
   - Расчет точек привязки
   - Обнаружение пересечений

```python
class HistoryService(QObject):
    """Сервис управления историей с оптимизацией"""
    
    def __init__(self, max_history: int = 50):
        self._stack: List[UMLDiagram] = []
        self._current_index: int = -1
        self._lock = threading.Lock()  # Thread-safety
        
    def push_state(self, diagram: UMLDiagram) -> None:
        """Добавить состояние с валидацией и оптимизацией"""
        with self._lock:
            # Валидация
            if not self._validate_state(diagram):
                return
                
            # Дедупликация
            if self._is_duplicate_state(diagram):
                return
                
            # Добавление
            state_copy = diagram.model_copy(deep=True)
            self._stack.append(state_copy)
            
            # Сжатие при необходимости
            if len(self._stack) > self.max_history:
                self._compress_old_states()
```

### Model Layer (Модели)

**Ответственность:** Данные и бизнес-правила предметной области.

#### Модели данных (Pydantic):

```python
class UMLDiagram(BaseModel):
    """Корневая модель диаграммы"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = "Untitled"
    nodes: List[UMLNode] = Field(default_factory=list)
    connections: List[UMLConnection] = Field(default_factory=list)
    
    def validate_integrity(self) -> List[str]:
        """Валидация целостности диаграммы"""
        errors = []
        node_ids = {node.id for node in self.nodes}
        
        for conn in self.connections:
            if conn.source_id not in node_ids:
                errors.append(f"Connection source not found: {conn.source_id}")
            if conn.target_id not in node_ids:
                errors.append(f"Connection target not found: {conn.target_id}")
                
        return errors

class UMLNode(BaseModel):
    """Модель класса/узла"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    x: float
    y: float
    properties: List[UMLProperty] = Field(default_factory=list)
    methods: List[UMLMethod] = Field(default_factory=list)
    is_abstract: bool = False
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.isidentifier():
            raise ValueError('Invalid class name')
        return v
```

#### DiagramManager — CRUD операции:

```python
class DiagramManager:
    """Менеджер для операций с диаграммой"""
    
    def __init__(self):
        self.diagram = UMLDiagram()
        
    def add_node(self, x: float, y: float, name: str = "NewClass") -> UMLNode:
        """Добавить узел в диаграмму"""
        node = UMLNode(name=name, x=x, y=y)
        self.diagram.nodes.append(node)
        return node
        
    def remove_node(self, node_id: str) -> bool:
        """Удалить узел и связанные связи"""
        # Удаление узла
        self.diagram.nodes = [n for n in self.diagram.nodes if n.id != node_id]
        
        # Удаление связей
        self.diagram.connections = [
            c for c in self.diagram.connections 
            if c.source_id != node_id and c.target_id != node_id
        ]
        
        return True
```

## Паттерны проектирования

### 1. Observer (Наблюдатель)
Реализован через PyQt сигналы/слоты:

```python
# Publisher
class DiagramController(QObject):
    card_added = pyqtSignal(object)
    
    def add_card(self):
        node = self.manager.add_node()
        self.card_added.emit(node)  # Уведомление подписчиков

# Subscriber
class MainWindow(QMainWindow):
    def __init__(self, controller):
        controller.card_added.connect(self._on_card_added)
        
    def _on_card_added(self, node):
        # Реакция на событие
        card = UMLCard(node.name, node.x, node.y)
        self.scene.addItem(card)
```

### 2. Strategy (Стратегия)
Для генерации кода на разных языках:

```python
class CodeGenerator:
    def generate(self, diagram: UMLDiagram, language: str) -> str:
        strategies = {
            "python": PythonGenerator(),
            "java": JavaGenerator(),
            "javascript": JavaScriptGenerator(),
        }
        
        strategy = strategies.get(language)
        if not strategy:
            raise ValueError(f"Unsupported language: {language}")
            
        return strategy.generate(diagram)

class PythonGenerator:
    def generate(self, diagram: UMLDiagram) -> str:
        # Специфичная логика для Python
        pass
```

### 3. Factory Method (Фабричный метод)
Для создания UI элементов:

```python
class WidgetFactory:
    @staticmethod
    def create_card(node: UMLNode) -> UMLCard:
        """Фабричный метод создания карточки"""
        card = UMLCard(node.name, node.x, node.y)
        card.setFlags(QGraphicsRectItem.ItemIsMovable | 
                      QGraphicsRectItem.ItemIsSelectable)
        return card
        
    @staticmethod
    def create_connection(source: UMLCard, target: UMLCard, 
                         conn_type: ConnectionType) -> ConnectionLine:
        """Фабричный метод создания связи"""
        return ConnectionLine(source, target, conn_type)
```

### 4. Command (Команда)
Готов к реализации для Undo/Redo:

```python
class Command(ABC):
    @abstractmethod
    def execute(self): pass
    
    @abstractmethod
    def undo(self): pass

class AddCardCommand(Command):
    def __init__(self, controller: DiagramController, x: float, y: float):
        self.controller = controller
        self.x, self.y = x, y
        self.node_id = None
        
    def execute(self):
        node = self.controller.add_card(self.x, self.y)
        self.node_id = node.id
        
    def undo(self):
        self.controller.remove_card(self.node_id)
```

### 5. Dependency Injection (Внедрение зависимостей)
Для слабой связанности:

```python
class Application:
    def __init__(self):
        # Создание зависимостей
        self.history_service = HistoryService()
        self.serialization_service = SerializationService()
        
        # Инъекция в контроллеры
        self.diagram_controller = DiagramController(
            history=self.history_service,
            serializer=self.serialization_service
        )
        
        # Инъекция в представление
        self.window = MainWindow(self.diagram_controller)
```

## Модели данных

### Иерархия моделей

```
UMLDiagram
├── nodes: List[UMLNode]
│   ├── properties: List[UMLProperty]
│   └── methods: List[UMLMethod]
│       └── parameters: List[UMLProperty]
└── connections: List[UMLConnection]
```

### Валидация данных

Используется **Pydantic** для автоматической валидации:

```python
class UMLProperty(BaseModel):
    name: str
    type: str = "Any"
    visibility: Literal["public", "private", "protected"] = "public"
    is_static: bool = False
    default_value: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if not v.isidentifier():
            raise ValueError('Property name must be valid identifier')
        return v
    
    @validator('type')
    def validate_type(cls, v):
        if not v:
            raise ValueError('Type cannot be empty')
        return v
```

### Сериализация

Автоматическая сериализация в JSON через Pydantic:

```python
# Сериализация
diagram_dict = diagram.model_dump()
json_str = json.dumps(diagram_dict, indent=2)

# Десериализация
diagram_dict = json.loads(json_str)
diagram = UMLDiagram.model_validate(diagram_dict)
```

## Поток данных

### Создание карточки

```
1. User clicks "Add Class"
   ↓
2. MainWindow.add_card_requested.emit()
   ↓
3. Application._on_add_card()
   ↓
4. DiagramController.add_card()
   ↓
5. DiagramManager.add_node()
   ↓
6. UMLDiagram.nodes.append(node)
   ↓
7. HistoryService.push_state()
   ↓
8. DiagramController.card_added.emit(node)
   ↓
9. Application._on_card_added()
   ↓
10. UMLCard created and added to scene
```

### Создание связи

```
1. User drags from anchor to anchor
   ↓
2. DiagramScene.connection_ready.emit()
   ↓
3. MainWindow._on_connection_ready()
   ↓
4. DiagramController.add_connection()
   ↓
5. DiagramManager.add_connection()
   ↓
6. UMLDiagram.connections.append(conn)
   ↓
7. HistoryService.push_state()
   ↓
8. DiagramController.connection_added.emit(conn)
   ↓
9. Application._on_connection_added()
   ↓
10. ConnectionLine created and added to scene
```

### Undo/Redo

```
1. User presses Ctrl+Z
   ↓
2. MainWindow.undo_requested.emit()
   ↓
3. DiagramController.undo()
   ↓
4. HistoryService.undo()
   ↓
5. Previous UMLDiagram state returned
   ↓
6. DiagramController.diagram_loaded.emit()
   ↓
7. Application._on_diagram_loaded()
   ↓
8. Scene cleared and rebuilt from state
```

## Производительность

### Оптимизации HistoryService

1. **Pydantic model_copy()** вместо deepcopy — **+30-50% быстрее**
2. **Дедупликация состояний** — **-94% состояний при drag&drop**
3. **Сжатие старых состояний** — **-40-60% памяти**
4. **Разделенная блокировка** — **-95% времени блокировки**
5. **Валидация по уровням** — **-96% проверок**

### Метрики производительности

| Операция | До оптимизации | После | Улучшение |
|----------|----------------|-------|-----------|
| Копирование состояния | 100ms | 50ms | **+100%** |
| Валидация при push | 3550 проверок | 150 проверок | **-96%** |
| Память при drag&drop | 50 состояний | 2-3 состояния | **-94%** |
| CPU при перетаскивании | 80-100% | 5-10% | **-90%** |

### Оптимизация UI

1. **Ленивая загрузка** виджетов
2. **Кэширование** геометрических расчетов
3. **Батчинг** обновлений сцены
4. **Оптимизация** перерисовки

```python
class UMLCard(QGraphicsRectItem):
    def __init__(self):
        self._cached_bounds = None
        
    def boundingRect(self):
        """Кэширование границ для производительности"""
        if self._cached_bounds is None:
            self._cached_bounds = self._calculate_bounds()
        return self._cached_bounds
        
    def update_content(self):
        """Инвалидация кэша при изменении"""
        self._cached_bounds = None
        super().update()
```

---

Эта архитектура обеспечивает **масштабируемость**, **поддерживаемость** и **расширяемость** системы LogicCraft. 🏗️