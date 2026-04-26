# Requirements Document

## Introduction

Рефакторинг слоя view приложения LogicCraft: вынос всех захардкоженных стилей (цвета, шрифты, размеры, толщины линий) из Python-кода в отдельные файлы стилей. Цель — централизовать управление внешним видом, упростить смену тем и устранить дублирование визуальных констант по всему view-слою.

Текущее состояние: стили разбросаны по 6 файлам view-слоя в виде строк-цветов, объектов `QColor`, `QFont`, `QPen`, `QBrush` прямо в коде. Файлы `theme.py` и `style.qss` существуют, но пусты.

## Glossary

- **Style_Manager** — модуль `theme.py`, отвечающий за загрузку и предоставление стилей всем компонентам view-слоя
- **Style_Token** — именованная константа стиля (цвет, шрифт, размер), определённая в одном месте и используемая по имени
- **QSS_File** — файл в формате Qt Style Sheets (`.qss`), применяемый к виджетам через `setStyleSheet()`
- **Graphics_Style** — набор параметров для `QPen`, `QBrush`, `QFont`, применяемых к `QGraphicsItem` (не поддерживают QSS напрямую)
- **Theme** — полный набор Style_Token, определяющий визуальный облик приложения
- **UML_Card** — виджет карточки UML-класса (`uml_card.py`)
- **Anchor_Point** — виджет точки привязки для создания связей (`anchor_point.py`)
- **Arrow_Head** — виджет наконечника стрелки (`arrow_head.py`)
- **Connection_Line** — виджет линии связи (`connection_line.py`)
- **Diagram_Scene** — сцена диаграммы (`diagram_scene.py`)
- **View_Layer** — совокупность всех файлов в `src/logiccraft/view/`

---

## Requirements

### Requirement 1: Централизованное хранилище Style_Token

**User Story:** Как разработчик, я хочу иметь единое место для всех визуальных констант, чтобы изменение цвета или шрифта требовало правки в одном файле, а не поиска по всему проекту.

#### Acceptance Criteria

1. THE Style_Manager SHALL определять все Style_Token в файле `src/logiccraft/view/theme.py`
2. THE Style_Manager SHALL группировать Style_Token по компонентам: карточки, связи, сцена, точки привязки, наконечники
3. THE Style_Manager SHALL предоставлять Style_Token как именованные атрибуты или константы, доступные через импорт
4. WHEN Style_Manager импортируется в любой файл View_Layer, THE Style_Manager SHALL предоставлять все Style_Token без дополнительной инициализации
5. THE Style_Manager SHALL содержать Style_Token для всех цветов, найденных в View_Layer: `#f5f5dc`, `#4169E1`, `#2c3e50`, `#27ae60`, `#DC143C`, `#666666`, `#FF6B6B`, `#FF4444`, `#FFFFFF`, `#fafafa`, `#e0e0e0`

---

### Requirement 2: Вынос Graphics_Style из UML_Card

**User Story:** Как разработчик, я хочу, чтобы UML_Card не содержал захардкоженных цветов и шрифтов, чтобы внешний вид карточки управлялся через Style_Manager.

#### Acceptance Criteria

1. WHEN UML_Card инициализируется, THE UML_Card SHALL получать цвета фона, рамки, заголовка и текста из Style_Manager, а не из строковых литералов
2. WHEN UML_Card переходит в состояние выделения, THE UML_Card SHALL получать цвет выделения из Style_Manager
3. THE UML_Card SHALL получать параметры шрифтов заголовка, атрибутов и методов из Style_Manager
4. IF Style_Manager не содержит запрошенного Style_Token, THEN THE UML_Card SHALL использовать значение по умолчанию, определённое в Style_Manager
5. THE UML_Card SHALL содержать ноль строковых литералов цветов (формата `"#RRGGBB"`) в своём исходном коде после рефакторинга

---

### Requirement 3: Вынос Graphics_Style из Anchor_Point

**User Story:** Как разработчик, я хочу, чтобы Anchor_Point не содержал захардкоженных цветов, чтобы стиль точек привязки управлялся централизованно.

#### Acceptance Criteria

1. WHEN Anchor_Point инициализируется, THE Anchor_Point SHALL получать цвет нормального состояния из Style_Manager
2. WHEN Anchor_Point получает событие hoverEnter, THE Anchor_Point SHALL получать цвет hover-состояния из Style_Manager
3. WHEN Anchor_Point получает событие hoverLeave, THE Anchor_Point SHALL восстанавливать цвет нормального состояния из Style_Manager
4. THE Anchor_Point SHALL содержать ноль строковых литералов цветов в своём исходном коде после рефакторинга

---

### Requirement 4: Вынос Graphics_Style из Arrow_Head

**User Story:** Как разработчик, я хочу, чтобы Arrow_Head не содержал захардкоженных цветов для каждого типа связи, чтобы стиль наконечников управлялся через Style_Manager.

#### Acceptance Criteria

1. WHEN Arrow_Head обновляет форму для типа `inheritance`, THE Arrow_Head SHALL получать цвет пера из Style_Manager
2. WHEN Arrow_Head обновляет форму для типа `composition`, THE Arrow_Head SHALL получать цвет заливки и пера из Style_Manager
3. WHEN Arrow_Head обновляет форму для типа `aggregation`, THE Arrow_Head SHALL получать цвет пера из Style_Manager
4. WHEN Arrow_Head обновляет форму для типа `association`, THE Arrow_Head SHALL получать цвет заливки и пера из Style_Manager
5. THE Arrow_Head SHALL содержать ноль строковых литералов цветов в своём исходном коде после рефакторинга

---

### Requirement 5: Вынос Graphics_Style из Connection_Line

**User Story:** Как разработчик, я хочу, чтобы Connection_Line не содержал захардкоженных цветов и толщин линий, чтобы стиль связей управлялся через Style_Manager.

#### Acceptance Criteria

1. WHEN Connection_Line инициализируется, THE Connection_Line SHALL получать цвет и толщину пера нормального состояния из Style_Manager
2. WHEN Connection_Line переходит в состояние выделения, THE Connection_Line SHALL получать цвет и толщину пера выделенного состояния из Style_Manager
3. THE Connection_Line SHALL содержать ноль строковых литералов цветов в своём исходном коде после рефакторинга

---

### Requirement 6: Вынос Graphics_Style из Diagram_Scene

**User Story:** Как разработчик, я хочу, чтобы Diagram_Scene не содержал захардкоженных цветов фона и сетки, чтобы стиль сцены управлялся через Style_Manager.

#### Acceptance Criteria

1. WHEN Diagram_Scene инициализируется, THE Diagram_Scene SHALL получать цвет фона из Style_Manager
2. WHEN Diagram_Scene отрисовывает сетку, THE Diagram_Scene SHALL получать цвет и толщину линий сетки из Style_Manager
3. WHEN Diagram_Scene создаёт временную линию связи, THE Diagram_Scene SHALL получать цвет временной линии из Style_Manager
4. THE Diagram_Scene SHALL содержать ноль строковых литералов цветов в своём исходном коде после рефакторинга

---

### Requirement 7: QSS-стили для Qt-виджетов

**User Story:** Как разработчик, я хочу, чтобы стили Qt-виджетов (диалоги, тулбар, статусбар) были вынесены в QSS-файл, а не задавались через `setStyleSheet()` в Python-коде.

#### Acceptance Criteria

1. THE Style_Manager SHALL загружать содержимое файла `src/logiccraft/style.qss` при инициализации приложения
2. WHEN приложение запускается, THE Style_Manager SHALL применять загруженный QSS к объекту `QApplication`
3. THE Style_Manager SHALL предоставлять метод `apply_stylesheet(app)` для применения QSS к `QApplication`
4. IF файл `style.qss` не найден, THEN THE Style_Manager SHALL логировать предупреждение и продолжать работу без применения QSS
5. WHERE диалоги (`EditClassDialog`, `ConnectionPropertiesDialog`) используют `setStyleSheet()`, THE Style_Manager SHALL предоставлять соответствующие QSS-строки через именованные константы

---

### Requirement 8: Структура файлов стилей

**User Story:** Как разработчик, я хочу понятную структуру файлов стилей, чтобы легко находить и изменять нужные стили.

#### Acceptance Criteria

1. THE Style_Manager SHALL организовывать Style_Token в `theme.py` по следующим секциям: `CardStyle`, `ConnectionStyle`, `SceneStyle`, `AnchorStyle`, `ArrowStyle`
2. THE Style_Manager SHALL хранить QSS для виджетов в файле `src/logiccraft/style.qss`
3. THE Style_Manager SHALL хранить QSS для диалогов в файле `src/logiccraft/style.qss` в отдельной секции с комментарием
4. WHEN разработчик добавляет новый Style_Token в `theme.py`, THE Style_Manager SHALL не требовать изменений в других файлах для применения токена

---

### Requirement 9: Обратная совместимость и отсутствие регрессий

**User Story:** Как разработчик, я хочу, чтобы рефакторинг не изменил визуальный результат приложения, чтобы пользователи не заметили разницы.

#### Acceptance Criteria

1. WHEN рефакторинг завершён, THE View_Layer SHALL отображать те же цвета и шрифты, что и до рефакторинга
2. WHEN рефакторинг завершён, THE View_Layer SHALL сохранять все интерактивные состояния (выделение, hover) с теми же визуальными эффектами
3. THE Style_Manager SHALL использовать те же значения цветов, что были захардкожены в исходном коде, в качестве значений по умолчанию
4. IF тест проверяет цвет компонента View_Layer, THEN тест SHALL получать тот же результат до и после рефакторинга
