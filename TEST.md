# Руководство по тестированию LogicCraft

Данный документ описывает, какие тесты запускать на каждом этапе разработки проекта LogicCraft.

## Быстрый старт

```bash
# Установка зависимостей
pip install pytest pydantic

# Запуск всех тестов
PYTHONPATH=./src python -m pytest test/ -v

# Запуск тестов конкретного модуля
PYTHONPATH=./src python -m pytest test/test_models.py -v
```

---

## Этап 1: Ядро и Интерактивный Холст (Месяц 1)

### Запускаемые тесты

```bash
PYTHONPATH=./src python -m pytest test/test_models.py test/test_generators.py -v
```

### Что проверяется

| Тестовый файл | Классы/функции | Описание |
|--------------|----------------|----------|
| `test_models.py` | `TestUMLProperty` | Создание свойств класса с разными visibility |
| `test_models.py` | `TestUMLMethod` | Создание методов с параметрами |
| `test_models.py` | `TestUMLNode` | Создание узлов (классов) с авто-generated UUID |
| `test_models.py` | `TestUMLConnection` | Создание связей между классами |
| `test_models.py` | `TestUMLDiagram` | Сериализация/десериализация диаграмм |
| `test_generators.py` | `TestDiagramMapperParseAttribute` | Парсинг атрибутов вида `+ name: str` |
| `test_generators.py` | `TestDiagramMapperParseMethod` | Парсинг методов вида `+ getName(): str` |
| `test_generators.py` | `TestDiagramMapperFormatAttribute` | Форматирование атрибутов обратно в строку |
| `test_generators.py` | `TestDiagramMapperFormatMethod` | Форматирование методов обратно в строку |
| `test_generators.py` | `TestDiagramMapperCardToNode` | Конвертация UI-карточки в модель |
| `test_generators.py` | `TestDiagramMapperNodeToCard` | Конвертация модели в UI-карточку |
| `test_generators.py` | `TestDiagramIOSave` | Сохранение диаграммы в JSON |
| `test_generators.py` | `TestDiagramIOLoad` | Загрузка диаграммы из JSON |

### Критерии приёмки

- [ ] Все тесты `test_models.py` проходят
- [ ] Все тесты `test_generators.py` проходят
- [ ] UUID генерируются корректно для всех сущностей
- [ ] Сериализация в JSON работает без ошибок

---

## Этап 2: Связи и Геометрия (Месяц 2)

### Запускаемые тесты

```bash
PYTHONPATH=./src python -m pytest test/test_connections.py -v
```

### Что проверяется

#### Неделя 1: Магнитные точки (Anchors)

| Тест | Описание |
|------|----------|
| `test_calculate_anchor_top_center` | Anchor в центре верхней грани |
| `test_calculate_anchor_bottom_center` | Anchor в центре нижней грани |
| `test_calculate_anchor_left_center` | Anchor в центре левой грани |
| `test_calculate_anchor_right_center` | Anchor в центре правой грани |
| `test_calculate_anchor_invalid_position` | Обработка неверной позиции |

#### Неделя 2: Отрисовка линий

| Тест | Описание |
|------|----------|
| `test_create_line_between_blocks` | Создание линии между блоками |
| `test_line_updates_on_block_move` | Обновление линии при движении блока |
| `test_line_with_multiplicity_label` | Линия с кратностью (1..*) |

#### Неделя 3: Наконечники стрелок

| Тест | Описание |
|------|----------|
| `test_inheritance_arrowhead_triangle` | Наследование - треугольник |
| `test_composition_arrowhead_diamond` | Композиция - закрашенный ромб |
| `test_aggregation_arrowhead_diamond_unfilled` | Агрегация - пустой ромб |
| `test_dependency_arrowhead_arrow` | Зависимость - стрелка |
| `test_arrowhead_angle_calculation` | Расчёт угла наконечника |

#### Неделя 4: Математический движок

| Тест | Описание |
|------|----------|
| `test_recalculate_line_on_block_move` | Пересчёт координат при движении |
| `test_find_best_anchor_pair` | Поиск оптимальных anchor-точек |
| `test_line_intersection_avoidance` | Избежание пересечений линий |
| `test_orthogonal_line_routing` | Ортогональная маршрутизация |

### Критерии приёмки

- [ ] Линии корректно соединяют блоки при их движении
- [ ] Наконечники отображаются правильно для каждого типа связи
- [ ] Линии не пересекаются (или минимизируют пересечения)
- [ ] Anchor-точки рассчитываются на границах блоков

---

## Этап 3: Редактирование и UX (Месяц 3)

### Запускаемые тесты

```bash
PYTHONPATH=./src python -m pytest test/test_editor_ux.py -v
```

### Что проверяется

#### Неделя 1: Inspector Panel

| Тест | Описание |
|------|----------|
| `test_inspector_panel_shows_selected_class` | Отображение свойств выбранного класса |
| `test_inspector_panel_clear_on_deselect` | Очистка при снятии выделения |
| `test_inspector_name_change_updates_class` | Изменение имени через inspector |
| `test_inspector_property_edit` | Редактирование свойства |
| `test_inspector_visibility_toggle` | Переключение visibility |

#### Неделя 2: Управление контентом

| Тест | Описание |
|------|----------|
| `test_add_attribute_to_class` | Добавление атрибута |
| `test_add_attribute_with_default_value` | Добавление со значением по умолчанию |
| `test_remove_attribute_from_class` | Удаление атрибута |
| `test_add_method_to_class` | Добавление метода |
| `test_remove_method_from_class` | Удаление метода |
| `test_add_method_with_parameters` | Добавление метода с параметрами |

#### Неделя 3: Горячие клавиши и меню

| Тест | Описание |
|------|----------|
| `test_ctrl_s_triggers_save` | Ctrl+S - сохранение |
| `test_ctrl_z_triggers_undo` | Ctrl+Z - отмена |
| `test_ctrl_y_triggers_redo` | Ctrl+Y - повтор |
| `test_delete_key_removes_selection` | Delete - удаление |
| `test_unregistered_key_ignored` | Неизвестные клавиши игнорируются |
| `test_context_menu_shows_on_right_click` | Контекстное меню по правому клику |
| `test_context_menu_add_class_option` | Опция "Добавить класс" |
| `test_context_menu_delete_option` | Опция "Удалить" |
| `test_context_menu_hides_on_selection` | Скрытие после выбора |

#### Неделя 4: Undo/Redo

| Тест | Описание |
|------|----------|
| `test_undo_restores_previous_state` | Undo восстанавливает состояние |
| `test_redo_restores_undone_state` | Redo восстанавливает отменённое |
| `test_undo_at_beginning_returns_none` | Undo в начале истории |
| `test_redo_at_end_returns_none` | Redo в конце истории |
| `test_history_limit_enforced` | Ограничение размера истории |
| `test_new_state_clears_redo_stack` | Новое состояние очищает redo |
| `test_state_deep_copy` | Глубокое копирование состояний |

### Критерии приёмки

- [ ] Inspector корректно отображает и редактирует свойства
- [ ] Горячие клавиши работают (Ctrl+S, Ctrl+Z, Ctrl+Y, Delete)
- [ ] Undo/Redo работает для всех операций
- [ ] История ограничена (по умолчанию 50 состояний)

---

## Этап 4: Codegen (Генерация кода) (Месяц 4)

### Запускаемые тесты

```bash
PYTHONPATH=./src python -m pytest test/test_codegen.py -v
```

### Что проверяется

#### Неделя 1: Jinja2 шаблоны

| Тест | Описание |
|------|----------|
| `test_template_class_generation` | Генерация Python-класса |
| `test_template_with_inheritance` | Класс с наследованием |
| `test_template_with_static_method` | Статические методы (@staticmethod) |
| `test_template_with_abstract_method` | Абстрактные методы (ABC) |
| `test_template_with_default_values` | Атрибуты со значениями по умолчанию |

#### Неделя 2: Трансляция связей

| Тест | Описание |
|------|----------|
| `test_inheritance_to_class_parent` | Наследование → parent class |
| `test_association_to_import` | Ассоциация → import |
| `test_composition_to_field` | Композиция → поле класса |
| `test_multiplicity_to_type_hint` | Кратность → list[Type] |
| `test_dependency_to_import` | Зависимость → import |

#### Неделя 3: Окно предпросмотра

| Тест | Описание |
|------|----------|
| `test_preview_shows_generated_files` | Отображение списка файлов |
| `test_preview_switch_tabs` | Переключение вкладок |
| `test_preview_syntax_highlighting` | Подсветка синтаксиса |
| `test_preview_copy_to_clipboard` | Копирование в буфер |

#### Неделя 4: Экспорт проекта

| Тест | Описание |
|------|----------|
| `test_export_creates_directory_structure` | Создание структуры папок |
| `test_export_writes_files` | Запись файлов |
| `test_export_creates_init_files` | Создание __init__.py |
| `test_export_overwrite_existing` | Перезапись существующих |
| `test_export_preserves_structure` | Сохранение вложенности |

#### Интеграционные тесты

| Тест | Описание |
|------|----------|
| `test_full_pipeline_diagram_to_files` | Полный pipeline: диаграмма → файлы |

### Критерии приёмки

- [ ] Генерируются валидные Python-файлы
- [ ] Наследование корректно преобразуется в class Child(Parent)
- [ ] Ассоциации преобразуются в import и поля
- [ ] Экспорт создаёт рабочую структуру проекта

---

## Этап 5: Полировка и Релиз (Месяц 5)

### Запускаемые тесты

```bash
PYTHONPATH=./src python -m pytest test/test_polish_release.py -v
```

### Что проверяется

#### Неделя 1: Темы

| Тест | Описание |
|------|----------|
| `test_theme_manager_initializes_with_default` | Инициализация темы |
| `test_theme_switch_to_dark` | Переключение на тёмную тему |
| `test_theme_switch_to_light` | Переключение на светлую тему |
| `test_theme_colors_defined_for_both_modes` | Все цвета определены |
| `test_theme_applies_to_components` | Применение к компонентам |
| `test_theme_persistence` | Сохранение предпочтения |
| `test_theme_detection_from_system` | Автоопределение системной темы |

#### Неделя 2: Экспорт изображений

| Тест | Описание |
|------|----------|
| `test_export_to_png` | Экспорт в PNG |
| `test_export_to_svg` | Экспорт в SVG |
| `test_export_resolution_setting` | Настройка DPI |
| `test_export_with_transparent_background` | Прозрачный фон |
| `test_export_preserves_element_positions` | Сохранение позиций |
| `test_export_creates_output_directory` | Создание директории |

#### Неделя 3: Кроссплатформенность

| Тест | Описание |
|------|----------|
| `test_pathlib_used_for_paths` | Использование pathlib |
| `test_utf8_encoding_for_files` | UTF-8 кодировка |
| `test_no_platform_specific_imports` | Нет платформенных импортов |
| `test_flet_run_usage` | Использование ft.run() |
| `test_windows_specific_behavior` | Windows-специфика |
| `test_macos_specific_behavior` | macOS-специфика |

#### Неделя 4: Сборка

| Тест | Описание |
|------|----------|
| `test_flet_build_command_windows` | Сборка для Windows |
| `test_flet_build_command_macos` | Сборка для macOS |
| `test_build_includes_assets` | Включение ресурсов |
| `test_build_version_info` | Информация о версии |
| `test_build_cleans_output_directory` | Очистка перед сборкой |
| `test_build_error_handling` | Обработка ошибок |

#### Производительность

| Тест | Описание |
|------|----------|
| `test_large_diagram_loading` | Загрузка больших диаграмм |
| `test_drag_performance` | Производительность drag |

### Критерии приёмки

- [ ] Dark/Light темы переключаются корректно
- [ ] Экспорт PNG/SVG работает
- [ ] Приложение запускается на Windows и macOS
- [ ] Сборка в .exe и .app проходит успешно

---

## Регрессионное тестирование

Перед каждым релизом запускать полный набор:

```bash
PYTHONPATH=./src python -m pytest test/ -v --tb=short
```

### Ожидаемые результаты

| Этап | Тесты | Минимальный % прохождения |
|------|-------|---------------------------|
| Месяц 1 | 36 | 100% |
| Месяц 2 | 17 | 100% |
| Месяц 3 | 25 | 100% |
| Месяц 4 | 24 | 100% |
| Месяц 5 | 13 | 90% |

---

## CI/CD интеграция

### GitHub Actions пример

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          pip install pytest pydantic flet
      - name: Run tests
        run: |
          PYTHONPATH=./src python -m pytest test/ -v
```

---

## Добавление новых тестов

1. Создайте тестовый файл в `test/` с префиксом `test_`
2. Используйте pytest:

```python
import pytest

def test_new_feature():
    """Description of what this test checks."""
    result = new_feature_function()
    assert result == expected_value
```

3. Запустите для проверки:

```bash
PYTHONPATH=./src python -m pytest test/test_your_file.py -v
```

---

## Устранение неполадок

### Проблема: ModuleNotFoundError: No module named 'logiccraft'

**Решение:** Установите PYTHONPATH

```bash
export PYTHONPATH=./src
# или
PYTHONPATH=./src python -m pytest test/
```

### Проблема: ModuleNotFoundError: No module named 'pydantic'

**Решение:** Установите зависимости

```bash
pip install pydantic flet pytest
```

### Проблема: Тесты падают с ошибками импорта flet.canvas

**Примечание:** Некоторые тесты используют mock-объекты для UI-компонентов. Это нормально для unit-тестов.

---

## Контакты

По вопросам тестирования обращайтесь к команде:
- **Саша (Architect)** - интеграция и CI/CD
- **Даша (Frontend)** - UI тесты
- **Семён (Backend)** - модели и кодогенерация
