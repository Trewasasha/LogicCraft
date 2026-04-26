# 🔀 Git Workflow для команды LogicCraft

## 📋 Текущая проблема

Сейчас команда работает напрямую с веткой `main`, что создает риски:
- ❌ Нестабильный код попадает в основную ветку
- ❌ Сложно откатить изменения
- ❌ Нет code review
- ❌ Конфликты при одновременной работе
- ❌ Нет истории фич и багфиксов

## ✅ Рекомендуемый Git Flow

### Структура веток

```
main (production-ready)
  ↑
develop (integration)
  ↑
feature/* (новые функции)
bugfix/* (исправления)
hotfix/* (срочные исправления)
```

### Основные ветки

#### `main` — Production
- **Всегда стабильная** версия
- Только проверенный код
- Каждый коммит = релиз
- **Защищена** от прямых коммитов
- Только через Pull Request с ревью

#### `develop` — Integration
- Текущая разработка
- Интеграция всех фич
- Тестирование перед релизом
- Может быть нестабильной

### Временные ветки

#### `feature/*` — Новые функции
```bash
# Создание
git checkout develop
git checkout -b feature/export-project

# Работа
git add .
git commit -m "feat: add project export dialog"

# Завершение
git push origin feature/export-project
# Создать Pull Request: feature/export-project → develop
```

**Примеры:**
- `feature/export-project` — экспорт проектов
- `feature/sequence-diagrams` — диаграммы последовательности
- `feature/dark-theme` — темная тема

#### `bugfix/*` — Исправления багов
```bash
git checkout develop
git checkout -b bugfix/connection-arrow-duplicate

git commit -m "fix: remove duplicate arrow heads"
git push origin bugfix/connection-arrow-duplicate
# PR: bugfix/connection-arrow-duplicate → develop
```

#### `hotfix/*` — Срочные исправления
```bash
# Только для критичных багов в production
git checkout main
git checkout -b hotfix/critical-crash

git commit -m "hotfix: fix critical crash on save"
git push origin hotfix/critical-crash
# PR: hotfix/critical-crash → main И develop
```

## 🚀 Workflow для команды

### 1️⃣ Начало работы над задачей

```bash
# Обновить develop
git checkout develop
git pull origin develop

# Создать ветку для задачи
git checkout -b feature/my-feature

# Или для бага
git checkout -b bugfix/fix-something
```

### 2️⃣ Работа над кодом

```bash
# Регулярные коммиты
git add .
git commit -m "feat: add export dialog UI"

git add .
git commit -m "feat: implement export logic"

git add .
git commit -m "test: add export tests"

# Пушить в свою ветку
git push origin feature/my-feature
```

### 3️⃣ Создание Pull Request

**На GitHub:**
1. Перейти в репозиторий
2. Нажать "New Pull Request"
3. Выбрать: `feature/my-feature` → `develop`
4. Заполнить описание:

```markdown
## Описание
Добавлена функция экспорта проектов с настройками

## Изменения
- ✅ Создан ProjectExportDialog
- ✅ Добавлены настройки стиля кода
- ✅ Реализован предпросмотр структуры

## Тестирование
- [x] Ручное тестирование
- [x] Unit тесты добавлены
- [ ] Integration тесты

## Скриншоты
![Export Dialog](screenshot.png)
```

5. Назначить ревьюера (другого члена команды)
6. Добавить метки: `feature`, `frontend`, `backend`

### 4️⃣ Code Review

**Ревьюер проверяет:**
- ✅ Код соответствует стандартам
- ✅ Тесты проходят
- ✅ Нет конфликтов
- ✅ Документация обновлена
- ✅ CHANGELOG.md обновлен

**Комментарии:**
```
# Запросить изменения
"Пожалуйста, добавьте docstrings к методам"

# Одобрить
"LGTM! 🚀" (Looks Good To Me)
```

### 5️⃣ Merge в develop

После одобрения:
```bash
# Squash and merge (рекомендуется)
# Все коммиты объединяются в один

# Или Merge commit
# Сохраняет всю историю коммитов
```

### 6️⃣ Релиз (develop → main)

```bash
# Когда develop готов к релизу
git checkout main
git pull origin main
git merge develop
git tag -a v1.4.0 -m "Release v1.4.0: Export Project"
git push origin main --tags
```

## 📝 Соглашения о коммитах

### Формат коммита

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Типы коммитов

- `feat:` — новая функция
- `fix:` — исправление бага
- `docs:` — изменения в документации
- `style:` — форматирование, отступы (не CSS)
- `refactor:` — рефакторинг кода
- `test:` — добавление тестов
- `chore:` — обновление зависимостей, конфигурации

### Примеры

```bash
# Хорошо ✅
git commit -m "feat(export): add project export dialog"
git commit -m "fix(ui): remove duplicate arrow heads"
git commit -m "docs: update README with export feature"
git commit -m "test(export): add unit tests for ProjectExporter"

# Плохо ❌
git commit -m "update"
git commit -m "fix bug"
git commit -m "changes"
```

### Детальный коммит

```bash
git commit -m "feat(export): add project structure export

- Created ProjectExportDialog with 4 tabs
- Implemented preview with real-time updates
- Added support for 5 languages and 4 architectures
- Generated config files (requirements.txt, pom.xml, etc.)

Closes #42"
```

## 🛡️ Защита веток

### Настройка на GitHub

**Settings → Branches → Branch protection rules**

#### Для `main`:
- ✅ Require pull request reviews (минимум 1)
- ✅ Require status checks to pass (тесты)
- ✅ Require branches to be up to date
- ✅ Include administrators
- ✅ Restrict who can push (никто)

#### Для `develop`:
- ✅ Require pull request reviews (опционально)
- ✅ Require status checks to pass
- ✅ Allow force pushes (для rebase)

## 🔄 Синхронизация с develop

### Регулярное обновление feature-ветки

```bash
# Находясь в feature/my-feature
git checkout develop
git pull origin develop

git checkout feature/my-feature
git rebase develop
# Или
git merge develop

git push origin feature/my-feature --force-with-lease
```

### Разрешение конфликтов

```bash
# При rebase/merge возникли конфликты
git status  # Посмотреть конфликтующие файлы

# Открыть файл, найти:
<<<<<<< HEAD
ваш код
=======
чужой код
>>>>>>> develop

# Исправить вручную, оставить нужное

git add .
git rebase --continue
# Или
git merge --continue
```

## 👥 Распределение ответственности

### Саша (Architect)
- **Ревью всех PR** перед merge в `main`
- Управление релизами
- Разрешение конфликтов архитектуры
- Ветки: `feature/architecture-*`, `refactor/*`

### Даша (Frontend)
- Ревью UI/UX изменений
- Ветки: `feature/ui-*`, `feature/dialog-*`
- Стили, темы, виджеты

### Семён (Backend)
- Ревью моделей и бизнес-логики
- Ветки: `feature/model-*`, `feature/service-*`
- Генерация кода, валидация

### Перекрестное ревью
- Каждый PR должен быть проверен **минимум одним** другим членом команды
- Желательно — двумя (один технический, один функциональный)

## 🤖 Автоматизация (CI/CD)

### GitHub Actions

Создать `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  pull_request:
    branches: [develop, main]
  push:
    branches: [develop, main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          pip install poetry
          poetry install
      
      - name: Run tests
        run: poetry run pytest
      
      - name: Check code style
        run: |
          poetry run black --check .
          poetry run flake8 .
      
      - name: Type checking
        run: poetry run mypy src/

  build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      
      - name: Build package
        run: poetry build
```

### Pre-commit hooks

Создать `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.13

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

Установка:
```bash
pip install pre-commit
pre-commit install
```

## 📊 Метрики качества

### Чеклист перед merge

- [ ] Все тесты проходят
- [ ] Code coverage не упал
- [ ] Нет конфликтов с develop
- [ ] Документация обновлена
- [ ] CHANGELOG.md обновлен
- [ ] Код прошел ревью
- [ ] Нет TODO/FIXME в коде
- [ ] Commit messages осмысленные

## 🎯 Быстрый старт для команды

### Первоначальная настройка

```bash
# 1. Клонировать репозиторий
git clone https://github.com/yourusername/logiccraft.git
cd logiccraft

# 2. Создать ветку develop (если нет)
git checkout -b develop
git push origin develop

# 3. Настроить Git
git config user.name "Ваше Имя"
git config user.email "your@email.com"

# 4. Установить pre-commit
pip install pre-commit
pre-commit install
```

### Ежедневная работа

```bash
# Утро: обновить develop
git checkout develop
git pull origin develop

# Создать ветку для задачи
git checkout -b feature/my-task

# Работа...
git add .
git commit -m "feat: implement feature"

# Вечер: запушить
git push origin feature/my-task

# Создать PR на GitHub
```

## 📚 Дополнительные ресурсы

- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Semantic Versioning](https://semver.org/)

## 🆘 Частые проблемы

### "Я случайно закоммитил в main"

```bash
# Откатить последний коммит (не потеряв изменения)
git reset --soft HEAD~1

# Создать правильную ветку
git checkout -b feature/my-feature

# Закоммитить снова
git commit -m "feat: my feature"
```

### "У меня конфликты при merge"

```bash
# Обновить develop
git checkout develop
git pull origin develop

# Вернуться в свою ветку
git checkout feature/my-feature

# Rebase на develop
git rebase develop

# Разрешить конфликты вручную
# После каждого файла:
git add <file>
git rebase --continue
```

### "Я хочу отменить последний коммит"

```bash
# Отменить коммит, сохранив изменения
git reset --soft HEAD~1

# Отменить коммит и изменения (ОПАСНО!)
git reset --hard HEAD~1
```

---

**Следуя этому workflow, команда LogicCraft будет работать эффективнее и безопаснее!** 🚀
