# 🏗️ Архитектура LogicCraft

## Обзор

LogicCraft построен на паттерне **MVC** с сервисным слоем. Компоненты взаимодействуют через PyQt6 сигналы/слоты.

```
┌─────────────────────────────────────────────────────┐
│                  View Layer                         │
│  MainWindow · DiagramView · DiagramScene            │
│  UMLCard · ConnectionLine · ArrowHead               │
│  ToolboxPanel · PropertiesPanel                     │
│  Dialogs: EditClass · ConnectionProperties · ...    │
├─────────────────────────────────────────────────────┤
│                Controller Layer                     │
│  DiagramController                                  │
├─────────────────────────────────────────────────────┤
│                 Service Layer                       │
│  HistoryService · CodeGenerator · ProjectExporter   │
│  SerializationService · GeometryService             │
├─────────────────────────────────────────────────────┤
│                  Model Layer                        │
│  UMLDiagram · UMLNode · UMLConnection               │
│  UMLProperty · UMLMethod · UMLEnumLiteral           │
│  DiagramManager · DiagramEngine                     │
└─────────────────────────────────────────────────────┘
```

---

## Структура проекта

```
src/logiccraft/
├── main.py                    # Точка входа, класс Application
├── __main__.py                # Запуск через python -m logiccraft
├── style.qss                  # Централизованные QSS стили
├── models/
│   ├── diagram.py             # UMLDiagram, UMLNode, UMLConnection, NodeType
│   ├── diagram_manager.py     # CRUD операции с диаграммой
│   ├── engine.py              # Валидация, статистика, анализ
│   ├── project_settings.py    # Настройки экспорта проекта
│   └── structure_template.py  # Шаблоны архитектур
├── controllers/
│   └── diagram_controller.py  # Главный контроллер (MVC)
├── services/
│   ├── history_service.py     # Undo/Redo с оптимизацией
│   ├── code_generator.py      # Генерация кода через Jinja2
│   ├── project_exporter.py    # Экспорт структуры проекта
│   └── serialization_service.py
├── view/
│   ├── theme.py               # Style tokens (CardStyle, SceneStyle, ...)
│   ├── main_window.py         # MainWindow + DiagramView
│   ├── scenes/
│   │   └── diagram_scene.py   # QGraphicsScene + snap to grid
│   ├── widgets/
│   │   ├── uml_card.py        # QGraphicsRectItem с кастомной отрисовкой
│   │   ├── connection_line.py # QGraphicsLineItem + метки множественности
│   │   ├── arrow_head.py      # QGraphicsPolygonItem для наконечников
│   │   └── anchor_point.py    # Точки привязки для создания связей
│   ├── panels/
│   │   ├── toolbox_panel.py   # Левая панель инструментов
│   │   └── properties_panel.py # Правая панель свойств
│   └── dialogs/
│       ├── welcome_dialog.py
│       ├── edit_class_dialog.py
│       ├── connection_properties.py
│       ├── code_generation_dialog.py
│       └── project_export_dialog.py
└── templates/
    ├── python_class.j2
    ├── java_class.j2
    ├── javascript_class.j2
    ├── typescript_class.j2
    └── csharp_class.j2
```

---

## Ключевые модели данных

```python
class NodeType(str, Enum):
    CLASS = "class"
    INTERFACE = "interface"
    ENUM = "enum"
    ABSTRACT_CLASS = "abstract_class"

class UMLNode(BaseModel):
    id: str
    name: str
    x: float
    y: float
    node_type: NodeType = NodeType.CLASS
    properties: List[UMLProperty]
    methods: List[UMLMethod]
    enum_literals: List[UMLEnumLiteral]
    is_abstract: bool = False

class UMLConnection(BaseModel):
    id: str
    source_id: str
    target_id: str
    type: ConnectionType = ConnectionType.association
    source_anchor: str
    target_anchor: str
    multiplicity: Optional[str] = None  # "1:0..*"
    name: Optional[str] = None

class ConnectionType(str, Enum):
    association = "association"
    inheritance = "inheritance"
    composition = "composition"
    aggregation = "aggregation"
    dependency = "dependency"
    realization = "realization"
    interaction = "interaction"
```

---

## Поток данных: создание элемента

```
Toolbox кнопка clicked
    → MainWindow.add_card_requested.emit(x, y, node_type)
    → Application._on_add_card(x, y, node_type)
    → DiagramController.add_card(x, y, NodeType(node_type))
    → DiagramManager.add_node(x, y, node_type=nt)
    → HistoryService.push_state(diagram)
    → DiagramController.card_added.emit(node)
    → Application._on_card_added(node)
    → UMLCard(node.name, node.x, node.y, node_type=node.node_type)
    → MainWindow.add_card_to_scene(card)
```

## Поток данных: Undo/Redo

```
Ctrl+Z
    → DiagramController.undo()
    → HistoryService.undo() → возвращает предыдущий UMLDiagram
    → DiagramController._on_state_restored(diagram)
    → manager.diagram = diagram.model_copy(deep=True)
    → DiagramController.diagram_loaded.emit()
    → Application._on_diagram_loaded()
    → Сцена очищается и перестраивается из состояния
```

---

## Система стилей

Все стили централизованы в двух местах:

**`theme.py`** — Python константы для QGraphicsItem (не поддерживают QSS):
```python
CardStyle.HEADER_BG = "#7C3AED"
SceneStyle.BACKGROUND = "#F0EFFE"
AnchorStyle.NORMAL_COLOR = "#9B72F5"
```

**`style.qss`** — Qt Style Sheets для виджетов:
```css
#WelcomeCardPrimary { background: ...; border-radius: 16px; }
#ToolboxButton { background: transparent; border-radius: 8px; }
#PropertiesInput { border: 1px solid #D4C9F8; }
```

Применяется через `apply_stylesheet(app)` при запуске.

---

## HistoryService — оптимизации

| Оптимизация | Результат |
|-------------|-----------|
| `model_copy()` вместо `deepcopy()` | +30-50% скорость |
| Дедупликация состояний | -94% состояний при drag |
| Сжатие старых состояний | -40-60% памяти |
| Разделённая блокировка | -95% времени блокировки |

---

## Генерация кода

Использует **Jinja2** шаблоны. Каждый язык — отдельный `.j2` файл.

```python
# CodeGenerator.generate(diagram, language)
template = env.get_template("python_class.j2")
return template.render(
    nodes=diagram.nodes,
    inheritance_map=inheritance_map,
    has_abstract_classes=...,
    has_interfaces=...,
    has_enums=...
)
```

Шаблоны используют `node.node_type.value` для различения типов:
- `'interface'` → `class Foo(ABC):`
- `'enum'` → `class Foo(Enum):`
- `'abstract_class'` → `class Foo(ABC):`
- `'class'` → `class Foo:`
