"""Diagram save/load utilities for PyQt6"""

import json
from pathlib import Path
from typing import List, Dict, Any


def save_diagram(cards_data: List[Dict], connections_data: List[Dict],
                 filepath: str):
    """Сохраняет диаграмму в JSON файл"""
    data = {
        "cards": cards_data,
        "connections": connections_data
    }
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_diagram(filepath: str) -> tuple[List[Dict], List[Dict]]:
    """Загружает диаграмму из JSON файла"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("cards", []), data.get("connections", [])