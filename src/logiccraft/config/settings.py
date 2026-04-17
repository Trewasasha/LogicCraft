"""Настройки приложения"""

import json
from pathlib import Path
from typing import Dict, Any


class AppSettings:
    """Настройки приложения"""

    def __init__(self, config_path: str = "theme_pref.json"):
        self.config_path = Path(config_path)
        self.settings = self._load_settings()

    def _load_settings(self) -> Dict[str, Any]:
        """Загрузить настройки из файла"""
        default_settings = {
            "theme": "light",
            "language": "python",
            "grid_size": 50,
            "show_grid": True,
            "auto_save": True,
            "auto_save_interval": 300,  # секунд
            "last_open_path": str(Path.home()),
            "window_width": 1200,
            "window_height": 800,
            "font_size": 10
        }

        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    default_settings.update(loaded)
            except Exception:
                pass

        return default_settings

    def save(self):
        """Сохранить настройки"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def get(self, key: str, default=None):
        """Получить значение"""
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        """Установить значение"""
        self.settings[key] = value
        self.save()

    @property
    def theme(self) -> str:
        return self.settings.get("theme", "light")

    @property
    def language(self) -> str:
        return self.settings.get("language", "python")

    @property
    def show_grid(self) -> bool:
        return self.settings.get("show_grid", True)

    @property
    def grid_size(self) -> int:
        return self.settings.get("grid_size", 50)

    @property
    def auto_save(self) -> bool:
        return self.settings.get("auto_save", True)


# Глобальный экземпляр настроек
settings = AppSettings()