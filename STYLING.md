# LogicCraft — Руководство по стилям

Все стили приложения сосредоточены в двух файлах. Менять нужно только их — больше нигде цвета и размеры не задаются.

---

## Файл 1: `src/logiccraft/view/theme.py`

Отвечает за **графические элементы на холсте** — карточки, линии, стрелки, точки привязки, фон сцены. Эти элементы не поддерживают CSS/QSS напрямую, поэтому стили задаются через Python-константы.

### Как изменить

Найди нужную секцию и поменяй значение по умолчанию в dataclass:

```python
# Было
@dataclass(frozen=True)
class _CardStyle:
    BACKGROUND: str = "#f5f5dc"

# Стало
@dataclass(frozen=True)
class _CardStyle:
    BACKGROUND: str = "#ffffff"
```

---

### CardStyle — карточка UML-класса

| Токен | Значение | Описание |
|---|---|---|
| `BACKGROUND` | `#f5f5dc` | Фон карточки (бежевый) |
| `BORDER` | `#4169E1` | Цвет рамки (синий) |
| `SELECTED_BORDER` | `#DC143C` | Цвет рамки при выделении (красный) |
| `BORDER_WIDTH` | `2` | Толщина рамки (px) |
| `SELECTED_BORDER_WIDTH` | `3` | Толщина рамки при выделении (px) |
| `HEADER_BG` | `#4169E1` | Фон заголовка (синий) |
| `HEADER_TEXT` | `white` | Цвет текста заголовка |
| `ATTRS_TEXT` | `#2c3e50` | Цвет текста атрибутов (тёмно-синий) |
| `METHODS_TEXT` | `#27ae60` | Цвет текста методов (зелёный) |
| `DIVIDER` | `#4169E1` | Цвет разделителей между секциями |
| `HEADER_FONT` | Arial 10 Bold | Шрифт заголовка |
| `ATTRS_FONT` | Menlo 9 | Шрифт атрибутов |
| `METHODS_FONT` | Menlo 9 | Шрифт методов |

Чтобы изменить шрифт, отредактируй property в классе `_CardStyle`:

```python
@property
def HEADER_FONT(self) -> QFont:
    return QFont("Arial", 10, QFont.Weight.Bold)  # шрифт, размер, начертание
```

---

### ConnectionStyle — линия связи

| Токен | Значение | Описание |
|---|---|---|
| `LINE_COLOR` | `#666666` | Цвет линии (серый) |
| `LINE_WIDTH` | `2` | Толщина линии (px) |
| `SELECTED_COLOR` | `#DC143C` | Цвет линии при выделении (красный) |
| `SELECTED_WIDTH` | `3` | Толщина линии при выделении (px) |

---

### SceneStyle — холст (фон и сетка)

| Токен | Значение | Описание |
|---|---|---|
| `BACKGROUND` | `#fafafa` | Цвет фона холста |
| `GRID_COLOR` | `#e0e0e0` | Цвет линий сетки |
| `GRID_WIDTH` | `0.5` | Толщина линий сетки (px) |
| `GRID_STEP` | `50` | Шаг сетки (px) |
| `TEMP_LINE_COLOR` | `#4169E1` | Цвет пунктира при создании связи |

---

### AnchorStyle — точки привязки

Красные кружки на карточке, за которые тянут для создания связи.

| Токен | Значение | Описание |
|---|---|---|
| `NORMAL_COLOR` | `#FF6B6B` | Цвет в обычном состоянии |
| `HOVER_COLOR` | `#FF4444` | Цвет при наведении мыши |
| `BORDER_COLOR` | `#FFFFFF` | Цвет обводки кружка |
| `BORDER_WIDTH` | `1.5` | Толщина обводки (px) |
| `HOVER_SCALE` | `1.2` | Масштаб при наведении (1.0 = без изменений) |

---

### ArrowStyle — наконечники стрелок

| Токен | Значение | Описание |
|---|---|---|
| `COLOR` | `#666666` | Цвет наконечника |
| `WIDTH_NORMAL` | `2.0` | Толщина контура (полый наконечник) |
| `WIDTH_THIN` | `1.5` | Толщина контура (закрашенный наконечник) |
| `SIZE` | `12` | Размер наконечника (px) |

Форма наконечника зависит от типа связи и не настраивается через токены:

| Тип связи | Форма | Заливка |
|---|---|---|
| `association` | треугольник | закрашен цветом `COLOR` |
| `inheritance` | треугольник | пустой |
| `composition` | ромб | закрашен цветом `COLOR` |
| `aggregation` | ромб | пустой |

---

## Файл 2: `src/logiccraft/style.qss`

Отвечает за **стандартные Qt-виджеты** — тулбар, диалоги, статусбар. Синтаксис аналогичен CSS, но с ограничениями Qt.

Файл загружается автоматически при старте приложения.

### Текущие секции

```css
/* === Toolbar === */
QToolBar { ... }

/* === Dialogs === */
QDialog { ... }
QDialog QLabel { ... }
QDialog QPushButton { ... }
QDialog QPushButton:hover { ... }

/* === StatusBar === */
QStatusBar { ... }
```

### Поддерживаемые псевдоклассы

`:hover`, `:pressed`, `:disabled`, `:checked`, `:focus`

### Пример добавления стиля

```css
/* Кнопка отмены в диалогах */
QDialog QPushButton[text="Cancel"] {
    background-color: #cccccc;
    color: #333333;
}
```

### Ограничения QSS

- Не поддерживаются CSS-переменные (`--color: red`)
- Не поддерживается `calc()`
- Нет flexbox/grid — позиционирование только через Qt layouts
- `border-radius` работает только если задан `background-color`

---

---

## Как создать тему с нуля

Тема — это полный набор значений для всех токенов в `theme.py` и отдельный `.qss` файл для виджетов.

### Шаг 1 — Создай файл темы

Создай новый файл рядом с `theme.py`, например `theme_dark.py`:

```
src/logiccraft/view/
├── theme.py          ← светлая тема (по умолчанию)
├── theme_dark.py     ← твоя новая тёмная тема
```

Скопируй содержимое `theme.py` в новый файл и измени значения токенов:

```python
# src/logiccraft/view/theme_dark.py

from dataclasses import dataclass
from PyQt6.QtGui import QFont
import logging
import os


@dataclass(frozen=True)
class _CardStyle:
    BACKGROUND: str = "#1e1e2e"       # тёмный фон карточки
    BORDER: str = "#89b4fa"           # голубая рамка
    SELECTED_BORDER: str = "#f38ba8"  # розовое выделение
    HEADER_BG: str = "#313244"        # тёмный заголовок
    HEADER_TEXT: str = "#cdd6f4"      # светлый текст
    ATTRS_TEXT: str = "#a6e3a1"       # зелёный текст атрибутов
    METHODS_TEXT: str = "#89dceb"     # голубой текст методов
    DIVIDER: str = "#45475a"          # тёмный разделитель
    BORDER_WIDTH: int = 2
    SELECTED_BORDER_WIDTH: int = 3

    @property
    def HEADER_FONT(self) -> QFont:
        return QFont("Arial", 10, QFont.Weight.Bold)

    @property
    def ATTRS_FONT(self) -> QFont:
        return QFont("Menlo", 9)

    @property
    def METHODS_FONT(self) -> QFont:
        return QFont("Menlo", 9)


@dataclass(frozen=True)
class _ConnectionStyle:
    LINE_COLOR: str = "#6c7086"
    LINE_WIDTH: int = 2
    SELECTED_COLOR: str = "#f38ba8"
    SELECTED_WIDTH: int = 3


@dataclass(frozen=True)
class _SceneStyle:
    BACKGROUND: str = "#181825"   # почти чёрный фон
    GRID_COLOR: str = "#313244"   # едва заметная сетка
    GRID_WIDTH: float = 0.5
    GRID_STEP: int = 50
    TEMP_LINE_COLOR: str = "#89b4fa"


@dataclass(frozen=True)
class _AnchorStyle:
    NORMAL_COLOR: str = "#f38ba8"
    HOVER_COLOR: str = "#eba0ac"
    BORDER_COLOR: str = "#1e1e2e"
    BORDER_WIDTH: float = 1.5
    HOVER_SCALE: float = 1.2


@dataclass(frozen=True)
class _ArrowStyle:
    COLOR: str = "#6c7086"
    WIDTH_NORMAL: float = 2.0
    WIDTH_THIN: float = 1.5
    SIZE: int = 12


CardStyle = _CardStyle()
ConnectionStyle = _ConnectionStyle()
SceneStyle = _SceneStyle()
AnchorStyle = _AnchorStyle()
ArrowStyle = _ArrowStyle()


def apply_stylesheet(app) -> None:
    qss_path = os.path.join(os.path.dirname(__file__), "..", "style_dark.qss")
    qss_path = os.path.normpath(qss_path)
    try:
        with open(qss_path, "r", encoding="utf-8") as f:
            content = f.read()
        app.setStyleSheet(content)
    except FileNotFoundError:
        logging.warning("style_dark.qss not found at %s, skipping stylesheet", qss_path)
```

### Шаг 2 — Создай QSS файл для виджетов

Создай `src/logiccraft/style_dark.qss` рядом с `style.qss`:

```css
/* === Toolbar === */
QToolBar {
    background-color: #313244;
    border-bottom: 1px solid #45475a;
    spacing: 4px;
}

/* === Dialogs === */
QDialog {
    background-color: #1e1e2e;
}

QDialog QLabel {
    color: #cdd6f4;
}

QDialog QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    padding: 4px 12px;
    border-radius: 3px;
}

QDialog QPushButton:hover {
    background-color: #74c7ec;
}

/* === StatusBar === */
QStatusBar {
    background-color: #313244;
    color: #cdd6f4;
}
```

### Шаг 3 — Подключи тему в `main.py`

Открой `src/logiccraft/main.py` и замени импорт темы:

```python
# Было — светлая тема
from logiccraft.view.theme import apply_stylesheet

# Стало — тёмная тема
from logiccraft.view.theme_dark import apply_stylesheet
```

> Все токены (`CardStyle`, `ConnectionStyle` и т.д.) импортируются автоматически из того же файла темы через остальные модули. Менять импорты в виджетах не нужно — они всегда берут из `theme.py`. Поэтому если хочешь переключать темы динамически, нужно будет доработать механизм импорта.

### Шаг 4 — Проверь тему

Запусти приложение и убедись что все элементы отображаются корректно:

```bash
poetry run python -m src.logiccraft.main
```

Чеклист проверки:
- [ ] Фон холста и сетка видны
- [ ] Карточки читаемы (текст контрастен к фону)
- [ ] Заголовок карточки отличается от тела
- [ ] Выделение карточки (клик) меняет цвет рамки
- [ ] Линии связей видны на фоне холста
- [ ] Точки привязки видны при выделении карточки
- [ ] Hover на точке привязки меняет цвет
- [ ] Диалоги (Edit Class, Connection Properties) читаемы
- [ ] Тулбар и статусбар стилизованы

### Советы по подбору цветов

**Контрастность** — текст на фоне должен иметь соотношение контрастности не ниже 4.5:1. Проверить можно на [contrast-ratio.com](https://contrast-ratio.com).

**Согласованность** — используй одну базовую палитру. Хорошие готовые палитры:
- [Catppuccin](https://github.com/catppuccin/catppuccin) — пастельные тёмные темы
- [Solarized](https://ethanschoonover.com/solarized/) — классика
- [Nord](https://www.nordtheme.com/) — холодные оттенки

**Акцентный цвет** — один цвет для интерактивных элементов (`BORDER`, `HEADER_BG`, кнопки в QSS). Используй его везде одинаково.

**Состояния** — `SELECTED_BORDER` и `SELECTED_COLOR` должны заметно отличаться от обычного состояния, но не конфликтовать с фоном.

---

## Цветовая палитра

Все цвета, используемые в приложении:

| Цвет | Hex | Где используется |
|---|---|---|
| Синий | `#4169E1` | Рамка карточки, заголовок, разделители, пунктир связи, кнопки |
| Красный | `#DC143C` | Выделение карточки и линии |
| Бежевый | `#f5f5dc` | Фон карточки |
| Тёмно-синий | `#2c3e50` | Текст атрибутов |
| Зелёный | `#27ae60` | Текст методов |
| Серый | `#666666` | Линии связей, наконечники |
| Светло-красный | `#FF6B6B` | Точки привязки (normal) |
| Красный | `#FF4444` | Точки привязки (hover) |
| Белый | `#FFFFFF` | Обводка точек привязки, текст заголовка |
| Почти белый | `#fafafa` | Фон холста |
| Светло-серый | `#e0e0e0` | Сетка холста |
