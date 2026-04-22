"""Модели шаблонов структуры проектов"""

import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime


@dataclass
class StructureTemplate:
    """Шаблон структуры проекта"""
    name: str
    language: str
    framework: Optional[str]
    description: str
    structure: Dict[str, Any]  # Дерево файлов и папок
    dependencies: List[str] = field(default_factory=list)
    dev_dependencies: List[str] = field(default_factory=list)
    scripts: Dict[str, str] = field(default_factory=dict)
    is_custom: bool = False

    def __post_init__(self):
        """Пост-инициализация для валидации"""
        if not self.name or not self.name.strip():
            raise ValueError("Template name cannot be empty")
        if not self.language or not self.language.strip():
            raise ValueError("Template language cannot be empty")
        if not isinstance(self.structure, dict):
            raise ValueError("Template structure must be a dictionary")

    def validate(self) -> List[str]:
        """Валидация шаблона"""
        errors = []
        
        # Валидация имени
        if not self.name or not self.name.strip():
            errors.append("Template name cannot be empty")
        elif len(self.name) > 100:
            errors.append("Template name cannot exceed 100 characters")
            
        # Валидация языка
        supported_languages = {"python", "java", "javascript", "typescript", "csharp"}
        if self.language not in supported_languages:
            errors.append(f"Unsupported language: {self.language}")
            
        # Валидация фреймворка
        if self.framework:
            valid_frameworks = self._get_valid_frameworks_for_language()
            if self.framework not in valid_frameworks:
                errors.append(f"Framework '{self.framework}' is not supported for {self.language}")
                
        # Валидация структуры
        if not isinstance(self.structure, dict):
            errors.append("Structure must be a dictionary")
        elif not self.structure:
            errors.append("Structure cannot be empty")
        else:
            structure_errors = self._validate_structure(self.structure)
            errors.extend(structure_errors)
            
        # Валидация зависимостей
        if not isinstance(self.dependencies, list):
            errors.append("Dependencies must be a list")
        if not isinstance(self.dev_dependencies, list):
            errors.append("Dev dependencies must be a list")
            
        # Валидация скриптов
        if not isinstance(self.scripts, dict):
            errors.append("Scripts must be a dictionary")
            
        return errors

    def _get_valid_frameworks_for_language(self) -> List[str]:
        """Получение списка поддерживаемых фреймворков для языка"""
        frameworks = {
            "python": ["django", "flask", "fastapi"],
            "java": ["spring", "spring-boot"],
            "javascript": ["express", "react", "vue", "angular"],
            "typescript": ["express", "react", "vue", "angular", "nest"],
            "csharp": ["aspnet-core", "blazor"]
        }
        return frameworks.get(self.language, [])

    def _validate_structure(self, structure: Dict[str, Any], path: str = "") -> List[str]:
        """Рекурсивная валидация структуры"""
        errors = []
        
        for name, content in structure.items():
            current_path = f"{path}/{name}" if path else name
            
            # Валидация имени файла/папки
            if not name or not isinstance(name, str):
                errors.append(f"Invalid name at {current_path}")
                continue
                
            # Проверка недопустимых символов в именах
            invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
            if any(char in name for char in invalid_chars):
                errors.append(f"Invalid characters in name: {current_path}")
                
            # Если это папка (словарь), рекурсивно проверяем содержимое
            if isinstance(content, dict):
                sub_errors = self._validate_structure(content, current_path)
                errors.extend(sub_errors)
            # Если это файл (строка или None), проверяем содержимое
            elif content is not None and not isinstance(content, str):
                errors.append(f"File content must be string or None at {current_path}")
                
        return errors

    def get_file_count(self) -> int:
        """Подсчет количества файлов в структуре"""
        return self._count_files(self.structure)

    def _count_files(self, structure: Dict[str, Any]) -> int:
        """Рекурсивный подсчет файлов"""
        count = 0
        for name, content in structure.items():
            if isinstance(content, dict):
                count += self._count_files(content)
            else:
                count += 1
        return count

    def get_directory_count(self) -> int:
        """Подсчет количества директорий в структуре"""
        return self._count_directories(self.structure)

    def _count_directories(self, structure: Dict[str, Any]) -> int:
        """Рекурсивный подсчет директорий"""
        count = 0
        for name, content in structure.items():
            if isinstance(content, dict):
                count += 1 + self._count_directories(content)
        return count

    def get_all_files(self) -> List[str]:
        """Получение списка всех файлов в структуре"""
        files = []
        self._collect_files(self.structure, "", files)
        return files

    def _collect_files(self, structure: Dict[str, Any], path: str, files: List[str]):
        """Рекурсивный сбор путей файлов"""
        for name, content in structure.items():
            current_path = f"{path}/{name}" if path else name
            if isinstance(content, dict):
                self._collect_files(content, current_path, files)
            else:
                files.append(current_path)

    def get_all_directories(self) -> List[str]:
        """Получение списка всех директорий в структуре"""
        directories = []
        self._collect_directories(self.structure, "", directories)
        return directories

    def _collect_directories(self, structure: Dict[str, Any], path: str, directories: List[str]):
        """Рекурсивный сбор путей директорий"""
        for name, content in structure.items():
            current_path = f"{path}/{name}" if path else name
            if isinstance(content, dict):
                directories.append(current_path)
                self._collect_directories(content, current_path, directories)

    def has_file(self, file_path: str) -> bool:
        """Проверка наличия файла в структуре"""
        return file_path in self.get_all_files()

    def has_directory(self, dir_path: str) -> bool:
        """Проверка наличия директории в структуре"""
        return dir_path in self.get_all_directories()

    def get_file_content(self, file_path: str) -> Optional[str]:
        """Получение содержимого файла по пути"""
        parts = file_path.split('/')
        current = self.structure
        
        for part in parts[:-1]:
            if part in current and isinstance(current[part], dict):
                current = current[part]
            else:
                return None
                
        file_name = parts[-1]
        if file_name in current and not isinstance(current[file_name], dict):
            return current[file_name]
        return None

    def set_file_content(self, file_path: str, content: str):
        """Установка содержимого файла по пути"""
        parts = file_path.split('/')
        current = self.structure
        
        # Создаем промежуточные директории если нужно
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                raise ValueError(f"Cannot create directory {part}: file exists")
            current = current[part]
            
        file_name = parts[-1]
        current[file_name] = content

    def add_dependency(self, dependency: str, is_dev: bool = False):
        """Добавление зависимости"""
        if is_dev:
            if dependency not in self.dev_dependencies:
                self.dev_dependencies.append(dependency)
        else:
            if dependency not in self.dependencies:
                self.dependencies.append(dependency)

    def remove_dependency(self, dependency: str):
        """Удаление зависимости"""
        if dependency in self.dependencies:
            self.dependencies.remove(dependency)
        if dependency in self.dev_dependencies:
            self.dev_dependencies.remove(dependency)

    def add_script(self, name: str, command: str):
        """Добавление скрипта"""
        self.scripts[name] = command

    def remove_script(self, name: str):
        """Удаление скрипта"""
        if name in self.scripts:
            del self.scripts[name]

    def to_dict(self) -> Dict[str, Any]:
        """Сериализация в словарь"""
        data = asdict(self)
        # Добавляем метаданные
        data["_template_version"] = "1.0"
        data["_created_at"] = datetime.now().isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StructureTemplate':
        """Десериализация из словаря"""
        # Удаляем метаданные
        clean_data = {k: v for k, v in data.items() if not k.startswith('_')}
        return cls(**clean_data)

    def to_json(self) -> str:
        """Сериализация в JSON"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> 'StructureTemplate':
        """Десериализация из JSON"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def save_to_file(self, file_path: str):
        """Сохранение шаблона в файл"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())

    @classmethod
    def load_from_file(cls, file_path: str) -> 'StructureTemplate':
        """Загрузка шаблона из файла"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return cls.from_json(f.read())

    def clone(self) -> 'StructureTemplate':
        """Создание копии шаблона"""
        return StructureTemplate.from_dict(self.to_dict())

    def merge_with(self, other: 'StructureTemplate') -> 'StructureTemplate':
        """Слияние с другим шаблоном"""
        if self.language != other.language:
            raise ValueError("Cannot merge templates with different languages")
            
        merged = self.clone()
        
        # Объединяем структуры
        merged.structure = self._merge_structures(self.structure, other.structure)
        
        # Объединяем зависимости
        merged.dependencies = list(set(self.dependencies + other.dependencies))
        merged.dev_dependencies = list(set(self.dev_dependencies + other.dev_dependencies))
        
        # Объединяем скрипты (приоритет у other)
        merged.scripts = {**self.scripts, **other.scripts}
        
        # Обновляем метаданные
        merged.name = f"{self.name}_merged_{other.name}"
        merged.description = f"Merged template: {self.description} + {other.description}"
        merged.is_custom = True
        
        return merged

    def _merge_structures(self, struct1: Dict[str, Any], struct2: Dict[str, Any]) -> Dict[str, Any]:
        """Рекурсивное слияние структур"""
        result = struct1.copy()
        
        for key, value in struct2.items():
            if key in result:
                if isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self._merge_structures(result[key], value)
                else:
                    # Приоритет у второй структуры
                    result[key] = value
            else:
                result[key] = value
                
        return result

    @classmethod
    def create_builtin_templates(cls) -> Dict[str, 'StructureTemplate']:
        """Создание встроенных шаблонов"""
        templates = {}
        
        # Django шаблон
        templates["django"] = cls(
            name="Django Project",
            language="python",
            framework="django",
            description="Standard Django web application structure with REST API support",
            structure={
                "manage.py": "#!/usr/bin/env python\nimport os\nimport sys\n\nif __name__ == '__main__':\n    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')\n    try:\n        from django.core.management import execute_from_command_line\n    except ImportError as exc:\n        raise ImportError(\n            \"Couldn't import Django. Are you sure it's installed and \"\n            \"available on your PYTHONPATH environment variable? Did you \"\n            \"forget to activate a virtual environment?\"\n        ) from exc\n    execute_from_command_line(sys.argv)",
                "requirements.txt": "Django>=4.2.0\ndjango-rest-framework>=3.14.0\ndjango-cors-headers>=4.0.0\npsycopg2-binary>=2.9.0\ncelery>=5.3.0\nredis>=4.5.0\nPillow>=10.0.0",
                "myproject": {
                    "__init__.py": "",
                    "settings.py": "from pathlib import Path\nimport os\n\nBASE_DIR = Path(__file__).resolve().parent.parent\n\nSECRET_KEY = 'your-secret-key-here'\nDEBUG = True\nALLOWED_HOSTS = []\n\nINSTALLED_APPS = [\n    'django.contrib.admin',\n    'django.contrib.auth',\n    'django.contrib.contenttypes',\n    'django.contrib.sessions',\n    'django.contrib.messages',\n    'django.contrib.staticfiles',\n    'rest_framework',\n    'corsheaders',\n    'apps.core',\n]\n\nMIDDLEWARE = [\n    'corsheaders.middleware.CorsMiddleware',\n    'django.middleware.security.SecurityMiddleware',\n    'django.contrib.sessions.middleware.SessionMiddleware',\n    'django.middleware.common.CommonMiddleware',\n    'django.middleware.csrf.CsrfViewMiddleware',\n    'django.contrib.auth.middleware.AuthenticationMiddleware',\n    'django.contrib.messages.middleware.MessageMiddleware',\n    'django.middleware.clickjacking.XFrameOptionsMiddleware',\n]\n\nROOT_URLCONF = 'myproject.urls'\n\nDATABASES = {\n    'default': {\n        'ENGINE': 'django.db.backends.sqlite3',\n        'NAME': BASE_DIR / 'db.sqlite3',\n    }\n}\n\nSTATIC_URL = '/static/'\nSTATIC_ROOT = BASE_DIR / 'staticfiles'\nMEDIA_URL = '/media/'\nMEDIA_ROOT = BASE_DIR / 'media'",
                    "urls.py": "from django.contrib import admin\nfrom django.urls import path, include\nfrom django.conf import settings\nfrom django.conf.urls.static import static\n\nurlpatterns = [\n    path('admin/', admin.site.urls),\n    path('api/', include('apps.core.urls')),\n]\n\nif settings.DEBUG:\n    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)",
                    "wsgi.py": "import os\nfrom django.core.wsgi import get_wsgi_application\n\nos.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')\napplication = get_wsgi_application()",
                    "asgi.py": "import os\nfrom django.core.asgi import get_asgi_application\n\nos.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')\napplication = get_asgi_application()"
                },
                "apps": {
                    "__init__.py": "",
                    "core": {
                        "__init__.py": "",
                        "models.py": "from django.db import models\nfrom django.contrib.auth.models import User\n\nclass BaseModel(models.Model):\n    created_at = models.DateTimeField(auto_now_add=True)\n    updated_at = models.DateTimeField(auto_now=True)\n    \n    class Meta:\n        abstract = True",
                        "views.py": "from rest_framework import viewsets, status\nfrom rest_framework.decorators import api_view\nfrom rest_framework.response import Response\n\n@api_view(['GET'])\ndef health_check(request):\n    return Response({'status': 'healthy'}, status=status.HTTP_200_OK)",
                        "urls.py": "from django.urls import path, include\nfrom rest_framework.routers import DefaultRouter\nfrom . import views\n\nrouter = DefaultRouter()\n\nurlpatterns = [\n    path('', include(router.urls)),\n    path('health/', views.health_check, name='health_check'),\n]",
                        "admin.py": "from django.contrib import admin\n\n# Register your models here.",
                        "apps.py": "from django.apps import AppConfig\n\nclass CoreConfig(AppConfig):\n    default_auto_field = 'django.db.models.BigAutoField'\n    name = 'apps.core'",
                        "serializers.py": "from rest_framework import serializers\n\n# Add your serializers here"
                    }
                },
                "static": {
                    "css": {
                        "main.css": "/* Main stylesheet */"
                    },
                    "js": {
                        "main.js": "// Main JavaScript file"
                    },
                    "images": {}
                },
                "templates": {
                    "base.html": "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n    <meta charset=\"UTF-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n    <title>{% block title %}Django Project{% endblock %}</title>\n    {% load static %}\n    <link rel=\"stylesheet\" href=\"{% static 'css/main.css' %}\">\n</head>\n<body>\n    {% block content %}\n    {% endblock %}\n    <script src=\"{% static 'js/main.js' %}\"></script>\n</body>\n</html>"
                },
                "tests": {
                    "__init__.py": "",
                    "test_models.py": "from django.test import TestCase\nfrom apps.core.models import BaseModel\n\nclass BaseModelTest(TestCase):\n    def test_base_model_creation(self):\n        # Add your model tests here\n        pass",
                    "test_views.py": "from django.test import TestCase\nfrom django.urls import reverse\nfrom rest_framework.test import APIClient\nfrom rest_framework import status\n\nclass ViewsTest(TestCase):\n    def setUp(self):\n        self.client = APIClient()\n    \n    def test_health_check(self):\n        url = reverse('health_check')\n        response = self.client.get(url)\n        self.assertEqual(response.status_code, status.HTTP_200_OK)\n        self.assertEqual(response.data['status'], 'healthy')"
                },
                ".gitignore": "# Django\n*.log\n*.pot\n*.pyc\n__pycache__/\nlocal_settings.py\ndb.sqlite3\ndb.sqlite3-journal\nmedia/\nstaticfiles/\n\n# Virtual Environment\nvenv/\nenv/\n.env\n\n# IDE\n.vscode/\n.idea/\n*.swp\n*.swo\n\n# OS\n.DS_Store\nThumbs.db",
                "README.md": "# Django Project\n\n## Setup\n\n1. Create virtual environment:\n```bash\npython -m venv venv\nsource venv/bin/activate  # On Windows: venv\\Scripts\\activate\n```\n\n2. Install dependencies:\n```bash\npip install -r requirements.txt\n```\n\n3. Run migrations:\n```bash\npython manage.py migrate\n```\n\n4. Create superuser:\n```bash\npython manage.py createsuperuser\n```\n\n5. Run development server:\n```bash\npython manage.py runserver\n```\n\n## API Endpoints\n\n- Health Check: `GET /api/health/`\n- Admin Panel: `/admin/`\n\n## Testing\n\n```bash\npython manage.py test\n```"
            },
            dependencies=["Django>=4.2.0", "django-rest-framework>=3.14.0", "django-cors-headers>=4.0.0", "psycopg2-binary>=2.9.0", "celery>=5.3.0", "redis>=4.5.0", "Pillow>=10.0.0"],
            dev_dependencies=["pytest-django>=4.5.0", "black>=23.0.0", "flake8>=6.0.0", "coverage>=7.0.0"],
            scripts={
                "runserver": "python manage.py runserver",
                "migrate": "python manage.py migrate",
                "makemigrations": "python manage.py makemigrations",
                "test": "python manage.py test",
                "collectstatic": "python manage.py collectstatic --noinput",
                "createsuperuser": "python manage.py createsuperuser"
            }
        )
        
        # Spring Boot шаблон
        templates["spring-boot"] = cls(
            name="Spring Boot Project",
            language="java",
            framework="spring-boot",
            description="Standard Spring Boot REST API application structure",
            structure={
                "pom.xml": """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
        <relativePath/>
    </parent>
    
    <groupId>com.example</groupId>
    <artifactId>demo</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>demo</name>
    <description>Demo project for Spring Boot</description>
    
    <properties>
        <java.version>17</java.version>
    </properties>
    
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>""",
                "src": {
                    "main": {
                        "java": {
                            "com": {
                                "example": {
                                    "demo": {
                                        "DemoApplication.java": "package com.example.demo;\n\nimport org.springframework.boot.SpringApplication;\nimport org.springframework.boot.autoconfigure.SpringBootApplication;\n\n@SpringBootApplication\npublic class DemoApplication {\n    public static void main(String[] args) {\n        SpringApplication.run(DemoApplication.class, args);\n    }\n}",
                                        "controller": {
                                            "HomeController.java": "package com.example.demo.controller;\n\nimport org.springframework.web.bind.annotation.*;\nimport org.springframework.http.ResponseEntity;\n\n@RestController\n@RequestMapping(\"/api\")\npublic class HomeController {\n    \n    @GetMapping(\"/health\")\n    public ResponseEntity<String> health() {\n        return ResponseEntity.ok(\"Application is running\");\n    }\n}",
                                            "UserController.java": "package com.example.demo.controller;\n\nimport com.example.demo.model.User;\nimport com.example.demo.service.UserService;\nimport org.springframework.beans.factory.annotation.Autowired;\nimport org.springframework.http.ResponseEntity;\nimport org.springframework.web.bind.annotation.*;\n\nimport java.util.List;\n\n@RestController\n@RequestMapping(\"/api/users\")\npublic class UserController {\n    \n    @Autowired\n    private UserService userService;\n    \n    @GetMapping\n    public List<User> getAllUsers() {\n        return userService.findAll();\n    }\n    \n    @GetMapping(\"/{id}\")\n    public ResponseEntity<User> getUserById(@PathVariable Long id) {\n        User user = userService.findById(id);\n        return user != null ? ResponseEntity.ok(user) : ResponseEntity.notFound().build();\n    }\n    \n    @PostMapping\n    public User createUser(@RequestBody User user) {\n        return userService.save(user);\n    }\n}"
                                        },
                                        "service": {
                                            "UserService.java": "package com.example.demo.service;\n\nimport com.example.demo.model.User;\nimport com.example.demo.repository.UserRepository;\nimport org.springframework.beans.factory.annotation.Autowired;\nimport org.springframework.stereotype.Service;\n\nimport java.util.List;\n\n@Service\npublic class UserService {\n    \n    @Autowired\n    private UserRepository userRepository;\n    \n    public List<User> findAll() {\n        return userRepository.findAll();\n    }\n    \n    public User findById(Long id) {\n        return userRepository.findById(id).orElse(null);\n    }\n    \n    public User save(User user) {\n        return userRepository.save(user);\n    }\n}"
                                        },
                                        "model": {
                                            "User.java": "package com.example.demo.model;\n\nimport jakarta.persistence.*;\nimport jakarta.validation.constraints.Email;\nimport jakarta.validation.constraints.NotBlank;\n\n@Entity\n@Table(name = \"users\")\npublic class User {\n    \n    @Id\n    @GeneratedValue(strategy = GenerationType.IDENTITY)\n    private Long id;\n    \n    @NotBlank(message = \"Name is required\")\n    @Column(nullable = false)\n    private String name;\n    \n    @Email(message = \"Email should be valid\")\n    @Column(unique = true, nullable = false)\n    private String email;\n    \n    // Constructors\n    public User() {}\n    \n    public User(String name, String email) {\n        this.name = name;\n        this.email = email;\n    }\n    \n    // Getters and Setters\n    public Long getId() { return id; }\n    public void setId(Long id) { this.id = id; }\n    \n    public String getName() { return name; }\n    public void setName(String name) { this.name = name; }\n    \n    public String getEmail() { return email; }\n    public void setEmail(String email) { this.email = email; }\n}"
                                        },
                                        "repository": {
                                            "UserRepository.java": "package com.example.demo.repository;\n\nimport com.example.demo.model.User;\nimport org.springframework.data.jpa.repository.JpaRepository;\nimport org.springframework.stereotype.Repository;\n\n@Repository\npublic interface UserRepository extends JpaRepository<User, Long> {\n    User findByEmail(String email);\n}"
                                        }
                                    }
                                }
                            }
                        },
                        "resources": {
                            "application.properties": "# Database Configuration\nspring.datasource.url=jdbc:h2:mem:testdb\nspring.datasource.driverClassName=org.h2.Driver\nspring.datasource.username=sa\nspring.datasource.password=password\n\n# JPA Configuration\nspring.jpa.database-platform=org.hibernate.dialect.H2Dialect\nspring.jpa.hibernate.ddl-auto=update\nspring.jpa.show-sql=true\n\n# H2 Console (for development)\nspring.h2.console.enabled=true\nspring.h2.console.path=/h2-console\n\n# Server Configuration\nserver.port=8080\n\n# Logging\nlogging.level.com.example.demo=DEBUG",
                            "application-prod.properties": "# Production Configuration\nspring.datasource.url=jdbc:postgresql://localhost:5432/demo\nspring.datasource.username=${DB_USERNAME}\nspring.datasource.password=${DB_PASSWORD}\nspring.jpa.hibernate.ddl-auto=validate\nspring.jpa.show-sql=false\nlogging.level.com.example.demo=INFO",
                            "static": {},
                            "templates": {}
                        }
                    },
                    "test": {
                        "java": {
                            "com": {
                                "example": {
                                    "demo": {
                                        "DemoApplicationTests.java": "package com.example.demo;\n\nimport org.junit.jupiter.api.Test;\nimport org.springframework.boot.test.context.SpringBootTest;\n\n@SpringBootTest\nclass DemoApplicationTests {\n    \n    @Test\n    void contextLoads() {\n    }\n}",
                                        "controller": {
                                            "UserControllerTest.java": "package com.example.demo.controller;\n\nimport com.example.demo.model.User;\nimport com.example.demo.service.UserService;\nimport com.fasterxml.jackson.databind.ObjectMapper;\nimport org.junit.jupiter.api.Test;\nimport org.springframework.beans.factory.annotation.Autowired;\nimport org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;\nimport org.springframework.boot.test.mock.mockito.MockBean;\nimport org.springframework.http.MediaType;\nimport org.springframework.test.web.servlet.MockMvc;\n\nimport java.util.Arrays;\n\nimport static org.mockito.Mockito.when;\nimport static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;\nimport static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;\n\n@WebMvcTest(UserController.class)\nclass UserControllerTest {\n    \n    @Autowired\n    private MockMvc mockMvc;\n    \n    @MockBean\n    private UserService userService;\n    \n    @Autowired\n    private ObjectMapper objectMapper;\n    \n    @Test\n    void getAllUsers_ShouldReturnUserList() throws Exception {\n        User user1 = new User(\"John Doe\", \"john@example.com\");\n        User user2 = new User(\"Jane Smith\", \"jane@example.com\");\n        \n        when(userService.findAll()).thenReturn(Arrays.asList(user1, user2));\n        \n        mockMvc.perform(get(\"/api/users\"))\n                .andExpect(status().isOk())\n                .andExpect(jsonPath(\"$\").isArray())\n                .andExpected(jsonPath(\"$.length()\").value(2));\n    }\n}"
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                ".gitignore": "# Compiled class file\n*.class\n\n# Log file\n*.log\n\n# BlueJ files\n*.ctxt\n\n# Mobile Tools for Java (J2ME)\n.mtj.tmp/\n\n# Package Files #\n*.jar\n*.war\n*.nar\n*.ear\n*.zip\n*.tar.gz\n*.rar\n\n# virtual machine crash logs\nhs_err_pid*\n\n# Maven\ntarget/\npom.xml.tag\npom.xml.releaseBackup\npom.xml.versionsBackup\npom.xml.next\nrelease.properties\ndependency-reduced-pom.xml\nbuildNumber.properties\n.mvn/timing.properties\n.mvn/wrapper/maven-wrapper.jar\n\n# IDE\n.idea/\n*.iws\n*.iml\n*.ipr\n.vscode/\n\n# OS\n.DS_Store\nThumbs.db",
                "README.md": "# Spring Boot Project\n\n## Prerequisites\n\n- Java 17 or higher\n- Maven 3.6 or higher\n\n## Getting Started\n\n1. Clone the repository\n2. Navigate to the project directory\n3. Run the application:\n\n```bash\n./mvnw spring-boot:run\n```\n\nOr build and run:\n\n```bash\n./mvnw clean package\njava -jar target/demo-0.0.1-SNAPSHOT.jar\n```\n\n## API Endpoints\n\n- Health Check: `GET /api/health`\n- Get All Users: `GET /api/users`\n- Get User by ID: `GET /api/users/{id}`\n- Create User: `POST /api/users`\n- H2 Console: `http://localhost:8080/h2-console` (development only)\n\n## Testing\n\n```bash\n./mvnw test\n```\n\n## Configuration\n\n- Development: `application.properties`\n- Production: `application-prod.properties`\n\n## Database\n\n- Development: H2 in-memory database\n- Production: PostgreSQL (configure in application-prod.properties)"
            },
            dependencies=["org.springframework.boot:spring-boot-starter-web", "org.springframework.boot:spring-boot-starter-data-jpa", "org.springframework.boot:spring-boot-starter-validation", "com.h2database:h2"],
            dev_dependencies=["org.springframework.boot:spring-boot-starter-test", "org.springframework.boot:spring-boot-testcontainers"],
            scripts={
                "build": "mvn clean compile",
                "test": "mvn test",
                "run": "mvn spring-boot:run",
                "package": "mvn clean package",
                "install": "mvn clean install"
            }
        )
        
        # Express.js шаблон
        templates["express"] = cls(
            name="Express.js Project",
            language="javascript",
            framework="express",
            description="Standard Express.js REST API structure with TypeScript support",
            structure={
                "package.json": """{
  "name": "express-api",
  "version": "1.0.0",
  "description": "Express.js REST API",
  "main": "dist/server.js",
  "scripts": {
    "start": "node dist/server.js",
    "dev": "nodemon src/server.ts",
    "build": "tsc",
    "test": "jest",
    "test:watch": "jest --watch",
    "lint": "eslint src/**/*.ts",
    "lint:fix": "eslint src/**/*.ts --fix"
  },
  "keywords": ["express", "api", "typescript", "nodejs"],
  "author": "",
  "license": "MIT"
}""",
                "tsconfig.json": """{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}""",
                "src": {
                    "server.ts": "import express from 'express';\nimport cors from 'cors';\nimport helmet from 'helmet';\nimport morgan from 'morgan';\nimport { config } from './config/database';\nimport { errorHandler } from './middleware/errorHandler';\nimport userRoutes from './routes/users';\nimport indexRoutes from './routes/index';\n\nconst app = express();\nconst PORT = process.env.PORT || 3000;\n\n// Middleware\napp.use(helmet());\napp.use(cors());\napp.use(morgan('combined'));\napp.use(express.json());\napp.use(express.urlencoded({ extended: true }));\n\n// Routes\napp.use('/api', indexRoutes);\napp.use('/api/users', userRoutes);\n\n// Error handling\napp.use(errorHandler);\n\n// Start server\napp.listen(PORT, () => {\n  console.log(`Server is running on port ${PORT}`);\n});",
                    "controllers": {
                        "userController.ts": "import { Request, Response, NextFunction } from 'express';\nimport { User } from '../models/User';\nimport { UserService } from '../services/userService';\n\nexport class UserController {\n  private userService: UserService;\n\n  constructor() {\n    this.userService = new UserService();\n  }\n\n  async getAllUsers(req: Request, res: Response, next: NextFunction): Promise<void> {\n    try {\n      const users = await this.userService.findAll();\n      res.json(users);\n    } catch (error) {\n      next(error);\n    }\n  }\n\n  async getUserById(req: Request, res: Response, next: NextFunction): Promise<void> {\n    try {\n      const { id } = req.params;\n      const user = await this.userService.findById(parseInt(id));\n      \n      if (!user) {\n        res.status(404).json({ message: 'User not found' });\n        return;\n      }\n      \n      res.json(user);\n    } catch (error) {\n      next(error);\n    }\n  }\n\n  async createUser(req: Request, res: Response, next: NextFunction): Promise<void> {\n    try {\n      const userData = req.body;\n      const user = await this.userService.create(userData);\n      res.status(201).json(user);\n    } catch (error) {\n      next(error);\n    }\n  }\n\n  async updateUser(req: Request, res: Response, next: NextFunction): Promise<void> {\n    try {\n      const { id } = req.params;\n      const userData = req.body;\n      const user = await this.userService.update(parseInt(id), userData);\n      \n      if (!user) {\n        res.status(404).json({ message: 'User not found' });\n        return;\n      }\n      \n      res.json(user);\n    } catch (error) {\n      next(error);\n    }\n  }\n\n  async deleteUser(req: Request, res: Response, next: NextFunction): Promise<void> {\n    try {\n      const { id } = req.params;\n      const deleted = await this.userService.delete(parseInt(id));\n      \n      if (!deleted) {\n        res.status(404).json({ message: 'User not found' });\n        return;\n      }\n      \n      res.status(204).send();\n    } catch (error) {\n      next(error);\n    }\n  }\n}"
                    },
                    "models": {
                        "User.ts": "export interface User {\n  id?: number;\n  name: string;\n  email: string;\n  createdAt?: Date;\n  updatedAt?: Date;\n}\n\nexport interface CreateUserDto {\n  name: string;\n  email: string;\n}\n\nexport interface UpdateUserDto {\n  name?: string;\n  email?: string;\n}"
                    },
                    "services": {
                        "userService.ts": "import { User, CreateUserDto, UpdateUserDto } from '../models/User';\n\nexport class UserService {\n  private users: User[] = [];\n  private nextId = 1;\n\n  async findAll(): Promise<User[]> {\n    return this.users;\n  }\n\n  async findById(id: number): Promise<User | undefined> {\n    return this.users.find(user => user.id === id);\n  }\n\n  async create(userData: CreateUserDto): Promise<User> {\n    const user: User = {\n      id: this.nextId++,\n      ...userData,\n      createdAt: new Date(),\n      updatedAt: new Date()\n    };\n    \n    this.users.push(user);\n    return user;\n  }\n\n  async update(id: number, userData: UpdateUserDto): Promise<User | undefined> {\n    const userIndex = this.users.findIndex(user => user.id === id);\n    \n    if (userIndex === -1) {\n      return undefined;\n    }\n    \n    this.users[userIndex] = {\n      ...this.users[userIndex],\n      ...userData,\n      updatedAt: new Date()\n    };\n    \n    return this.users[userIndex];\n  }\n\n  async delete(id: number): Promise<boolean> {\n    const userIndex = this.users.findIndex(user => user.id === id);\n    \n    if (userIndex === -1) {\n      return false;\n    }\n    \n    this.users.splice(userIndex, 1);\n    return true;\n  }\n}"
                    },
                    "routes": {
                        "index.ts": "import { Router, Request, Response } from 'express';\n\nconst router = Router();\n\nrouter.get('/health', (req: Request, res: Response) => {\n  res.json({ \n    status: 'healthy', \n    timestamp: new Date().toISOString(),\n    uptime: process.uptime()\n  });\n});\n\nrouter.get('/', (req: Request, res: Response) => {\n  res.json({ \n    message: 'Express.js API Server',\n    version: '1.0.0'\n  });\n});\n\nexport default router;",
                        "users.ts": "import { Router } from 'express';\nimport { UserController } from '../controllers/userController';\nimport { validateUser } from '../middleware/validation';\n\nconst router = Router();\nconst userController = new UserController();\n\nrouter.get('/', userController.getAllUsers.bind(userController));\nrouter.get('/:id', userController.getUserById.bind(userController));\nrouter.post('/', validateUser, userController.createUser.bind(userController));\nrouter.put('/:id', validateUser, userController.updateUser.bind(userController));\nrouter.delete('/:id', userController.deleteUser.bind(userController));\n\nexport default router;"
                    },
                    "middleware": {
                        "errorHandler.ts": "import { Request, Response, NextFunction } from 'express';\n\nexport interface AppError extends Error {\n  statusCode?: number;\n  isOperational?: boolean;\n}\n\nexport const errorHandler = (err: AppError, req: Request, res: Response, next: NextFunction): void => {\n  const statusCode = err.statusCode || 500;\n  const message = err.message || 'Internal Server Error';\n  \n  console.error(`Error ${statusCode}: ${message}`);\n  console.error(err.stack);\n  \n  res.status(statusCode).json({\n    error: {\n      message,\n      status: statusCode,\n      timestamp: new Date().toISOString()\n    }\n  });\n};",
                        "validation.ts": "import { Request, Response, NextFunction } from 'express';\nimport { body, validationResult } from 'express-validator';\n\nexport const validateUser = [\n  body('name')\n    .notEmpty()\n    .withMessage('Name is required')\n    .isLength({ min: 2, max: 50 })\n    .withMessage('Name must be between 2 and 50 characters'),\n  \n  body('email')\n    .isEmail()\n    .withMessage('Valid email is required')\n    .normalizeEmail(),\n  \n  (req: Request, res: Response, next: NextFunction) => {\n    const errors = validationResult(req);\n    \n    if (!errors.isEmpty()) {\n      res.status(400).json({\n        error: {\n          message: 'Validation failed',\n          details: errors.array()\n        }\n      });\n      return;\n    }\n    \n    next();\n  }\n];"
                    },
                    "config": {
                        "database.ts": "export const config = {\n  development: {\n    host: process.env.DB_HOST || 'localhost',\n    port: parseInt(process.env.DB_PORT || '5432'),\n    database: process.env.DB_NAME || 'express_dev',\n    username: process.env.DB_USER || 'postgres',\n    password: process.env.DB_PASS || 'password'\n  },\n  test: {\n    host: process.env.DB_HOST || 'localhost',\n    port: parseInt(process.env.DB_PORT || '5432'),\n    database: process.env.DB_NAME || 'express_test',\n    username: process.env.DB_USER || 'postgres',\n    password: process.env.DB_PASS || 'password'\n  },\n  production: {\n    host: process.env.DB_HOST,\n    port: parseInt(process.env.DB_PORT || '5432'),\n    database: process.env.DB_NAME,\n    username: process.env.DB_USER,\n    password: process.env.DB_PASS\n  }\n};"
                    }
                },
                "tests": {
                    "user.test.ts": "import request from 'supertest';\nimport express from 'express';\nimport userRoutes from '../src/routes/users';\n\nconst app = express();\napp.use(express.json());\napp.use('/api/users', userRoutes);\n\ndescribe('User API', () => {\n  describe('GET /api/users', () => {\n    it('should return empty array initially', async () => {\n      const response = await request(app)\n        .get('/api/users')\n        .expect(200);\n      \n      expect(response.body).toEqual([]);\n    });\n  });\n  \n  describe('POST /api/users', () => {\n    it('should create a new user', async () => {\n      const userData = {\n        name: 'John Doe',\n        email: 'john@example.com'\n      };\n      \n      const response = await request(app)\n        .post('/api/users')\n        .send(userData)\n        .expect(201);\n      \n      expect(response.body).toMatchObject(userData);\n      expect(response.body.id).toBeDefined();\n      expect(response.body.createdAt).toBeDefined();\n    });\n    \n    it('should return 400 for invalid user data', async () => {\n      const invalidData = {\n        name: '',\n        email: 'invalid-email'\n      };\n      \n      await request(app)\n        .post('/api/users')\n        .send(invalidData)\n        .expect(400);\n    });\n  });\n});",
                    "jest.config.js": "module.exports = {\n  preset: 'ts-jest',\n  testEnvironment: 'node',\n  roots: ['<rootDir>/tests'],\n  testMatch: ['**/*.test.ts'],\n  collectCoverageFrom: [\n    'src/**/*.ts',\n    '!src/**/*.d.ts'\n  ],\n  coverageDirectory: 'coverage',\n  coverageReporters: ['text', 'lcov', 'html']\n};"
                },
                "public": {
                    "index.html": "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n    <meta charset=\"UTF-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n    <title>Express.js API</title>\n    <style>\n        body { font-family: Arial, sans-serif; margin: 40px; }\n        .container { max-width: 600px; margin: 0 auto; }\n        .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }\n    </style>\n</head>\n<body>\n    <div class=\"container\">\n        <h1>Express.js API Server</h1>\n        <p>Welcome to the Express.js REST API server.</p>\n        \n        <h2>Available Endpoints:</h2>\n        <div class=\"endpoint\"><strong>GET</strong> /api/health - Health check</div>\n        <div class=\"endpoint\"><strong>GET</strong> /api/users - Get all users</div>\n        <div class=\"endpoint\"><strong>POST</strong> /api/users - Create user</div>\n        <div class=\"endpoint\"><strong>GET</strong> /api/users/:id - Get user by ID</div>\n        <div class=\"endpoint\"><strong>PUT</strong> /api/users/:id - Update user</div>\n        <div class=\"endpoint\"><strong>DELETE</strong> /api/users/:id - Delete user</div>\n    </div>\n</body>\n</html>"
                },
                ".env.example": "# Server Configuration\nPORT=3000\nNODE_ENV=development\n\n# Database Configuration\nDB_HOST=localhost\nDB_PORT=5432\nDB_NAME=express_dev\nDB_USER=postgres\nDB_PASS=password\n\n# JWT Configuration\nJWT_SECRET=your-secret-key\nJWT_EXPIRES_IN=24h",
                ".gitignore": "# Dependencies\nnode_modules/\nnpm-debug.log*\nyarn-debug.log*\nyarn-error.log*\n\n# Runtime data\npids\n*.pid\n*.seed\n*.pid.lock\n\n# Coverage directory used by tools like istanbul\ncoverage/\n\n# nyc test coverage\n.nyc_output\n\n# Grunt intermediate storage\n.grunt\n\n# Bower dependency directory\nbower_components\n\n# node-waf configuration\n.lock-wscript\n\n# Compiled binary addons\nbuild/Release\n\n# Dependency directories\nnode_modules/\njspm_packages/\n\n# TypeScript cache\n*.tsbuildinfo\n\n# Optional npm cache directory\n.npm\n\n# Optional eslint cache\n.eslintcache\n\n# Output of 'npm pack'\n*.tgz\n\n# Yarn Integrity file\n.yarn-integrity\n\n# dotenv environment variables file\n.env\n.env.test\n.env.local\n.env.production\n\n# parcel-bundler cache\n.cache\n.parcel-cache\n\n# next.js build output\n.next\n\n# nuxt.js build output\n.nuxt\n\n# vuepress build output\n.vuepress/dist\n\n# Serverless directories\n.serverless\n\n# FuseBox cache\n.fusebox/\n\n# DynamoDB Local files\n.dynamodb/\n\n# TernJS port file\n.tern-port\n\n# Build output\ndist/\nbuild/\n\n# IDE\n.vscode/\n.idea/\n*.swp\n*.swo\n\n# OS\n.DS_Store\nThumbs.db",
                "README.md": "# Express.js API Server\n\nA modern Express.js REST API server built with TypeScript.\n\n## Features\n\n- TypeScript support\n- RESTful API design\n- Input validation\n- Error handling\n- CORS enabled\n- Security headers with Helmet\n- Request logging\n- Unit testing with Jest\n- Code linting with ESLint\n\n## Prerequisites\n\n- Node.js 16+ \n- npm or yarn\n\n## Installation\n\n1. Clone the repository\n2. Install dependencies:\n\n```bash\nnpm install\n```\n\n3. Copy environment variables:\n\n```bash\ncp .env.example .env\n```\n\n4. Update the `.env` file with your configuration\n\n## Development\n\n```bash\n# Start development server with hot reload\nnpm run dev\n\n# Build TypeScript\nnpm run build\n\n# Start production server\nnpm start\n```\n\n## Testing\n\n```bash\n# Run tests\nnpm test\n\n# Run tests in watch mode\nnpm run test:watch\n```\n\n## API Endpoints\n\n### Health Check\n- `GET /api/health` - Server health status\n\n### Users\n- `GET /api/users` - Get all users\n- `GET /api/users/:id` - Get user by ID\n- `POST /api/users` - Create new user\n- `PUT /api/users/:id` - Update user\n- `DELETE /api/users/:id` - Delete user\n\n## Project Structure\n\n```\nsrc/\n├── controllers/     # Request handlers\n├── models/         # Data models and interfaces\n├── routes/         # Route definitions\n├── services/       # Business logic\n├── middleware/     # Custom middleware\n├── config/         # Configuration files\n└── server.ts       # Application entry point\n```\n\n## Code Quality\n\n```bash\n# Lint code\nnpm run lint\n\n# Fix linting issues\nnpm run lint:fix\n```"
            },
            dependencies=["express", "cors", "helmet", "morgan", "express-validator"],
            dev_dependencies=["@types/express", "@types/cors", "@types/morgan", "@types/node", "@types/jest", "@types/supertest", "typescript", "ts-node", "nodemon", "jest", "ts-jest", "supertest", "eslint", "@typescript-eslint/parser", "@typescript-eslint/eslint-plugin"],
            scripts={
                "start": "node dist/server.js",
                "dev": "nodemon src/server.ts",
                "build": "tsc",
                "test": "jest",
                "test:watch": "jest --watch",
                "lint": "eslint src/**/*.ts",
                "lint:fix": "eslint src/**/*.ts --fix"
            }
        )
        
        # React шаблон
        templates["react"] = cls(
            name="React Project",
            language="javascript",
            framework="react",
            description="Standard React application structure",
            structure={
                "package.json": "{}",
                "public": {
                    "index.html": "<!-- Main HTML file -->",
                    "favicon.ico": None
                },
                "src": {
                    "index.js": "// Main entry point",
                    "App.js": "// Main App component",
                    "App.css": "/* App styles */",
                    "components": {
                        "Header.js": "// Header component",
                        "Footer.js": "// Footer component"
                    },
                    "pages": {
                        "Home.js": "// Home page",
                        "About.js": "// About page"
                    },
                    "hooks": {
                        "useAuth.js": "// Authentication hook"
                    },
                    "utils": {
                        "api.js": "// API utilities"
                    },
                    "styles": {
                        "globals.css": "/* Global styles */"
                    }
                },
                "tests": {
                    "App.test.js": "// App tests"
                }
            },
            dependencies=["react", "react-dom", "react-router-dom"],
            dev_dependencies=["@testing-library/react", "@testing-library/jest-dom"],
            scripts={
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test"
            }
        )
        
        # ASP.NET Core шаблон
        templates["aspnet-core"] = cls(
            name="ASP.NET Core Project",
            language="csharp",
            framework="aspnet-core",
            description="Standard ASP.NET Core web API structure",
            structure={
                "Program.cs": "// Main program file",
                "appsettings.json": "{}",
                "Controllers": {
                    "WeatherForecastController.cs": "// Weather controller"
                },
                "Models": {
                    "WeatherForecast.cs": "// Weather model"
                },
                "Services": {
                    "IWeatherService.cs": "// Weather service interface",
                    "WeatherService.cs": "// Weather service implementation"
                },
                "Data": {
                    "ApplicationDbContext.cs": "// Database context"
                },
                "Properties": {
                    "launchSettings.json": "{}"
                }
            },
            dependencies=["Microsoft.AspNetCore.App"],
            dev_dependencies=["Microsoft.AspNetCore.Mvc.Testing"],
            scripts={
                "build": "dotnet build",
                "run": "dotnet run",
                "test": "dotnet test"
            }
        )
        
        return templates

    @classmethod
    def get_builtin_template(cls, template_name: str) -> Optional['StructureTemplate']:
        """Получение встроенного шаблона по имени"""
        templates = cls.create_builtin_templates()
        return templates.get(template_name)

    @classmethod
    def get_builtin_templates_for_language(cls, language: str) -> List['StructureTemplate']:
        """Получение встроенных шаблонов для языка"""
        templates = cls.create_builtin_templates()
        return [template for template in templates.values() if template.language == language]

    @classmethod
    def get_all_builtin_templates(cls) -> List['StructureTemplate']:
        """Получение всех встроенных шаблонов"""
        templates = cls.create_builtin_templates()
        return list(templates.values())

    def is_compatible_with_language(self, language: str) -> bool:
        """Проверка совместимости шаблона с языком"""
        return self.language == language

    def get_estimated_size(self) -> int:
        """Оценка размера проекта в байтах"""
        size = 0
        for file_path in self.get_all_files():
            content = self.get_file_content(file_path)
            if content:
                size += len(content.encode('utf-8'))
            else:
                # Базовый размер для пустых файлов
                size += 100
        return size

    def __str__(self) -> str:
        """Строковое представление шаблона"""
        framework_info = f" ({self.framework})" if self.framework else ""
        return f"{self.name} - {self.language}{framework_info}"

    def __repr__(self) -> str:
        """Представление для отладки"""
        return f"StructureTemplate(name='{self.name}', language='{self.language}', framework='{self.framework}')"