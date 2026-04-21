# 🚀 Установка LogicCraft

Подробные инструкции по установке LogicCraft на различных операционных системах.

## Содержание

1. [Системные требования](#системные-требования)
2. [Установка через Poetry (рекомендуется)](#установка-через-poetry-рекомендуется)
3. [Установка через pip](#установка-через-pip)
4. [Установка из исходного кода](#установка-из-исходного-кода)
5. [Проверка установки](#проверка-установки)
6. [Устранение неполадок](#устранение-неполадок)

## Системные требования

### Минимальные требования
- **Python**: 3.13 или выше
- **ОС**: Windows 10+, macOS 11+, Linux (Ubuntu 20.04+)
- **RAM**: 512 MB свободной памяти
- **Дисплей**: 1280x720 или выше
- **Свободное место**: 100 MB

### Рекомендуемые требования
- **Python**: 3.13+
- **RAM**: 1 GB
- **Дисплей**: 1920x1080
- **Свободное место**: 500 MB

## Установка через Poetry (рекомендуется)

Poetry — современный менеджер зависимостей для Python, который обеспечивает изолированное окружение и точное управление версиями.

### Шаг 1: Установка Poetry

#### Windows
```powershell
# PowerShell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

#### macOS/Linux
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

#### Альтернативный способ (через pip)
```bash
pip install poetry
```

### Шаг 2: Клонирование репозитория
```bash
git clone https://github.com/yourusername/logiccraft.git
cd logiccraft
```

### Шаг 3: Установка зависимостей
```bash
# Установка основных зависимостей
poetry install

# Установка с dev зависимостями (для разработки)
poetry install --with dev
```

### Шаг 4: Запуск приложения
```bash
poetry run python -m src.logiccraft.main
```

## Установка через pip

Если вы предпочитаете использовать pip и виртуальные окружения:

### Шаг 1: Создание виртуального окружения
```bash
# Создание окружения
python -m venv logiccraft-env

# Активация (Windows)
logiccraft-env\Scripts\activate

# Активация (macOS/Linux)
source logiccraft-env/bin/activate
```

### Шаг 2: Клонирование и установка
```bash
git clone https://github.com/yourusername/logiccraft.git
cd logiccraft

# Установка зависимостей
pip install -r requirements.txt

# Или установка основных зависимостей
pip install pyqt6 pydantic
```

### Шаг 3: Запуск
```bash
python src/logiccraft/main.py
```

## Установка из исходного кода

Для разработчиков, которые хотят внести вклад в проект:

### Шаг 1: Форк и клонирование
```bash
# Форкните репозиторий на GitHub, затем клонируйте свой форк
git clone https://github.com/yourusername/logiccraft.git
cd logiccraft

# Добавьте upstream репозиторий
git remote add upstream https://github.com/original/logiccraft.git
```

### Шаг 2: Установка в режиме разработки
```bash
# С Poetry
poetry install --with dev

# С pip
pip install -e .
```

### Шаг 3: Настройка pre-commit хуков (опционально)
```bash
poetry run pre-commit install
```

## Проверка установки

### Проверка зависимостей
```bash
# С Poetry
poetry run python -c "import PyQt6; import pydantic; print('All dependencies installed successfully!')"

# С pip
python -c "import PyQt6; import pydantic; print('All dependencies installed successfully!')"
```

### Запуск тестов
```bash
# С Poetry
poetry run pytest

# С pip
python -m pytest
```

### Проверка версии
```bash
# С Poetry
poetry run python -c "from src.logiccraft import __version__; print(f'LogicCraft version: {__version__}')"
```

## Устранение неполадок

### Проблема: `ModuleNotFoundError: No module named 'PyQt6'`

**Решение:**
```bash
# Убедитесь, что PyQt6 установлен
pip install pyqt6

# Или с Poetry
poetry add pyqt6
```

### Проблема: `ImportError` при запуске

**Причина:** Неправильный PYTHONPATH или запуск не из корня проекта.

**Решение:**
```bash
# Убедитесь, что находитесь в корне проекта
cd /path/to/logiccraft

# Запуск через модуль
poetry run python -m src.logiccraft.main

# Или добавьте путь в PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python src/logiccraft/main.py
```

### Проблема: Окно не отображается на macOS

**Решение:**
```bash
# Установите PyQt6 через Homebrew
brew install pyqt6

# Или используйте conda
conda install pyqt
```

### Проблема: Ошибки при сохранении файлов

**Причина:** Недостаточно прав доступа.

**Решение:**
```bash
# Создайте директорию для сохранений
mkdir -p ~/.logiccraft/saves
chmod 755 ~/.logiccraft/saves
```

### Проблема: Медленная работа на Linux

**Решение:**
```bash
# Установите дополнительные зависимости
sudo apt-get install python3-pyqt6 python3-pyqt6.qtcore python3-pyqt6.qtgui

# Или используйте аппаратное ускорение
export QT_GRAPHICSSYSTEM=native
```

### Проблема: Poetry не найден после установки

**Решение:**
```bash
# Добавьте Poetry в PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Или используйте полный путь
~/.local/bin/poetry --version
```

### Проблема: Конфликт версий Python

**Решение:**
```bash
# Укажите конкретную версию Python для Poetry
poetry env use python3.13

# Или создайте окружение с нужной версией
poetry env use /usr/bin/python3.13
```

## Дополнительные настройки

### Настройка IDE

#### VS Code
Установите расширения:
- Python
- Pylance
- Black Formatter

#### PyCharm
1. Откройте проект
2. File → Settings → Project → Python Interpreter
3. Выберите Poetry Environment

### Переменные окружения

Создайте файл `.env` в корне проекта:
```bash
# Режим отладки
DEBUG=true

# Путь к конфигурации
LOGICCRAFT_CONFIG_PATH=~/.logiccraft

# Уровень логирования
LOG_LEVEL=INFO
```

### Настройка темы

Создайте файл `theme_pref.json`:
```json
{
    "theme": "light",
    "language": "ru",
    "auto_save": true,
    "grid_enabled": true
}
```

## Обновление

### Обновление через Poetry
```bash
git pull origin main
poetry install
```

### Обновление через pip
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## Удаление

### Удаление Poetry окружения
```bash
poetry env remove python
```

### Удаление pip окружения
```bash
# Деактивация окружения
deactivate

# Удаление папки
rm -rf logiccraft-env
```

### Очистка конфигурации
```bash
rm -rf ~/.logiccraft
```

---

Если у вас остались вопросы, создайте Issue в GitHub репозитории или обратитесь к [руководству пользователя](USER_GUIDE.md). 🚀