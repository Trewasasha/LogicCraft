# Implementation Plan: view-styles-extraction

## Overview

Рефакторинг view-слоя: вынос всех захардкоженных цветов, шрифтов и размеров из 5 Python-файлов в централизованное хранилище `theme.py` и QSS-файл `style.qss`. Поведение приложения не меняется.

## Tasks

- [x] 1. Создать theme.py с централизованными Style_Token
  - Определить frozen dataclass-секции: CardStyle, ConnectionStyle, SceneStyle, AnchorStyle, ArrowStyle
  - Добавить все 11 исходных цветов в соответствующие секции
  - Добавить шрифтовые токены в CardStyle
  - Реализовать функцию apply_stylesheet(app) с обработкой отсутствия файла
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 7.3, 7.4, 8.1_

- [x] 2. Заполнить style.qss QSS-правилами для виджетов
  - Добавить секцию QToolBar
  - Добавить секцию QDialog
  - Добавить секцию QStatusBar
  - _Requirements: 7.2, 8.2, 8.3_

- [x] 3. Отрефакторить uml_card.py
  - [x] 3.1 Заменить все строковые литералы цветов на токены из CardStyle
    - Фон, рамка, заголовок, текст атрибутов, текст методов, разделители
    - Цвет выделения и ширина пера
    - Шрифты заголовка, атрибутов, методов
    - _Requirements: 2.1, 2.2, 2.3, 2.5_
  - [ ]* 3.2 Написать property-тест Property 1: UMLCard использует цвета из CardStyle при инициализации
    - **Property 1: UMLCard использует цвета из CardStyle при инициализации**
    - **Validates: Requirements 2.1**
  - [ ]* 3.3 Написать property-тест Property 2: UMLCard использует цвет выделения из CardStyle
    - **Property 2: UMLCard использует цвет выделения из CardStyle**
    - **Validates: Requirements 2.2**
  - [ ]* 3.4 Написать property-тест Property 3: UMLCard использует шрифты из CardStyle
    - **Property 3: UMLCard использует шрифты из CardStyle**
    - **Validates: Requirements 2.3**
  - [ ]* 3.5 Написать smoke-тест: отсутствие строковых литералов цветов в uml_card.py
    - **Validates: Requirements 2.5**

- [x] 4. Отрефакторить anchor_point.py
  - [x] 4.1 Заменить все строковые литералы цветов на токены из AnchorStyle
    - Нормальный цвет, hover-цвет, цвет рамки, ширина рамки, масштаб hover
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  - [ ]* 4.2 Написать property-тест Property 4: AnchorPoint использует цвета из AnchorStyle
    - **Property 4: AnchorPoint использует цвета из AnchorStyle**
    - **Validates: Requirements 3.1, 3.2, 3.3**
  - [ ]* 4.3 Написать smoke-тест: отсутствие строковых литералов цветов в anchor_point.py
    - **Validates: Requirements 3.4**

- [x] 5. Отрефакторить arrow_head.py
  - [x] 5.1 Заменить все строковые литералы цветов на токены из ArrowStyle
    - Цвет пера и заливки для всех 4 типов связей
    - Размер наконечника
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  - [ ]* 5.2 Написать property-тест Property 5: ArrowHead использует цвета из ArrowStyle для любого типа связи
    - **Property 5: ArrowHead использует цвета из ArrowStyle для любого типа связи**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**
  - [ ]* 5.3 Написать smoke-тест: отсутствие строковых литералов цветов в arrow_head.py
    - **Validates: Requirements 4.5**

- [x] 6. Отрефакторить connection_line.py
  - [x] 6.1 Заменить все строковые литералы цветов на токены из ConnectionStyle
    - Цвет и ширина пера нормального состояния
    - Цвет и ширина пера выделенного состояния
    - _Requirements: 5.1, 5.2, 5.3_
  - [ ]* 6.2 Написать property-тест Property 6: ConnectionLine использует цвета из ConnectionStyle
    - **Property 6: ConnectionLine использует цвета из ConnectionStyle**
    - **Validates: Requirements 5.1, 5.2**
  - [ ]* 6.3 Написать smoke-тест: отсутствие строковых литералов цветов в connection_line.py
    - **Validates: Requirements 5.3**

- [x] 7. Отрефакторить diagram_scene.py
  - [x] 7.1 Заменить все строковые литералы цветов на токены из SceneStyle
    - Цвет фона, цвет и толщина сетки, шаг сетки
    - Цвет временной линии связи
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  - [ ]* 7.2 Написать property-тест Property 7: DiagramScene использует цвет фона из SceneStyle
    - **Property 7: DiagramScene использует цвет фона из SceneStyle**
    - **Validates: Requirements 6.1**
  - [ ]* 7.3 Написать smoke-тест: отсутствие строковых литералов цветов в diagram_scene.py
    - **Validates: Requirements 6.4**

- [x] 8. Checkpoint — убедиться что все тесты проходят
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Подключить apply_stylesheet в main.py и написать unit-тесты для theme.py
  - [x] 9.1 Вызвать apply_stylesheet(app) в Application.__init__ после создания QApplication
    - _Requirements: 7.1, 7.2_
  - [-]* 9.2 Написать unit-тесты для theme.py
    - test_theme_has_all_sections
    - test_theme_tokens_accessible_without_init
    - test_theme_contains_all_original_colors
    - test_apply_stylesheet_calls_set_stylesheet
    - test_apply_stylesheet_missing_file
    - **Validates: Requirements 1.1–1.5, 7.1–7.4**
  - [ ]* 9.3 Написать property-тест Property 8: обратная совместимость цветов
    - **Property 8: Обратная совместимость цветов**
    - **Validates: Requirements 9.1, 9.2, 9.3**

- [x] 10. Final checkpoint — все тесты проходят
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Задачи с `*` — опциональные тесты, можно пропустить для быстрого MVP
- Рефакторинг не меняет поведение приложения — только организацию констант
- Все исходные цвета сохраняются как значения по умолчанию в токенах
