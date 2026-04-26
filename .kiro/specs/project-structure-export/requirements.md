# Requirements Document

## Introduction

Расширение системы экспорта LogicCraft для создания полноценных структур проектов с правильной организацией папок, конфигурационными файлами и настройками генерации кода для каждого поддерживаемого языка программирования.

## Glossary

- **Project_Exporter**: Система экспорта проектов LogicCraft
- **Structure_Template**: Шаблон организации папок для конкретного языка/фреймворка
- **Generation_Settings**: Настройки генерации кода (стили, соглашения именования)
- **Config_Generator**: Компонент создания конфигурационных файлов проекта
- **UML_Diagram**: Диаграмма классов UML в LogicCraft
- **Export_Dialog**: Диалоговое окно настройки экспорта проекта
- **Project_Structure**: Полная структура папок и файлов проекта

## Requirements

### Requirement 1: Диалог настройки экспорта проекта

**User Story:** Как пользователь LogicCraft, я хочу настроить параметры экспорта проекта через удобный интерфейс, чтобы получить структуру проекта, соответствующую моим требованиям.

#### Acceptance Criteria

1. WHEN пользователь выбирает "Экспорт проекта" в меню, THE Export_Dialog SHALL отобразить окно настройки экспорта
2. THE Export_Dialog SHALL предоставить выбор языка программирования из поддерживаемых (Python, Java, JavaScript, TypeScript, C#)
3. THE Export_Dialog SHALL предоставить выбор типа структуры проекта (Simple, MVC, Layered Architecture, Clean Architecture)
4. THE Export_Dialog SHALL предоставить настройки включения дополнительных компонентов (тесты, документация, конфигурационные файлы)
5. THE Export_Dialog SHALL предоставить выбор пакетного менеджера для каждого языка (pip/poetry для Python, npm/yarn для JS/TS, Maven/Gradle для Java, NuGet для C#)
6. THE Export_Dialog SHALL предоставить поля для метаданных проекта (название, автор, описание, версия)

### Requirement 2: Генерация структуры папок

**User Story:** Как пользователь, я хочу получить правильно организованную структуру папок для выбранного языка и архитектуры, чтобы мой проект соответствовал принятым стандартам.

#### Acceptance Criteria

1. WHEN пользователь выбирает Python и Simple структуру, THE Project_Exporter SHALL создать структуру с основным пакетом и модулями
2. WHEN пользователь выбирает Python и MVC структуру, THE Project_Exporter SHALL создать папки models, views, controllers с соответствующими __init__.py файлами
3. WHEN пользователь выбирает Java проект, THE Project_Exporter SHALL создать стандартную Maven структуру src/main/java с пакетами
4. WHEN пользователь выбирает JavaScript/TypeScript проект, THE Project_Exporter SHALL создать структуру с папками src, tests, и корневыми конфигурационными файлами
5. WHEN пользователь выбирает C# проект, THE Project_Exporter SHALL создать структуру .NET проекта с .sln и .csproj файлами
6. THE Project_Exporter SHALL размещать сгенерированные классы в соответствующих папках согласно выбранной архитектуре

### Requirement 3: Создание конфигурационных файлов

**User Story:** Как разработчик, я хочу получить готовые конфигурационные файлы для моего проекта, чтобы сразу начать разработку без дополнительной настройки.

#### Acceptance Criteria

1. WHEN экспортируется Python проект, THE Config_Generator SHALL создать requirements.txt с базовыми зависимостями
2. WHEN экспортируется Python проект с Poetry, THE Config_Generator SHALL создать pyproject.toml файл
3. WHEN экспортируется Java проект, THE Config_Generator SHALL создать pom.xml с корректными метаданными проекта
4. WHEN экспортируется JavaScript/TypeScript проект, THE Config_Generator SHALL создать package.json с соответствующими зависимостями
5. WHEN экспортируется TypeScript проект, THE Config_Generator SHALL создать tsconfig.json с рекомендуемыми настройками
6. WHEN экспортируется C# проект, THE Config_Generator SHALL создать .csproj файл с правильными настройками .NET
7. THE Config_Generator SHALL включать метаданные проекта (название, автор, версия, описание) в конфигурационные файлы

### Requirement 4: Настройки генерации кода

**User Story:** Как пользователь, я хочу настроить стиль генерируемого кода, чтобы он соответствовал стандартам моей команды или проекта.

#### Acceptance Criteria

1. THE Generation_Settings SHALL предоставить выбор соглашений именования (camelCase, snake_case, PascalCase) для каждого элемента
2. THE Generation_Settings SHALL предоставить настройку размера отступов (2 пробела, 4 пробела, табы)
3. THE Generation_Settings SHALL предоставить опции включения/исключения элементов (конструкторы, геттеры/сеттеры, документация)
4. WHEN пользователь выбирает Python, THE Generation_Settings SHALL применить snake_case для методов и атрибутов
5. WHEN пользователь выбирает Java/C#, THE Generation_Settings SHALL применить camelCase для методов и PascalCase для классов
6. THE Generation_Settings SHALL сохранять пользовательские настройки для повторного использования

### Requirement 5: Создание дополнительных файлов проекта

**User Story:** Как пользователь, я хочу получить дополнительные файлы проекта (README, .gitignore, тесты), чтобы иметь полноценную структуру для разработки.

#### Acceptance Criteria

1. WHEN включена опция документации, THE Project_Exporter SHALL создать README.md с описанием проекта и инструкциями по установке
2. THE Project_Exporter SHALL создать .gitignore файл с правилами для выбранного языка программирования
3. WHEN включена опция тестов, THE Project_Exporter SHALL создать базовые тестовые файлы с примерами тестов для сгенерированных классов
4. WHEN включена опция документации, THE Project_Exporter SHALL создать папку docs с базовой структурой документации
5. THE Project_Exporter SHALL создать файл лицензии при выборе соответствующей опции
6. THE Project_Exporter SHALL создать файлы CI/CD конфигурации при выборе соответствующей опции (GitHub Actions, GitLab CI)

### Requirement 6: Интеграция с существующей системой генерации

**User Story:** Как пользователь, я хочу использовать расширенный экспорт совместно с существующей системой генерации кода, чтобы получить полноценный проект из моей UML диаграммы.

#### Acceptance Criteria

1. THE Project_Exporter SHALL использовать существующий Code_Generator для создания файлов классов
2. THE Project_Exporter SHALL размещать сгенерированные классы в соответствующих папках структуры проекта
3. THE Project_Exporter SHALL применять настройки стиля кода ко всем генерируемым файлам
4. THE Project_Exporter SHALL сохранять связи между классами при размещении в разных модулях/пакетах
5. THE Project_Exporter SHALL генерировать корректные импорты между модулями в зависимости от структуры проекта
6. THE Project_Exporter SHALL поддерживать все существующие типы UML элементов (классы, интерфейсы, абстрактные классы)

### Requirement 7: Валидация и обработка ошибок

**User Story:** Как пользователь, я хочу получать понятные сообщения об ошибках и предупреждения, чтобы успешно экспортировать проект.

#### Acceptance Criteria

1. WHEN название проекта содержит недопустимые символы, THE Export_Dialog SHALL отобразить предупреждение и предложить исправление
2. WHEN выбранная папка экспорта недоступна для записи, THE Project_Exporter SHALL отобразить ошибку с предложением выбрать другую папку
3. WHEN в диаграмме нет классов, THE Project_Exporter SHALL отобразить предупреждение и предложить создать базовую структуру
4. IF экспорт прерван из-за ошибки, THEN THE Project_Exporter SHALL очистить частично созданные файлы
5. THE Project_Exporter SHALL проверять корректность метаданных проекта перед началом экспорта
6. THE Project_Exporter SHALL отображать прогресс экспорта с возможностью отмены операции

### Requirement 8: Шаблоны проектов

**User Story:** Как пользователь, я хочу использовать готовые шаблоны проектов для популярных фреймворков, чтобы быстро начать разработку с правильной структурой.

#### Acceptance Criteria

1. THE Structure_Template SHALL предоставить шаблон Django проекта для Python
2. THE Structure_Template SHALL предоставить шаблон Spring Boot проекта для Java
3. THE Structure_Template SHALL предоставить шаблон Express.js проекта для JavaScript/TypeScript
4. THE Structure_Template SHALL предоставить шаблон React проекта для JavaScript/TypeScript
5. THE Structure_Template SHALL предоставить шаблон ASP.NET Core проекта для C#
6. WHEN пользователь выбирает шаблон фреймворка, THE Project_Exporter SHALL включить соответствующие зависимости и конфигурационные файлы
7. THE Structure_Template SHALL поддерживать кастомные пользовательские шаблоны

### Requirement 9: Предпросмотр структуры проекта

**User Story:** Как пользователь, я хочу видеть предпросмотр структуры проекта перед экспортом, чтобы убедиться в правильности настроек.

#### Acceptance Criteria

1. THE Export_Dialog SHALL отображать дерево файлов и папок, которые будут созданы
2. THE Export_Dialog SHALL показывать количество файлов, которые будут созданы
3. THE Export_Dialog SHALL позволять просматривать содержимое ключевых файлов (package.json, requirements.txt)
4. WHEN пользователь изменяет настройки, THE Export_Dialog SHALL обновлять предпросмотр в реальном времени
5. THE Export_Dialog SHALL выделять файлы, которые будут перезаписаны при экспорте в существующую папку
6. THE Export_Dialog SHALL отображать размер проекта и количество строк кода

### Requirement 10: Сохранение и загрузка профилей экспорта

**User Story:** Как пользователь, я хочу сохранять и загружать профили настроек экспорта, чтобы повторно использовать одинаковые конфигурации для разных проектов.

#### Acceptance Criteria

1. THE Export_Dialog SHALL предоставить возможность сохранения текущих настроек как профиль
2. THE Export_Dialog SHALL предоставить возможность загрузки сохраненного профиля
3. THE Export_Dialog SHALL предоставить список доступных профилей с возможностью удаления
4. THE Export_Dialog SHALL включать в профиль все настройки генерации и структуры проекта
5. THE Export_Dialog SHALL предоставить профили по умолчанию для популярных конфигураций
6. THE Export_Dialog SHALL валидировать совместимость загружаемого профиля с текущей версией LogicCraft