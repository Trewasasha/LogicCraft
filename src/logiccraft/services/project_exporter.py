"""Сервис экспорта проектов с готовой структурой папок"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from ..models.diagram import UMLDiagram
from ..models.project_settings import ProjectSettings
from .code_generator import CodeGenerator
from ..templates.config import get_language_config


class ProjectExporter:
    """Экспортер проектов с готовой структурой"""
    
    def __init__(self):
        self.generator = CodeGenerator()
        
    def export_project(self, diagram: UMLDiagram, settings: ProjectSettings, 
                      export_path: str) -> Dict[str, Any]:
        """Экспорт полного проекта с структурой папок"""
        
        project_path = Path(export_path) / settings.name
        
        # Создаем базовую структуру
        structure = self._create_project_structure(settings, project_path)
        
        # Генерируем код
        files = self.generator.generate_files(diagram, settings.language)
        
        # Размещаем файлы по структуре
        self._place_code_files(files, structure, settings)
        
        # Создаем конфигурационные файлы
        if settings.include_config:
            self._create_config_files(structure, settings, diagram)
            
        # Создаем тесты
        if settings.include_tests:
            self._create_test_files(structure, settings, diagram)
            
        # Создаем документацию
        if settings.include_docs:
            self._create_documentation(structure, settings, diagram)
            
        # Создаем файлы на диске
        created_files = self._write_structure_to_disk(structure)
        
        return {
            "project_path": str(project_path),
            "files_created": len(created_files),
            "structure": structure,
            "settings": settings
        }
    
    def _create_project_structure(self, settings: ProjectSettings, 
                                project_path: Path) -> Dict[str, Any]:
        """Создание структуры проекта в зависимости от языка и типа"""
        
        if settings.language == "python":
            return self._create_python_structure(settings, project_path)
        elif settings.language == "java":
            return self._create_java_structure(settings, project_path)
        elif settings.language in ["javascript", "typescript"]:
            return self._create_js_structure(settings, project_path)
        elif settings.language == "csharp":
            return self._create_csharp_structure(settings, project_path)
        else:
            return self._create_generic_structure(settings, project_path)
    
    def _create_python_structure(self, settings: ProjectSettings, 
                               project_path: Path) -> Dict[str, Any]:
        """Структура Python проекта"""
        
        package_name = settings.name.lower().replace("-", "_")
        
        structure = {
            "type": "directory",
            "path": project_path,
            "children": {
                "README.md": {
                    "type": "file",
                    "content": self._generate_readme(settings)
                },
                "requirements.txt": {
                    "type": "file", 
                    "content": self._generate_python_requirements(settings)
                },
                "setup.py": {
                    "type": "file",
                    "content": self._generate_python_setup(settings)
                },
                ".gitignore": {
                    "type": "file",
                    "content": self._generate_python_gitignore()
                }
            }
        }
        
        # Основной пакет
        if settings.structure_type == "simple":
            structure["children"][package_name] = {
                "type": "directory",
                "children": {
                    "__init__.py": {"type": "file", "content": ""},
                    "main.py": {"type": "file", "content": self._generate_python_main(settings)}
                }
            }
        elif settings.structure_type == "mvc":
            structure["children"][package_name] = {
                "type": "directory", 
                "children": {
                    "__init__.py": {"type": "file", "content": ""},
                    "models": {
                        "type": "directory",
                        "children": {"__init__.py": {"type": "file", "content": ""}}
                    },
                    "views": {
                        "type": "directory",
                        "children": {"__init__.py": {"type": "file", "content": ""}}
                    },
                    "controllers": {
                        "type": "directory", 
                        "children": {"__init__.py": {"type": "file", "content": ""}}
                    },
                    "main.py": {"type": "file", "content": self._generate_python_main(settings)}
                }
            }
        elif settings.structure_type == "layered":
            structure["children"][package_name] = {
                "type": "directory",
                "children": {
                    "__init__.py": {"type": "file", "content": ""},
                    "domain": {
                        "type": "directory",
                        "children": {"__init__.py": {"type": "file", "content": ""}}
                    },
                    "application": {
                        "type": "directory",
                        "children": {"__init__.py": {"type": "file", "content": ""}}
                    },
                    "infrastructure": {
                        "type": "directory",
                        "children": {"__init__.py": {"type": "file", "content": ""}}
                    },
                    "presentation": {
                        "type": "directory",
                        "children": {"__init__.py": {"type": "file", "content": ""}}
                    }
                }
            }
        
        # Тесты
        if settings.include_tests:
            structure["children"]["tests"] = {
                "type": "directory",
                "children": {
                    "__init__.py": {"type": "file", "content": ""},
                    "test_models.py": {"type": "file", "content": self._generate_python_tests(settings)}
                }
            }
            
        # Документация
        if settings.include_docs:
            structure["children"]["docs"] = {
                "type": "directory", 
                "children": {
                    "index.md": {"type": "file", "content": self._generate_docs_index(settings)},
                    "api.md": {"type": "file", "content": "# API Documentation\n\nTODO: Add API documentation"}
                }
            }
            
        return structure
    
    def _create_java_structure(self, settings: ProjectSettings, 
                             project_path: Path) -> Dict[str, Any]:
        """Структура Java проекта"""
        
        package_path = settings.name.lower().replace("-", "").replace("_", "")
        
        structure = {
            "type": "directory",
            "path": project_path,
            "children": {
                "README.md": {"type": "file", "content": self._generate_readme(settings)},
                "pom.xml": {"type": "file", "content": self._generate_maven_pom(settings)},
                ".gitignore": {"type": "file", "content": self._generate_java_gitignore()},
                "src": {
                    "type": "directory",
                    "children": {
                        "main": {
                            "type": "directory",
                            "children": {
                                "java": {
                                    "type": "directory",
                                    "children": {
                                        "com": {
                                            "type": "directory",
                                            "children": {
                                                "example": {
                                                    "type": "directory",
                                                    "children": {
                                                        package_path: {
                                                            "type": "directory",
                                                            "children": {
                                                                "Main.java": {
                                                                    "type": "file",
                                                                    "content": self._generate_java_main(settings)
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                },
                                "resources": {
                                    "type": "directory",
                                    "children": {
                                        "application.properties": {
                                            "type": "file",
                                            "content": self._generate_java_properties(settings)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        # Тесты для Java
        if settings.include_tests:
            structure["children"]["src"]["children"]["test"] = {
                "type": "directory",
                "children": {
                    "java": {
                        "type": "directory",
                        "children": {
                            "com": {
                                "type": "directory",
                                "children": {
                                    "example": {
                                        "type": "directory",
                                        "children": {
                                            package_path: {
                                                "type": "directory",
                                                "children": {
                                                    "MainTest.java": {
                                                        "type": "file",
                                                        "content": self._generate_java_tests(settings)
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            
        return structure
    
    def _create_js_structure(self, settings: ProjectSettings, 
                           project_path: Path) -> Dict[str, Any]:
        """Структура JavaScript/TypeScript проекта"""
        
        is_typescript = settings.language == "typescript"
        ext = ".ts" if is_typescript else ".js"
        
        structure = {
            "type": "directory",
            "path": project_path,
            "children": {
                "README.md": {"type": "file", "content": self._generate_readme(settings)},
                "package.json": {"type": "file", "content": self._generate_package_json(settings)},
                ".gitignore": {"type": "file", "content": self._generate_js_gitignore()},
                "src": {
                    "type": "directory",
                    "children": {
                        f"index{ext}": {
                            "type": "file",
                            "content": self._generate_js_main(settings)
                        }
                    }
                }
            }
        }
        
        # TypeScript конфигурация
        if is_typescript:
            structure["children"]["tsconfig.json"] = {
                "type": "file",
                "content": self._generate_tsconfig(settings)
            }
            
        # Тесты
        if settings.include_tests:
            test_ext = ".test.ts" if is_typescript else ".test.js"
            structure["children"]["tests"] = {
                "type": "directory",
                "children": {
                    f"index{test_ext}": {
                        "type": "file",
                        "content": self._generate_js_tests(settings)
                    }
                }
            }
            
        return structure
    
    def _create_csharp_structure(self, settings: ProjectSettings, 
                               project_path: Path) -> Dict[str, Any]:
        """Структура C# проекта"""
        
        structure = {
            "type": "directory",
            "path": project_path,
            "children": {
                "README.md": {"type": "file", "content": self._generate_readme(settings)},
                f"{settings.name}.sln": {"type": "file", "content": self._generate_csharp_solution(settings)},
                ".gitignore": {"type": "file", "content": self._generate_csharp_gitignore()},
                settings.name: {
                    "type": "directory",
                    "children": {
                        f"{settings.name}.csproj": {
                            "type": "file",
                            "content": self._generate_csharp_project(settings)
                        },
                        "Program.cs": {
                            "type": "file",
                            "content": self._generate_csharp_main(settings)
                        }
                    }
                }
            }
        }
        
        return structure
    
    def _create_generic_structure(self, settings: ProjectSettings, 
                                project_path: Path) -> Dict[str, Any]:
        """Универсальная структура проекта"""
        
        return {
            "type": "directory",
            "path": project_path,
            "children": {
                "README.md": {"type": "file", "content": self._generate_readme(settings)},
                ".gitignore": {"type": "file", "content": "# Generated files\n*.log\n*.tmp\n"},
                "src": {
                    "type": "directory",
                    "children": {}
                }
            }
        }
    
    def _place_code_files(self, files: Dict[str, str], structure: Dict[str, Any], 
                         settings: ProjectSettings):
        """Размещение сгенерированных файлов в структуре проекта"""
        
        # Определяем целевую папку для кода
        if settings.language == "python":
            package_name = settings.name.lower().replace("-", "_")
            if settings.structure_type == "mvc":
                target_path = ["children", package_name, "children", "models", "children"]
            elif settings.structure_type == "layered":
                target_path = ["children", package_name, "children", "domain", "children"]
            else:
                target_path = ["children", package_name, "children"]
        elif settings.language == "java":
            package_path = settings.name.lower().replace("-", "").replace("_", "")
            target_path = ["children", "src", "children", "main", "children", "java", 
                          "children", "com", "children", "example", "children", package_path, "children"]
        elif settings.language in ["javascript", "typescript"]:
            target_path = ["children", "src", "children"]
        elif settings.language == "csharp":
            target_path = ["children", settings.name, "children"]
        else:
            target_path = ["children", "src", "children"]
        
        # Размещаем файлы
        current = structure
        for path_part in target_path:
            current = current[path_part]
            
        for filename, content in files.items():
            current[filename] = {
                "type": "file",
                "content": content
            }
    
    def _write_structure_to_disk(self, structure: Dict[str, Any]) -> List[str]:
        """Запись структуры на диск"""
        
        created_files = []
        
        def write_recursive(item: Dict[str, Any], current_path: Path):
            if item["type"] == "directory":
                current_path.mkdir(parents=True, exist_ok=True)
                created_files.append(str(current_path))
                
                if "children" in item:
                    for name, child in item["children"].items():
                        child_path = current_path / name
                        write_recursive(child, child_path)
                        
            elif item["type"] == "file":
                current_path.parent.mkdir(parents=True, exist_ok=True)
                with open(current_path, 'w', encoding='utf-8') as f:
                    f.write(item.get("content", ""))
                created_files.append(str(current_path))
        
        write_recursive(structure, structure["path"])
        return created_files

    # ─── Config / Test / Docs stubs (called from export_project) ───────────────

    def _create_config_files(self, structure: Dict[str, Any],
                             settings: ProjectSettings, diagram: UMLDiagram):
        """Дополнительные конфигурационные файлы (CI, лицензия и т.д.)"""
        children = structure["children"]
        if settings.include_license and settings.license:
            children["LICENSE"] = {"type": "file", "content": self._generate_license(settings)}
        if settings.include_ci:
            children[".github"] = {
                "type": "directory",
                "children": {
                    "workflows": {
                        "type": "directory",
                        "children": {
                            "ci.yml": {"type": "file", "content": self._generate_github_actions(settings)}
                        }
                    }
                }
            }

    def _create_test_files(self, structure: Dict[str, Any],
                           settings: ProjectSettings, diagram: UMLDiagram):
        """Тестовые файлы уже добавляются в _create_*_structure; здесь — заглушка"""
        pass

    def _create_documentation(self, structure: Dict[str, Any],
                              settings: ProjectSettings, diagram: UMLDiagram):
        """Документация уже добавляется в _create_*_structure; здесь — заглушка"""
        pass

    # ─── Content generators ─────────────────────────────────────────────────────

    def _generate_readme(self, settings: ProjectSettings) -> str:
        author_line = f"\nAuthor: {settings.author}" if settings.author else ""
        desc_line = f"\n{settings.description}" if settings.description else ""
        return (
            f"# {settings.name}\n"
            f"{desc_line}\n"
            f"Version: {settings.version}{author_line}\n\n"
            f"## Getting Started\n\nTODO: add setup instructions.\n"
        )

    def _generate_python_requirements(self, settings: ProjectSettings) -> str:
        lines = ["# Core dependencies"]
        if settings.include_tests:
            lines += ["", "# Test dependencies", "pytest>=7.0.0", "pytest-cov>=4.0.0"]
        return "\n".join(lines) + "\n"

    def _generate_python_setup(self, settings: ProjectSettings) -> str:
        pkg = settings.name.lower().replace("-", "_")
        return (
            f'from setuptools import setup, find_packages\n\n'
            f'setup(\n'
            f'    name="{settings.name}",\n'
            f'    version="{settings.version}",\n'
            f'    author="{settings.author}",\n'
            f'    description="{settings.description}",\n'
            f'    packages=find_packages(),\n'
            f'    python_requires=">=3.9",\n'
            f')\n'
        )

    def _generate_python_main(self, settings: ProjectSettings) -> str:
        return (
            f'"""Entry point for {settings.name}"""\n\n\n'
            f'def main():\n'
            f'    print("Hello from {settings.name}")\n\n\n'
            f'if __name__ == "__main__":\n'
            f'    main()\n'
        )

    def _generate_python_tests(self, settings: ProjectSettings) -> str:
        return (
            f'"""Tests for {settings.name}"""\n\n\n'
            f'def test_placeholder():\n'
            f'    assert True\n'
        )

    def _generate_python_gitignore(self) -> str:
        return (
            "__pycache__/\n*.py[cod]\n*.egg-info/\ndist/\nbuild/\n"
            ".venv/\nvenv/\n.env\n.DS_Store\n*.log\n.pytest_cache/\n"
        )

    def _generate_maven_pom(self, settings: ProjectSettings) -> str:
        pkg = settings.name.lower().replace("-", "").replace("_", "")
        return (
            f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<project xmlns="http://maven.apache.org/POM/4.0.0"\n'
            f'         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
            f'         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 '
            f'http://maven.apache.org/xsd/maven-4.0.0.xsd">\n'
            f'    <modelVersion>4.0.0</modelVersion>\n'
            f'    <groupId>com.example</groupId>\n'
            f'    <artifactId>{settings.name}</artifactId>\n'
            f'    <version>{settings.version}</version>\n'
            f'    <properties>\n'
            f'        <java.version>17</java.version>\n'
            f'        <maven.compiler.source>17</maven.compiler.source>\n'
            f'        <maven.compiler.target>17</maven.compiler.target>\n'
            f'    </properties>\n'
            f'</project>\n'
        )

    def _generate_java_main(self, settings: ProjectSettings) -> str:
        pkg = settings.name.lower().replace("-", "").replace("_", "")
        return (
            f'package com.example.{pkg};\n\n'
            f'public class Main {{\n'
            f'    public static void main(String[] args) {{\n'
            f'        System.out.println("Hello from {settings.name}");\n'
            f'    }}\n'
            f'}}\n'
        )

    def _generate_java_properties(self, settings: ProjectSettings) -> str:
        return f'# {settings.name} configuration\napp.name={settings.name}\napp.version={settings.version}\n'

    def _generate_java_tests(self, settings: ProjectSettings) -> str:
        pkg = settings.name.lower().replace("-", "").replace("_", "")
        return (
            f'package com.example.{pkg};\n\n'
            f'import org.junit.jupiter.api.Test;\n'
            f'import static org.junit.jupiter.api.Assertions.*;\n\n'
            f'class MainTest {{\n'
            f'    @Test\n'
            f'    void placeholderTest() {{\n'
            f'        assertTrue(true);\n'
            f'    }}\n'
            f'}}\n'
        )

    def _generate_java_gitignore(self) -> str:
        return "target/\n*.class\n*.jar\n.idea/\n*.iml\n.DS_Store\n"

    def _generate_package_json(self, settings: ProjectSettings) -> str:
        is_ts = settings.language == "typescript"
        scripts = {
            "start": "node dist/index.js" if is_ts else "node src/index.js",
            "build": "tsc" if is_ts else "echo 'No build step'",
            "test": "jest"
        }
        deps: Dict[str, str] = {}
        dev_deps: Dict[str, str] = {"jest": "^29.0.0"}
        if is_ts:
            dev_deps.update({"typescript": "^5.0.0", "@types/node": "^20.0.0", "ts-node": "^10.0.0"})

        import json as _json
        data = {
            "name": settings.name,
            "version": settings.version,
            "description": settings.description,
            "author": settings.author,
            "main": "dist/index.js" if is_ts else "src/index.js",
            "scripts": scripts,
            "dependencies": deps,
            "devDependencies": dev_deps
        }
        return _json.dumps(data, indent=2) + "\n"

    def _generate_tsconfig(self, settings: ProjectSettings) -> str:
        import json as _json
        cfg = {
            "compilerOptions": {
                "target": "ES2020",
                "module": "commonjs",
                "lib": ["ES2020"],
                "outDir": "./dist",
                "rootDir": "./src",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True
            },
            "include": ["src/**/*"],
            "exclude": ["node_modules", "dist"]
        }
        return _json.dumps(cfg, indent=2) + "\n"

    def _generate_js_main(self, settings: ProjectSettings) -> str:
        if settings.language == "typescript":
            return f'// Entry point for {settings.name}\n\nconsole.log("Hello from {settings.name}");\n'
        return f'// Entry point for {settings.name}\n\nconsole.log("Hello from {settings.name}");\n'

    def _generate_js_tests(self, settings: ProjectSettings) -> str:
        ext = "ts" if settings.language == "typescript" else "js"
        return (
            f'// Tests for {settings.name}\n\n'
            f'test("placeholder", () => {{\n'
            f'    expect(true).toBe(true);\n'
            f'}});\n'
        )

    def _generate_js_gitignore(self) -> str:
        return "node_modules/\ndist/\nbuild/\n.env\n.DS_Store\n*.log\ncoverage/\n"

    def _generate_csharp_solution(self, settings: ProjectSettings) -> str:
        return (
            f'\nMicrosoft Visual Studio Solution File, Format Version 12.00\n'
            f'# Visual Studio Version 17\n'
            f'Project("{{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}}") = "{settings.name}", '
            f'"{settings.name}\\{settings.name}.csproj", '
            f'"{{00000000-0000-0000-0000-000000000001}}"\n'
            f'EndProject\n'
        )

    def _generate_csharp_project(self, settings: ProjectSettings) -> str:
        return (
            f'<Project Sdk="Microsoft.NET.Sdk">\n'
            f'  <PropertyGroup>\n'
            f'    <OutputType>Exe</OutputType>\n'
            f'    <TargetFramework>net8.0</TargetFramework>\n'
            f'    <AssemblyName>{settings.name}</AssemblyName>\n'
            f'    <RootNamespace>{settings.name}</RootNamespace>\n'
            f'    <Version>{settings.version}</Version>\n'
            f'    <Authors>{settings.author}</Authors>\n'
            f'    <Description>{settings.description}</Description>\n'
            f'  </PropertyGroup>\n'
            f'</Project>\n'
        )

    def _generate_csharp_main(self, settings: ProjectSettings) -> str:
        return (
            f'// Entry point for {settings.name}\n\n'
            f'Console.WriteLine("Hello from {settings.name}");\n'
        )

    def _generate_csharp_gitignore(self) -> str:
        return "bin/\nobj/\n*.user\n.vs/\n*.suo\n.DS_Store\n"

    def _generate_docs_index(self, settings: ProjectSettings) -> str:
        return f'# {settings.name} Documentation\n\n{settings.description}\n\n## Overview\n\nTODO: add documentation.\n'

    def _generate_license(self, settings: ProjectSettings) -> str:
        year = __import__("datetime").date.today().year
        author = settings.author or "Author"
        if settings.license == "MIT":
            return (
                f'MIT License\n\nCopyright (c) {year} {author}\n\n'
                f'Permission is hereby granted, free of charge, to any person obtaining a copy\n'
                f'of this software and associated documentation files (the "Software"), to deal\n'
                f'in the Software without restriction, including without limitation the rights\n'
                f'to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n'
                f'copies of the Software, and to permit persons to whom the Software is\n'
                f'furnished to do so, subject to the following conditions:\n\n'
                f'The above copyright notice and this permission notice shall be included in all\n'
                f'copies or substantial portions of the Software.\n\n'
                f'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.\n'
            )
        return f'Copyright (c) {year} {author}. All rights reserved.\n'

    def _generate_github_actions(self, settings: ProjectSettings) -> str:
        lang = settings.language
        if lang == "python":
            run_cmd = "pytest"
            setup = "pip install -r requirements.txt"
        elif lang == "java":
            run_cmd = "mvn test"
            setup = ""
        elif lang in ["javascript", "typescript"]:
            run_cmd = "npm test"
            setup = "npm install"
        else:
            run_cmd = "echo 'No tests configured'"
            setup = ""

        steps = f'      - name: Install\n        run: {setup}\n' if setup else ""
        return (
            f'name: CI\non: [push, pull_request]\njobs:\n  build:\n'
            f'    runs-on: ubuntu-latest\n    steps:\n'
            f'      - uses: actions/checkout@v4\n'
            f'{steps}'
            f'      - name: Test\n        run: {run_cmd}\n'
        )

    def preview_structure(self, settings: ProjectSettings) -> Dict[str, Any]:
        """Предпросмотр структуры без создания файлов на диске"""
        from ..models.diagram import UMLDiagram
        dummy_diagram = UMLDiagram(name="preview")
        project_path = Path("/preview") / settings.name
        return self._create_project_structure(settings, project_path)

    def get_flat_file_list(self, structure: Dict[str, Any], base: str = "") -> List[str]:
        """Получить плоский список путей файлов из структуры"""
        result = []
        for name, child in structure.get("children", {}).items():
            path = f"{base}/{name}" if base else name
            if child["type"] == "directory":
                result.extend(self.get_flat_file_list(child, path))
            else:
                result.append(path)
        return result
