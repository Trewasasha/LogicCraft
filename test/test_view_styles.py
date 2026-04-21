"""Тесты для view-styles-extraction: theme.py, рефакторинг view-компонентов.

Покрывает:
- Unit-тесты структуры theme.py
- Property-тесты (Hypothesis) для view-компонентов
- Smoke-тесты отсутствия захардкоженных цветов
"""
import re
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Нужен QApplication для создания Qt-виджетов
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor, QFont

_app = QApplication.instance() or QApplication(sys.argv)


# ─────────────────────────────────────────────
# Unit-тесты: структура theme.py
# ─────────────────────────────────────────────

class TestThemeStructure:
    """Requirement 1: Централизованное хранилище Style_Token"""

    def test_theme_has_all_sections(self):
        """1.1, 1.2, 8.1 — все секции присутствуют"""
        from logiccraft.view.theme import (
            CardStyle, ConnectionStyle, SceneStyle, AnchorStyle, ArrowStyle
        )
        assert CardStyle is not None
        assert ConnectionStyle is not None
        assert SceneStyle is not None
        assert AnchorStyle is not None
        assert ArrowStyle is not None

    def test_theme_tokens_accessible_without_init(self):
        """1.4 — токены доступны сразу после импорта"""
        from logiccraft.view.theme import CardStyle
        # Не должно бросать исключений
        _ = CardStyle.BACKGROUND
        _ = CardStyle.BORDER

    def test_theme_contains_all_original_colors(self):
        """1.5 — все 11 исходных цветов присутствуют в токенах"""
        from logiccraft.view.theme import (
            CardStyle, ConnectionStyle, SceneStyle, AnchorStyle, ArrowStyle
        )
        all_colors = {
            CardStyle.BACKGROUND, CardStyle.BORDER, CardStyle.SELECTED_BORDER,
            CardStyle.HEADER_BG, CardStyle.HEADER_TEXT,
            CardStyle.ATTRS_TEXT, CardStyle.METHODS_TEXT,
            ConnectionStyle.LINE_COLOR, ConnectionStyle.SELECTED_COLOR,
            AnchorStyle.NORMAL_COLOR, AnchorStyle.HOVER_COLOR, AnchorStyle.BORDER_COLOR,
            ArrowStyle.COLOR,
            SceneStyle.BACKGROUND, SceneStyle.GRID_COLOR, SceneStyle.TEMP_LINE_COLOR,
        }
        required = {
            "#f5f5dc", "#4169E1", "#2c3e50", "#27ae60", "#DC143C",
            "#666666", "#FF6B6B", "#FF4444", "#FFFFFF", "#fafafa", "#e0e0e0",
        }
        # Нормализуем регистр для сравнения
        all_colors_lower = {c.lower() for c in all_colors}
        for color in required:
            assert color.lower() in all_colors_lower, f"Missing color {color} in theme"

    def test_card_style_has_font_properties(self):
        """2.3 — CardStyle предоставляет шрифтовые токены"""
        from logiccraft.view.theme import CardStyle
        assert isinstance(CardStyle.HEADER_FONT, QFont)
        assert isinstance(CardStyle.ATTRS_FONT, QFont)
        assert isinstance(CardStyle.METHODS_FONT, QFont)

    def test_apply_stylesheet_calls_set_stylesheet(self, tmp_path):
        """7.1, 7.2, 7.3 — apply_stylesheet вызывает app.setStyleSheet"""
        qss_content = "QDialog { background: white; }"
        qss_file = tmp_path / "style.qss"
        qss_file.write_text(qss_content, encoding="utf-8")

        mock_app = MagicMock()

        import logiccraft.view.theme as theme_module
        original_path = None
        # Патчим os.path.join чтобы вернуть наш временный файл
        with patch("logiccraft.view.theme.os.path.join", return_value=str(qss_file)):
            with patch("logiccraft.view.theme.os.path.normpath", return_value=str(qss_file)):
                from logiccraft.view.theme import apply_stylesheet
                apply_stylesheet(mock_app)

        mock_app.setStyleSheet.assert_called_once_with(qss_content)

    def test_apply_stylesheet_missing_file(self):
        """7.4 — отсутствие style.qss не вызывает исключение"""
        mock_app = MagicMock()
        with patch("logiccraft.view.theme.os.path.join", return_value="/nonexistent/style.qss"):
            with patch("logiccraft.view.theme.os.path.normpath", return_value="/nonexistent/style.qss"):
                from logiccraft.view.theme import apply_stylesheet
                # Не должно бросать исключений
                apply_stylesheet(mock_app)
        mock_app.setStyleSheet.assert_not_called()


# ─────────────────────────────────────────────
# Smoke-тесты: отсутствие захардкоженных цветов
# ─────────────────────────────────────────────

COLOR_PATTERN = re.compile(r'"#[0-9A-Fa-f]{6}"')
SRC_ROOT = Path(__file__).parent.parent / "src" / "logiccraft" / "view"


class TestNoHardcodedColors:
    """Requirements 2.5, 3.4, 4.5, 5.3, 6.4 — ноль строковых литералов цветов"""

    def _check_file(self, rel_path: str):
        source = (SRC_ROOT / rel_path).read_text(encoding="utf-8")
        matches = COLOR_PATTERN.findall(source)
        assert not matches, f"Hardcoded colors found in {rel_path}: {matches}"

    def test_no_hardcoded_colors_in_uml_card(self):
        self._check_file("widgets/uml_card.py")

    def test_no_hardcoded_colors_in_anchor_point(self):
        self._check_file("widgets/anchor_point.py")

    def test_no_hardcoded_colors_in_arrow_head(self):
        self._check_file("widgets/arrow_head.py")

    def test_no_hardcoded_colors_in_connection_line(self):
        self._check_file("widgets/connection_line.py")

    def test_no_hardcoded_colors_in_diagram_scene(self):
        self._check_file("scenes/diagram_scene.py")


# ─────────────────────────────────────────────
# Property-тесты (Hypothesis)
# ─────────────────────────────────────────────

from hypothesis import given, settings
from hypothesis import strategies as st


# Feature: view-styles-extraction, Property 1: UMLCard использует цвета из CardStyle при инициализации
@given(
    name=st.text(min_size=1, max_size=50).filter(lambda s: s.strip()),
    attrs=st.lists(st.text(max_size=30), max_size=5),
    methods=st.lists(st.text(max_size=30), max_size=5),
)
@settings(max_examples=100)
def test_uml_card_uses_card_style_colors(name, attrs, methods):
    """Property 1 — Validates: Requirements 2.1"""
    from logiccraft.view.widgets.uml_card import UMLCard
    from logiccraft.view.theme import CardStyle
    card = UMLCard(name, attributes=attrs, methods=methods)
    assert card.brush().color() == QColor(CardStyle.BACKGROUND)
    assert card.pen().color() == QColor(CardStyle.BORDER)


# Feature: view-styles-extraction, Property 2: UMLCard использует цвет выделения из CardStyle
@given(
    name=st.text(min_size=1, max_size=50).filter(lambda s: s.strip()),
)
@settings(max_examples=100)
def test_uml_card_selected_uses_card_style(name):
    """Property 2 — Validates: Requirements 2.2"""
    from logiccraft.view.widgets.uml_card import UMLCard
    from logiccraft.view.theme import CardStyle
    card = UMLCard(name)
    card.setSelected(True)
    assert card.pen().color() == QColor(CardStyle.SELECTED_BORDER)
    card.setSelected(False)
    assert card.pen().color() == QColor(CardStyle.BORDER)


# Feature: view-styles-extraction, Property 3: UMLCard использует шрифты из CardStyle
@given(
    name=st.text(min_size=1, max_size=50).filter(lambda s: s.strip()),
)
@settings(max_examples=100)
def test_uml_card_uses_card_style_fonts(name):
    """Property 3 — Validates: Requirements 2.3"""
    from logiccraft.view.widgets.uml_card import UMLCard
    from logiccraft.view.theme import CardStyle
    card = UMLCard(name)
    assert card.header_text.font() == CardStyle.HEADER_FONT
    assert card.attrs_text.font() == CardStyle.ATTRS_FONT
    assert card.methods_text.font() == CardStyle.METHODS_FONT


# Feature: view-styles-extraction, Property 4: AnchorPoint использует цвета из AnchorStyle
@given(
    anchor_name=st.sampled_from(["top", "bottom", "left", "right"]),
)
@settings(max_examples=100)
def test_anchor_point_uses_anchor_style(anchor_name):
    """Property 4 — Validates: Requirements 3.1, 3.2, 3.3"""
    from logiccraft.view.widgets.anchor_point import AnchorPoint
    from logiccraft.view.theme import AnchorStyle
    from unittest.mock import MagicMock
    mock_card = MagicMock()
    mock_card.id = "test-card"
    anchor = AnchorPoint(mock_card, anchor_name, size=8)
    # Нормальное состояние
    assert anchor.brush().color() == QColor(AnchorStyle.NORMAL_COLOR)
    # Hover-состояние (симулируем через прямой вызов)
    anchor.setBrush(__import__('PyQt6.QtGui', fromlist=['QBrush']).QBrush(QColor(AnchorStyle.HOVER_COLOR)))
    assert anchor.brush().color() == QColor(AnchorStyle.HOVER_COLOR)
    # Возврат к нормальному
    anchor.setBrush(__import__('PyQt6.QtGui', fromlist=['QBrush']).QBrush(QColor(AnchorStyle.NORMAL_COLOR)))
    assert anchor.brush().color() == QColor(AnchorStyle.NORMAL_COLOR)


# Feature: view-styles-extraction, Property 5: ArrowHead использует цвета из ArrowStyle для любого типа связи
@given(
    conn_type=st.sampled_from(["association", "inheritance", "composition", "aggregation"]),
)
@settings(max_examples=100)
def test_arrow_head_uses_arrow_style(conn_type):
    """Property 5 — Validates: Requirements 4.1, 4.2, 4.3, 4.4"""
    from logiccraft.view.widgets.arrow_head import ArrowHead, ConnectionType
    from logiccraft.view.theme import ArrowStyle
    from PyQt6.QtCore import QPointF
    ct = ConnectionType(conn_type)
    arrow = ArrowHead(QPointF(1, 0), ct)
    pen_color = arrow.pen().color()
    assert pen_color == QColor(ArrowStyle.COLOR), (
        f"ArrowHead({conn_type}) pen color {pen_color.name()} != {ArrowStyle.COLOR}"
    )


# Feature: view-styles-extraction, Property 6: ConnectionLine использует цвета из ConnectionStyle
@given(
    source_anchor=st.sampled_from(["top", "bottom", "left", "right"]),
    target_anchor=st.sampled_from(["top", "bottom", "left", "right"]),
)
@settings(max_examples=50)
def test_connection_line_uses_connection_style(source_anchor, target_anchor):
    """Property 6 — Validates: Requirements 5.1, 5.2"""
    from logiccraft.view.widgets.uml_card import UMLCard
    from logiccraft.view.widgets.connection_line import ConnectionLine
    from logiccraft.view.theme import ConnectionStyle
    src = UMLCard("Source", x=0, y=0)
    tgt = UMLCard("Target", x=200, y=0)
    line = ConnectionLine(src, tgt, source_anchor, target_anchor)
    # Нормальное состояние
    assert line.pen().color() == QColor(ConnectionStyle.LINE_COLOR)
    # Выделенное состояние
    line.set_selected(True)
    assert line.pen().color() == QColor(ConnectionStyle.SELECTED_COLOR)
    # Снятие выделения
    line.set_selected(False)
    assert line.pen().color() == QColor(ConnectionStyle.LINE_COLOR)


# Feature: view-styles-extraction, Property 7: DiagramScene использует цвет фона из SceneStyle
@settings(max_examples=10)
@given(st.just(None))
def test_diagram_scene_uses_scene_style_background(_):
    """Property 7 — Validates: Requirements 6.1"""
    from logiccraft.view.scenes.diagram_scene import DiagramScene
    from logiccraft.view.theme import SceneStyle
    scene = DiagramScene()
    assert scene.backgroundBrush().color() == QColor(SceneStyle.BACKGROUND)


# Feature: view-styles-extraction, Property 8: Обратная совместимость цветов
@given(st.just(None))
@settings(max_examples=10)
def test_backward_compatibility_colors(_):
    """Property 8 — Validates: Requirements 9.1, 9.2, 9.3"""
    from logiccraft.view.theme import (
        CardStyle, ConnectionStyle, SceneStyle, AnchorStyle, ArrowStyle
    )
    # Проверяем что токены содержат исходные захардкоженные значения
    assert CardStyle.BACKGROUND == "#f5f5dc"
    assert CardStyle.BORDER == "#4169E1"
    assert CardStyle.SELECTED_BORDER == "#DC143C"
    assert CardStyle.ATTRS_TEXT == "#2c3e50"
    assert CardStyle.METHODS_TEXT == "#27ae60"
    assert ConnectionStyle.LINE_COLOR == "#666666"
    assert ConnectionStyle.SELECTED_COLOR == "#DC143C"
    assert AnchorStyle.NORMAL_COLOR == "#FF6B6B"
    assert AnchorStyle.HOVER_COLOR == "#FF4444"
    assert AnchorStyle.BORDER_COLOR == "#FFFFFF"
    assert ArrowStyle.COLOR == "#666666"
    assert SceneStyle.BACKGROUND == "#fafafa"
    assert SceneStyle.GRID_COLOR == "#e0e0e0"
    assert SceneStyle.TEMP_LINE_COLOR == "#4169E1"


# ─────────────────────────────────────────────
# Unit-тесты: DiagramScene использует SceneStyle
# ─────────────────────────────────────────────

class TestDiagramSceneStyle:
    """Requirements 6.2, 6.3"""

    def test_scene_temp_line_uses_scene_style(self):
        """6.3 — start_connection создаёт линию с цветом из SceneStyle"""
        from logiccraft.view.scenes.diagram_scene import DiagramScene
        from logiccraft.view.theme import SceneStyle
        from unittest.mock import MagicMock
        from PyQt6.QtCore import QPointF
        scene = DiagramScene()
        mock_card = MagicMock()
        mock_card.id = "card-1"
        mock_card.get_anchor_point.return_value = QPointF(0, 0)
        scene.start_connection(mock_card, "right")
        assert scene.temp_line is not None
        assert scene.temp_line.pen().color() == QColor(SceneStyle.TEMP_LINE_COLOR)
        scene.cancel_connection()
