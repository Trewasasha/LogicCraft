# LogicCraft — Документация View-слоя

View-слой отвечает за визуальное представление UML-диаграммы и взаимодействие с пользователем. Построен на PyQt6 с использованием Graphics View Framework.

---

## Архитектура

```
view/
├── main_window.py          # Главное окно приложения
├── theme.py                # Централизованные стили
├── scenes/
│   └── diagram_scene.py    # Холст для диаграммы
├── widgets/
│   ├── uml_card.py         # Карточка UML-класса
│   ├── connection_line.py  # Линия связи между карточками
│   ├── anchor_point.py     # Точка привязки для создания связей
│   └── arrow_head.py       # Наконечник стрелки
└── dialogs/
    ├── edit_class_dialog.py         # Диалог редактирования класса
    └── connection_properties.py     # Диалог свойств связи
```

### Принципы

- **Разделение ответственности** — каждый компонент отвечает за свою часть UI
- **Сигналы/слоты** — взаимодействие через PyQt signals, минимум прямых вызовов
- **Централизованные стили** — все цвета и размеры в `theme.py`, не в коде компонентов
- **Иммутабельность ID** — каждый элемент (карточка, связь) имеет UUID, который не меняется

---

## Компоненты

### MainWindow

**Файл:** `main_window.py`

**Назначение:** Главное окно приложения — контейнер для всех UI-элементов.

**Состав:**
- `DiagramView` — viewport для отображения сцены с поддержкой зума (Ctrl+колесо)
- `DiagramScene` — холст с карточками и связями
- Меню (File, Edit)
- Тулбар (Add Class, Save, Load, Edit, Delete)
- Статусбар

**Ключевые методы:**

| Метод | Описание |
|---|---|
| `add_card_to_scene(card)` | Добавить карточку на сцену и в `card_map` |
| `remove_card_from_scene(card_id)` | Удалить карточку со сцены |
| `add_connection_to_scene(conn)` | Добавить связь на сцену и в `connection_map` |
| `remove_connection_from_scene(conn_id)` | Удалить связь со сцены (включая `arrow_head`) |
| `clear_scene()` | Очистить всю сцену |

**Сигналы (эмитит MainWindow):**

| Сигнал | Параметры | Когда эмитится |
|---|---|---|
| `add_card_requested` | `(x: float, y: float)` | Клик на "Add Class" |
| `save_requested` | `(filepath: str)` | Выбран файл для сохранения |
| `load_requested` | `(filepath: str)` | Выбран файл для загрузки |
| `clear_requested` | `()` | Подтверждена очистка диаграммы |
| `edit_card_requested` | `(card_id, name, attrs, methods)` | Сохранены изменения в `EditClassDialog` |
| `edit_connection_requested` | `(conn_id, new_type)` | Изменён тип связи в `ConnectionPropertiesDialog` |

**Горячие клавиши:**

| Комбинация | Действие |
|---|---|
| `Ctrl+S` | Сохранить |
| `Ctrl+Z` | Отменить (Undo) |
| `Ctrl+Shift+Z` / `Ctrl+Y` | Повторить (Redo) |
| `Delete` / `Backspace` | Удалить выделенное |
| `Ctrl+колесо мыши` | Зум |

---

### DiagramScene

**Файл:** `scenes/diagram_scene.py`

**Назначение:** Холст для размещения карточек и связей. Управляет процессом создания связей через drag-and-drop.

**Особенности:**
- Рисует фон с сеткой (шаг 50px)
- Отображает временную пунктирную линию при создании связи
- Эмитит сигналы при завершении создания связи и перемещении карточки

**Ключевые методы:**

| Метод | Описание |
|---|---|
| `drawBackground(painter, rect)` | Рисует фон и сетку |
| `start_connection(source_card, anchor)` | Начало создания связи — появляется пунктир |
| `finish_connection(target_card, anchor)` | Завершение создания связи — эмитит `connection_ready` |
| `cancel_connection()` | Отмена создания связи (отпустили мышь не на точке привязки) |

**Сигналы:**

| Сигнал | Параметры | Когда эмитится |
|---|---|---|
| `connection_ready` | `(source_id, target_id, source_anchor, target_anchor)` | Пользователь соединил две карточки |
| `card_moved` | `(card_id, x, y)` | Карточка перемещена (для сохранения позиции в модели) |

**Состояние при создании связи:**

```python
self.connection_active = True       # Идёт процесс создания связи
self.connection_source = card       # Исходная карточка
self.source_anchor = "right"        # Исходная точка привязки
self.temp_line = QGraphicsLineItem  # Временная пунктирная линия
```

---

### UMLCard

**Файл:** `widgets/uml_card.py`

**Назначение:** Карточка UML-класса с заголовком, атрибутами, методами и точками привязки.

**Структура:**

```
┌─────────────────────┐
│   ClassName         │ ← header_bg (синий фон)
├─────────────────────┤ ← divider1
│ +attr1: str         │ ← attrs_text (зелёный)
│ -attr2: int         │
├─────────────────────┤ ← divider2
│ +method1()          │ ← methods_text (голубой)
│ +method2(): str     │
└─────────────────────┘
  ●   ●   ●   ●        ← anchor points (top, bottom, left, right)
```

**Ключевые методы:**

| Метод | Описание |
|---|---|
| `update_content()` | Пересчитывает высоту карточки и обновляет текст |
| `get_anchor_point(name)` | Возвращает позицию точки привязки в координатах сцены |
| `setSelected(selected)` | Меняет цвет рамки и показывает/скрывает точки привязки |
| `to_dict()` | Сериализация в словарь для сохранения |

**Сигналы:**

| Сигнал | Параметры | Когда эмитится |
|---|---|---|
| `position_changed` | `()` | Карточка перемещена (для обновления связей) |
| `about_to_delete` | `(card)` | Карточка удаляется (для очистки связей) |

**Точки привязки:**

| Константа | Позиция |
|---|---|
| `ANCHOR_TOP` | Верх карточки (центр) |
| `ANCHOR_BOTTOM` | Низ карточки (центр) |
| `ANCHOR_LEFT` | Левая сторона (центр) |
| `ANCHOR_RIGHT` | Правая сторона (центр) |

**Флаги:**
- `ItemIsMovable` — можно перетаскивать
- `ItemIsSelectable` — можно выделить кликом
- `ItemSendsGeometryChanges` — эмитит `itemChange` при перемещении

---

### ConnectionLine

**Файл:** `widgets/connection_line.py`

**Назначение:** Линия связи между двумя карточками с наконечником стрелки.

**Особенности:**
- Автоматически обновляет позицию при перемещении карточек (подписка на `position_changed`)
- Наконечник (`ArrowHead`) создаётся один раз и переиспользуется
- Линия укорачивается на 12px чтобы не заходить внутрь наконечника

**Ключевые методы:**

| Метод | Описание |
|---|---|
| `update_position()` | Пересчитывает координаты линии и наконечника |
| `set_selected(selected)` | Меняет цвет линии и наконечника |
| `set_connection_type(type)` | Меняет тип связи (форму наконечника) |

**Сигналы:**

| Сигнал | Параметры | Когда эмитится |
|---|---|---|
| `selected_changed` | `(connection, selected)` | Изменилось состояние выделения |
| `about_to_delete` | `(connection)` | Связь удаляется |

**Типы связей:**

| Тип | Enum | Форма наконечника |
|---|---|---|
| Ассоциация | `ConnectionType.ASSOCIATION` | Закрашенный треугольник |
| Наследование | `ConnectionType.INHERITANCE` | Полый треугольник |
| Композиция | `ConnectionType.COMPOSITION` | Закрашенный ромб |
| Агрегация | `ConnectionType.AGGREGATION` | Полый ромб |

---

### AnchorPoint

**Файл:** `widgets/anchor_point.py`

**Назначение:** Красный кружок на карточке, за который тянут для создания связи.

**Поведение:**
1. **Hover** — кружок увеличивается и меняет цвет
2. **MousePress** — начинается создание связи (`scene.start_connection`)
3. **MouseMove** — пунктирная линия тянется за курсором
4. **MouseRelease** — если отпустили на другой `AnchorPoint` → `scene.finish_connection`, иначе → `scene.cancel_connection`

**Ключевые методы:**

| Метод | Описание |
|---|---|
| `hoverEnterEvent()` | Меняет цвет на `HOVER_COLOR` и масштаб на `HOVER_SCALE` |
| `hoverLeaveEvent()` | Возвращает цвет на `NORMAL_COLOR` и масштаб на 1.0 |
| `_create_search_rect(center)` | Создаёт прямоугольник 10×10px для поиска целевой точки |

**Видимость:**
- Точки привязки видны только когда карточка выделена (`card.setSelected(True)`)
- `zValue = 1000` — всегда поверх других элементов

---

### ArrowHead

**Файл:** `widgets/arrow_head.py`

**Назначение:** Наконечник стрелки на конце `ConnectionLine`.

**Формы:**

| Тип связи | Форма | Код |
|---|---|---|
| `association` | Закрашенный треугольник | `setBrush(COLOR)` |
| `inheritance` | Полый треугольник | `setBrush(NoBrush)` |
| `composition` | Закрашенный ромб | `setBrush(COLOR)` |
| `aggregation` | Полый ромб | `setBrush(NoBrush)` |

**Ключевые методы:**

| Метод | Описание |
|---|---|
| `_update_shape()` | Пересоздаёт полигон в зависимости от типа связи |
| `_update_rotation()` | Поворачивает наконечник по направлению линии |
| `set_direction(direction)` | Устанавливает направление (вектор от source к target) |
| `set_connection_type(type)` | Меняет тип связи и форму наконечника |

**Размер:**
- Базовый размер задаётся через `ArrowStyle.SIZE` (по умолчанию 12px)
- Высота треугольника/ромба = `SIZE * 0.6`

---

### EditClassDialog

**Файл:** `dialogs/edit_class_dialog.py`

**Назначение:** Диалог редактирования имени класса, атрибутов и методов.

**UI:**
- Поле ввода имени класса
- Список атрибутов с кнопками Add/Remove
- Список методов с кнопками Add/Remove
- Кнопки OK/Cancel

**Ключевые методы:**

| Метод | Описание |
|---|---|
| `get_data()` | Возвращает `(name, attributes, methods)` |
| `_add_attribute()` | Показывает `QInputDialog` для ввода атрибута |
| `_add_method()` | Показывает `QInputDialog` для ввода метода |

**Формат атрибутов/методов:**
- Атрибут: `+name: str`, `-age: int`, `#id: UUID`
- Метод: `+getName(): str`, `-calculate(): void`

---

### ConnectionPropertiesDialog

**Файл:** `dialogs/connection_properties.py`

**Назначение:** Диалог выбора типа связи (ассоциация, наследование, композиция, агрегация).

**UI:**
- Выпадающий список с типами связей
- Кнопки OK/Cancel

**Ключевые методы:**

| Метод | Описание |
|---|---|
| `get_connection_type()` | Возвращает выбранный `ConnectionType` |

---

## Поток данных

### Создание карточки

```
User: клик "Add Class"
  ↓
MainWindow._on_add_clicked()
  ↓ emit add_card_requested(x, y)
Application._on_add_card()
  ↓ controller.add_card(x, y)
Controller: создаёт UMLNode в модели
  ↓ emit card_added(node)
Application._on_card_added()
  ↓ создаёт UMLCard
  ↓ window.add_card_to_scene(card)
MainWindow: добавляет card на scene
```

### Создание связи

```
User: тянет от anchor_point к anchor_point
  ↓
AnchorPoint.mousePressEvent()
  ↓ scene.start_connection(card, anchor)
DiagramScene: создаёт temp_line (пунктир)
  ↓
User: отпускает мышь на другой anchor_point
  ↓
AnchorPoint.mouseReleaseEvent()
  ↓ scene.finish_connection(target_card, target_anchor)
DiagramScene: удаляет temp_line
  ↓ emit connection_ready(source_id, target_id, ...)
MainWindow._on_connection_ready()
  ↓ controller.add_connection(...)
Controller: создаёт UMLConnection в модели
  ↓ emit connection_added(conn)
Application._on_connection_added()
  ↓ создаёт ConnectionLine
  ↓ window.add_connection_to_scene(conn_line)
MainWindow: добавляет conn_line на scene
```

### Перемещение карточки

```
User: перетаскивает карточку
  ↓
UMLCard.itemChange(ItemPositionHasChanged)
  ↓ emit signals.position_changed()
ConnectionLine.update_position() (подписан на сигнал)
  ↓ пересчитывает координаты линии и наконечника
  ↓
UMLCard.itemChange()
  ↓ scene.on_card_moved(card)
DiagramScene
  ↓ emit card_moved(card_id, x, y)
MainWindow._on_card_moved()
  ↓ controller.update_card(card_id, x=x, y=y)
Controller: обновляет позицию в модели
```

---

## Стилизация

Все стили сосредоточены в двух файлах:

### theme.py — графические элементы

Токены для `QGraphicsItem` (карточки, линии, стрелки, точки привязки, сцена):

```python
CardStyle.BACKGROUND = "#f5f5dc"
CardStyle.BORDER = "#4169E1"
ConnectionStyle.LINE_COLOR = "#666666"
SceneStyle.BACKGROUND = "#fafafa"
AnchorStyle.NORMAL_COLOR = "#FF6B6B"
ArrowStyle.COLOR = "#666666"
```

### style.qss — Qt-виджеты

QSS для стандартных виджетов (тулбар, диалоги, статусбар):

```css
QToolBar { background-color: #f0f0f0; }
QDialog QPushButton { background-color: #4169E1; }
```

Подробнее см. `STYLING.md`.

---

## Частые задачи

### Добавить новый тип связи

1. Добавь значение в `ConnectionType` enum (`arrow_head.py`)
2. Добавь обработку в `ArrowHead._update_shape()`
3. Добавь пункт в `ConnectionPropertiesDialog._setup_ui()`

### Изменить цвет карточки

Отредактируй `theme.py`:

```python
@dataclass(frozen=True)
class _CardStyle:
    BACKGROUND: str = "#ffffff"  # было #f5f5dc
```

### Добавить новую точку привязки

1. Добавь константу в `UMLCard`: `ANCHOR_CENTER = "center"`
2. Создай `AnchorPoint` в `_create_anchors()`
3. Обнови позицию в `_update_anchor_positions()`

### Добавить контекстное меню на карточку

Переопредели `contextMenuEvent` в `UMLCard`:

```python
def contextMenuEvent(self, event):
    menu = QMenu()
    edit_action = menu.addAction("Edit")
    delete_action = menu.addAction("Delete")
    action = menu.exec(event.screenPos())
    if action == edit_action:
        # эмитить сигнал или вызвать диалог
    event.accept()
```

---

## Отладка

### Включить отладочные print'ы

Раскомментируй строки с `print(f"DEBUG: ...")` в:
- `anchor_point.py` — процесс создания связи
- `diagram_scene.py` — сигналы сцены
- `main_window.py` — обработка событий

### Визуализировать bounding boxes

Добавь в `DiagramView.__init__`:

```python
self.setRenderHint(QPainter.RenderHint.Antialiasing)
self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
```

### Проверить z-order элементов

```python
for item in scene.items():
    print(f"{item.__class__.__name__}: zValue={item.zValue()}")
```

Ожидаемый порядок:
- `AnchorPoint`: 1000 (поверх всего)
- `ArrowHead`: 100
- `ConnectionLine`: 0 (по умолчанию)
- `UMLCard`: 0

---

## Ограничения Qt Graphics View

- **Нет CSS** — `QGraphicsItem` не поддерживают QSS, только `QPen`/`QBrush`
- **Координаты** — сцена использует float-координаты, но рендеринг округляет до пикселей
- **Производительность** — при >1000 элементов на сцене нужна оптимизация (BSP-индекс, LOD)
- **Шрифты** — `QFont` не поддерживает web-шрифты, только системные

---

## Дальнейшее развитие

- [ ] Поддержка нескольких тем (светлая/тёмная)
- [ ] Контекстное меню на карточках и связях
- [ ] Snap-to-grid при перемещении карточек
- [ ] Экспорт диаграммы в PNG/SVG
- [ ] Миниатюра диаграммы (overview)
- [ ] Группировка карточек (packages)
