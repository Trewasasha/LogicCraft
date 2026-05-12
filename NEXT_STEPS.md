# 🎯 Следующие шаги для LogicCraft

**Дата**: 13 мая 2026  
**Текущая версия**: v1.4.0-dev  
**Прогресс по Roadmap**: 43% (7 из 16 недель)

---

## 🔥 Критические задачи (сделать СЕЙЧАС)

### 1. Исправить debug-логи в production коде ⏱️ 1 час
**Файл**: `src/logiccraft/utils/icon_manager.py`

```python
# БЫЛО (плохо):
print(f"[DEBUG] Корень проекта: {project_root}")
print(f"[DEBUG] Ищем иконки в: {self.icons_dir}")

# ДОЛЖНО БЫТЬ (хорошо):
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Корень проекта: {project_root}")
logger.debug(f"Ищем иконки в: {self.icons_dir}")
```

**Команды**:
```bash
# Открыть файл
code src/logiccraft/utils/icon_manager.py

# Заменить все print() на logger.debug()
# Добавить в начало файла:
# import logging
# logger = logging.getLogger(__name__)
```

---

### 2. Завершить Use Case диаграммы ⏱️ 2-3 дня

#### Текущий статус: 60% ✅

**Что уже сделано**:
- ✅ Модели `UseCaseActor` и `UseCaseScenario`
- ✅ Виджеты `ActorWidget` и `ScenarioWidget`
- ✅ Интеграция в контроллер
- ✅ Сохранение/загрузка

**Что нужно доделать**:

#### Задача 2.1: Интегрировать виджеты в MainWindow
**Файл**: `src/logiccraft/view/main_window.py`

```python
# Добавить обработчики для Use Case элементов:
def _on_uc_actor_added(self, actor_model):
    """Добавить виджет актёра на сцену"""
    from .widgets.actor_widget import ActorWidget
    widget = ActorWidget(
        name=actor_model.name,
        x=actor_model.x,
        y=actor_model.y,
        actor_id=actor_model.id
    )
    widget.signals.move_finished.connect(
        lambda aid, x, y: self.controller.on_uc_actor_move_finished(aid, x, y)
    )
    widget.signals.delete_requested.connect(self.controller.remove_uc_actor)
    self.scene.addItem(widget)
    self.uc_actor_map[actor_model.id] = widget

# Аналогично для сценариев
```

#### Задача 2.2: Добавить переключатель типов диаграмм
**Файл**: `src/logiccraft/view/panels/toolbox_panel.py`

```python
# Добавить в начало панели:
diagram_type_group = QGroupBox("Тип диаграммы")
diagram_type_layout = QVBoxLayout()

class_diagram_btn = QRadioButton("Диаграмма классов")
usecase_diagram_btn = QRadioButton("Use Case диаграмма")
class_diagram_btn.setChecked(True)

diagram_type_layout.addWidget(class_diagram_btn)
diagram_type_layout.addWidget(usecase_diagram_btn)
diagram_type_group.setLayout(diagram_type_layout)

# Подключить сигналы для переключения
```

#### Задача 2.3: Написать тесты
**Файл**: `test/test_use_case.py` (создать новый)

```python
import pytest
from logiccraft.models.diagram import UseCaseActor, UseCaseScenario

def test_create_actor():
    actor = UseCaseActor(name="Пользователь", x=100, y=100)
    assert actor.name == "Пользователь"
    assert actor.x == 100
    assert actor.y == 100

def test_create_scenario():
    scenario = UseCaseScenario(name="Войти в систему", x=200, y=200)
    assert scenario.name == "Войти в систему"
    
# Добавить еще 10-15 тестов
```

**Команды**:
```bash
# Запустить тесты
poetry run pytest test/test_use_case.py -v

# Проверить покрытие
poetry run pytest --cov=src/logiccraft/models test/test_use_case.py
```

---

### 3. Заполнить TODO в шаблонах ⏱️ 2-3 часа

**Файл**: `src/logiccraft/services/project_exporter.py`

#### Задача 3.1: Улучшить README шаблон
```python
def _generate_readme(self, settings: ProjectSettings) -> str:
    # БЫЛО:
    f"## Getting Started\n\nTODO: add setup instructions.\n"
    
    # ДОЛЖНО БЫТЬ:
    setup_instructions = self._get_setup_instructions(settings.language)
    return f"""# {settings.name}

{settings.description}

## Features

- Feature 1
- Feature 2
- Feature 3

## Installation

{setup_instructions}

## Usage

```{settings.language}
# Example code here
```

## Project Structure

```
{self._generate_tree_structure(settings)}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

{settings.license}
"""
```

#### Задача 3.2: Добавить API документацию
```python
def _generate_api_docs(self, settings: ProjectSettings) -> str:
    return f"""# API Documentation

## Overview

This document describes the API endpoints and their usage.

## Base URL

```
http://localhost:{settings.port or 8000}/api
```

## Endpoints

### GET /api/health
Health check endpoint.

**Response:**
```json
{{
  "status": "ok",
  "version": "{settings.version}"
}}
```

### GET /api/items
Get all items.

**Response:**
```json
[
  {{"id": 1, "name": "Item 1"}},
  {{"id": 2, "name": "Item 2"}}
]
```

## Authentication

[Add authentication details here]

## Error Handling

All errors follow this format:
```json
{{
  "error": "Error message",
  "code": "ERROR_CODE"
}}
```
"""
```

---

## ⚡ Задачи на эту неделю (Неделя 11)

### Понедельник (13 мая)
- [x] Ревью проекта
- [ ] Исправить debug-логи (1 час)
- [ ] Интегрировать ActorWidget в MainWindow (2 часа)

### Вторник (14 мая)
- [ ] Интегрировать ScenarioWidget в MainWindow (2 часа)
- [ ] Добавить переключатель типов диаграмм (3 часа)

### Среда (15 мая)
- [ ] Тестирование Use Case функционала (4 часа)
- [ ] Исправление багов (2 часа)

### Четверг (16 мая)
- [ ] Заполнить TODO в шаблонах (3 часа)
- [ ] Обновить документацию (2 часа)

### Пятница (17 мая)
- [ ] Финальное тестирование (3 часа)
- [ ] Коммит и push (1 час)
- [ ] Подготовка к Неделе 8 (1 час)

---

## 📅 План на следующие 2 недели

### Неделя 12 (20-24 мая): Завершение Use Case + начало Недели 8
- [ ] Полировка Use Case диаграмм
- [ ] Начать двойной клик для редактирования
- [ ] Inline-редактирование имени класса

### Неделя 13 (27-31 мая): Неделя 8 - Улучшение редактора
- [ ] Поиск классов по имени
- [ ] Подсветка связанных классов
- [ ] Автоматическое расположение (auto-layout)
- [ ] Мини-карта диаграммы

---

## 🎯 Цели на месяц (май 2026)

1. ✅ Завершить Use Case диаграммы (Неделя 11)
2. ✅ Завершить улучшение редактора (Неделя 8)
3. ✅ Исправить все критические баги
4. ✅ Увеличить покрытие тестами до 75%
5. ✅ Обновить всю документацию

---

## 📊 Метрики успеха

| Метрика | Сейчас | Цель на конец мая | Статус |
|---------|--------|-------------------|--------|
| Use Case прогресс | 60% | 100% | 🟡 |
| Покрытие тестами | 70% | 75% | 🟢 |
| Критических багов | 2 | 0 | 🔴 |
| TODO в коде | 5 | 0 | 🟡 |
| Недель завершено | 7 | 9 | 🟢 |

---

## 🚀 Команды для быстрого старта

```bash
# 1. Исправить debug-логи
code src/logiccraft/utils/icon_manager.py

# 2. Работа над Use Case
code src/logiccraft/view/main_window.py
code src/logiccraft/view/panels/toolbox_panel.py

# 3. Создать тесты
touch test/test_use_case.py
code test/test_use_case.py

# 4. Запустить тесты
poetry run pytest test/test_use_case.py -v

# 5. Проверить покрытие
poetry run pytest --cov=src/logiccraft

# 6. Запустить приложение
poetry run python -m logiccraft

# 7. Коммит изменений
git add .
git commit -m "feat: Завершена интеграция Use Case диаграмм"
git push origin main
```

---

## 📝 Чеклист перед коммитом

- [ ] Все тесты проходят (`pytest`)
- [ ] Нет debug-логов (`print()`)
- [ ] Нет TODO в критичных местах
- [ ] Документация обновлена
- [ ] CHANGELOG.md обновлен
- [ ] Код отформатирован (`black`)
- [ ] Нет lint ошибок (`flake8`)

---

## 🎓 Полезные ссылки

- [PROJECT_REVIEW.md](PROJECT_REVIEW.md) - Полное ревью проекта
- [docs/ROADMAP.md](docs/ROADMAP.md) - Дорожная карта
- [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) - Руководство разработчика
- [CHANGELOG.md](CHANGELOG.md) - История изменений

---

**Удачи в разработке! 🚀**
