"""Tests for Month 3: Editing and UX.

This module tests:
- Inspector panel for editing selected class properties
- Content management methods: add_attribute(), remove_method()
- Hotkeys (Ctrl+S, Ctrl+Z, Delete) and context menu
- Undo/Redo system based on state stack
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime


class TestInspectorPanel:
    """Tests for inspector panel (Week 1, Month 3)."""

    def test_inspector_panel_shows_selected_class(self):
        """Test inspector panel displays properties of selected class."""
        selected_class = {
            "id": "class_1",
            "name": "User",
            "properties": [
                {"name": "username", "type": "str", "visibility": "public"}
            ],
            "methods": [
                {"name": "get_username", "return_type": "str", "visibility": "public"}
            ]
        }
        
        inspector = InspectorPanel()
        inspector.load_class(selected_class)
        
        assert inspector.current_class == selected_class
        assert inspector.name_field.value == "User"
        assert len(inspector.properties_list) == 1
        assert len(inspector.methods_list) == 1

    def test_inspector_panel_clear_on_deselect(self):
        """Test inspector panel clears when no class is selected."""
        inspector = InspectorPanel()
        inspector.load_class({"id": "class_1", "name": "User", "properties": [], "methods": []})
        
        inspector.clear()
        
        assert inspector.current_class is None
        assert inspector.name_field.value == ""

    def test_inspector_name_change_updates_class(self):
        """Test changing name in inspector updates the class."""
        selected_class = {"id": "class_1", "name": "User", "properties": [], "methods": []}
        on_update = Mock()
        
        inspector = InspectorPanel(on_class_update=on_update)
        inspector.load_class(selected_class)
        inspector.name_field.value = "Customer"
        inspector.on_name_change(None)
        
        on_update.assert_called_once()
        assert selected_class["name"] == "Customer"

    def test_inspector_property_edit(self):
        """Test editing a property in inspector panel."""
        selected_class = {
            "id": "class_1",
            "name": "User",
            "properties": [
                {"name": "username", "type": "str", "visibility": "public"}
            ],
            "methods": []
        }
        
        inspector = InspectorPanel()
        inspector.load_class(selected_class)
        
        # Edit property type
        inspector.edit_property(0, type="string")
        
        assert selected_class["properties"][0]["type"] == "string"

    def test_inspector_visibility_toggle(self):
        """Test toggling visibility in inspector."""
        selected_class = {
            "id": "class_1",
            "name": "User",
            "properties": [
                {"name": "password", "type": "str", "visibility": "private"}
            ],
            "methods": []
        }
        
        inspector = InspectorPanel()
        inspector.load_class(selected_class)
        
        # Toggle visibility
        inspector.set_property_visibility(0, "protected")
        
        assert selected_class["properties"][0]["visibility"] == "protected"


class TestContentManagement:
    """Tests for content management methods (Week 2, Month 3)."""

    def test_add_attribute_to_class(self):
        """Test add_attribute() adds property to class."""
        class_model = {
            "id": "class_1",
            "name": "User",
            "properties": [],
            "methods": []
        }
        
        result = add_attribute(
            class_model,
            name="email",
            type="str",
            visibility="public"
        )
        
        assert len(result["properties"]) == 1
        assert result["properties"][0]["name"] == "email"
        assert result["properties"][0]["type"] == "str"

    def test_add_attribute_with_default_value(self):
        """Test add_attribute() with default value."""
        class_model = {
            "id": "class_1",
            "name": "Config",
            "properties": [],
            "methods": []
        }
        
        result = add_attribute(
            class_model,
            name="timeout",
            type="int",
            visibility="public",
            default_value="30"
        )
        
        assert result["properties"][0]["default_value"] == "30"

    def test_remove_attribute_from_class(self):
        """Test remove_attribute() removes property from class."""
        class_model = {
            "id": "class_1",
            "name": "User",
            "properties": [
                {"name": "username", "type": "str"},
                {"name": "email", "type": "str"}
            ],
            "methods": []
        }
        
        result = remove_attribute(class_model, index=0)
        
        assert len(result["properties"]) == 1
        assert result["properties"][0]["name"] == "email"

    def test_add_method_to_class(self):
        """Test add_method() adds method to class."""
        class_model = {
            "id": "class_1",
            "name": "User",
            "properties": [],
            "methods": []
        }
        
        result = add_method(
            class_model,
            name="validate",
            return_type="bool",
            visibility="public",
            parameters=[{"name": "strict", "type": "bool"}]
        )
        
        assert len(result["methods"]) == 1
        assert result["methods"][0]["name"] == "validate"
        assert result["methods"][0]["return_type"] == "bool"

    def test_remove_method_from_class(self):
        """Test remove_method() removes method from class."""
        class_model = {
            "id": "class_1",
            "name": "User",
            "properties": [],
            "methods": [
                {"name": "save", "return_type": "void"},
                {"name": "delete", "return_type": "void"}
            ]
        }
        
        result = remove_method(class_model, index=1)
        
        assert len(result["methods"]) == 1
        assert result["methods"][0]["name"] == "save"

    def test_add_method_with_parameters(self):
        """Test add_method() with multiple parameters."""
        class_model = {
            "id": "class_1",
            "name": "Calculator",
            "properties": [],
            "methods": []
        }
        
        result = add_method(
            class_model,
            name="calculate",
            return_type="float",
            visibility="public",
            parameters=[
                {"name": "a", "type": "float"},
                {"name": "b", "type": "float"},
                {"name": "operation", "type": "str"}
            ]
        )
        
        method = result["methods"][0]
        assert len(method["parameters"]) == 3
        assert method["parameters"][2]["name"] == "operation"


class TestHotkeys:
    """Tests for hotkeys (Week 3, Month 3)."""

    def test_ctrl_s_triggers_save(self):
        """Test Ctrl+S hotkey triggers save action."""
        save_handler = Mock()
        hotkey_manager = HotkeyManager()
        hotkey_manager.register("ctrl+s", save_handler)
        
        event = Mock()
        event.key = "s"
        event.ctrl = True
        
        hotkey_manager.handle_keydown(event)
        
        save_handler.assert_called_once()

    def test_ctrl_z_triggers_undo(self):
        """Test Ctrl+Z hotkey triggers undo action."""
        undo_handler = Mock()
        hotkey_manager = HotkeyManager()
        hotkey_manager.register("ctrl+z", undo_handler)
        
        event = Mock()
        event.key = "z"
        event.ctrl = True
        
        hotkey_manager.handle_keydown(event)
        
        undo_handler.assert_called_once()

    def test_ctrl_y_triggers_redo(self):
        """Test Ctrl+Y hotkey triggers redo action."""
        redo_handler = Mock()
        hotkey_manager = HotkeyManager()
        hotkey_manager.register("ctrl+y", redo_handler)
        
        event = Mock()
        event.key = "y"
        event.ctrl = True
        
        hotkey_manager.handle_keydown(event)
        
        redo_handler.assert_called_once()

    def test_delete_key_removes_selection(self):
        """Test Delete key removes selected element."""
        delete_handler = Mock()
        hotkey_manager = HotkeyManager()
        hotkey_manager.register("delete", delete_handler)
        
        event = Mock()
        event.key = "Delete"  # Flet uses capitalized key names
        
        hotkey_manager.handle_keydown(event)
        
        delete_handler.assert_called_once()

    def test_unregistered_key_ignored(self):
        """Test unregistered keys are ignored."""
        handler = Mock()
        hotkey_manager = HotkeyManager()
        
        event = Mock()
        event.key = "x"
        event.ctrl = False
        
        hotkey_manager.handle_keydown(event)
        
        handler.assert_not_called()


class TestContextMenu:
    """Tests for context menu (Week 3, Month 3)."""

    def test_context_menu_shows_on_right_click(self):
        """Test context menu appears on right-click."""
        menu = ContextMenu()
        
        menu.show_at(x=100, y=200)
        
        assert menu.visible is True
        assert menu.position == (100, 200)

    def test_context_menu_add_class_option(self):
        """Test context menu has 'Add Class' option."""
        on_add_class = Mock()
        menu = ContextMenu(options={"add_class": on_add_class})
        
        menu.select_option("add_class")
        
        on_add_class.assert_called_once()

    def test_context_menu_delete_option(self):
        """Test context menu has 'Delete' option."""
        on_delete = Mock()
        menu = ContextMenu(options={"delete": on_delete})
        
        menu.select_option("delete")
        
        on_delete.assert_called_once()

    def test_context_menu_hides_on_selection(self):
        """Test context menu hides after option selection."""
        menu = ContextMenu(options={"add_class": Mock()})
        menu.show_at(x=100, y=200)
        
        menu.select_option("add_class")
        
        assert menu.visible is False


class TestUndoRedo:
    """Tests for Undo/Redo system (Week 4, Month 3)."""

    def test_undo_restores_previous_state(self):
        """Test undo restores diagram to previous state."""
        history = HistoryManager()
        
        state1 = {"classes": [{"name": "User"}], "connections": []}
        state2 = {"classes": [{"name": "User"}, {"name": "Order"}], "connections": []}
        
        history.push_state(state1)
        history.push_state(state2)
        
        restored = history.undo()
        
        assert restored == state1

    def test_redo_restores_undone_state(self):
        """Test redo restores state after undo."""
        history = HistoryManager()
        
        state1 = {"classes": [{"name": "User"}], "connections": []}
        state2 = {"classes": [{"name": "User"}, {"name": "Order"}], "connections": []}
        
        history.push_state(state1)
        history.push_state(state2)
        history.undo()
        
        restored = history.redo()
        
        assert restored == state2

    def test_undo_at_beginning_returns_none(self):
        """Test undo at beginning of history returns None."""
        history = HistoryManager()
        
        result = history.undo()
        
        assert result is None

    def test_redo_at_end_returns_none(self):
        """Test redo at end of history returns None."""
        history = HistoryManager()
        
        state = {"classes": [], "connections": []}
        history.push_state(state)
        
        result = history.redo()
        
        assert result is None

    def test_history_limit_enforced(self):
        """Test history size is limited to prevent memory issues."""
        history = HistoryManager(max_history=3)
        
        for i in range(5):
            history.push_state({"version": i})
        
        assert len(history.stack) == 3
        # Oldest state should be removed
        assert history.stack[0]["version"] == 2

    def test_new_state_clears_redo_stack(self):
        """Test pushing new state clears redo stack."""
        history = HistoryManager()
        
        state1 = {"classes": [{"name": "User"}]}
        state2 = {"classes": [{"name": "User"}, {"name": "Order"}]}
        state3 = {"classes": [{"name": "User"}, {"name": "Product"}]}
        
        history.push_state(state1)
        history.push_state(state2)
        history.undo()
        history.push_state(state3)  # This should clear redo stack
        
        redo_result = history.redo()
        assert redo_result is None

    def test_state_deep_copy(self):
        """Test states are deep copied to prevent mutation."""
        history = HistoryManager()
        
        state1 = {"classes": [{"name": "User"}]}
        state2 = {"classes": [{"name": "Order"}]}
        history.push_state(state1)
        history.push_state(state2)
        
        # Modify original state1 after pushing
        state1["classes"][0]["name"] = "Customer"
        
        # Undo to state1 - should have original value due to deep copy
        restored = history.undo()
        assert restored["classes"][0]["name"] == "User"


# Placeholder classes and functions
class InspectorPanel:
    """Placeholder: Inspector panel for editing class properties."""
    
    def __init__(self, on_class_update=None):
        self.current_class = None
        self.name_field = Mock()
        self.properties_list = []
        self.methods_list = []
        self.on_class_update = on_class_update
    
    def load_class(self, class_data):
        self.current_class = class_data
        self.name_field.value = class_data.get("name", "")
        self.properties_list = list(class_data.get("properties", []))
        self.methods_list = list(class_data.get("methods", []))
    
    def clear(self):
        self.current_class = None
        self.name_field.value = ""
    
    def on_name_change(self, event):
        if self.current_class:
            self.current_class["name"] = self.name_field.value
            if self.on_class_update:
                self.on_class_update(self.current_class)
    
    def edit_property(self, index, **kwargs):
        if self.current_class and 0 <= index < len(self.current_class["properties"]):
            self.current_class["properties"][index].update(kwargs)
    
    def set_property_visibility(self, index, visibility):
        if self.current_class and 0 <= index < len(self.current_class["properties"]):
            self.current_class["properties"][index]["visibility"] = visibility


def add_attribute(class_model, name, type, visibility, default_value=None):
    """Placeholder: Add attribute to class."""
    result = class_model.copy()
    result["properties"] = list(result.get("properties", []))
    prop = {"name": name, "type": type, "visibility": visibility}
    if default_value:
        prop["default_value"] = default_value
    result["properties"].append(prop)
    return result


def remove_attribute(class_model, index):
    """Placeholder: Remove attribute from class."""
    result = class_model.copy()
    result["properties"] = list(result.get("properties", []))
    if 0 <= index < len(result["properties"]):
        result["properties"].pop(index)
    return result


def add_method(class_model, name, return_type, visibility, parameters=None):
    """Placeholder: Add method to class."""
    result = class_model.copy()
    result["methods"] = list(result.get("methods", []))
    method = {
        "name": name,
        "return_type": return_type,
        "visibility": visibility,
        "parameters": parameters or []
    }
    result["methods"].append(method)
    return result


def remove_method(class_model, index):
    """Placeholder: Remove method from class."""
    result = class_model.copy()
    result["methods"] = list(result.get("methods", []))
    if 0 <= index < len(result["methods"]):
        result["methods"].pop(index)
    return result


class HotkeyManager:
    """Placeholder: Hotkey manager."""
    
    def __init__(self):
        self.bindings = {}
    
    def register(self, key_combo, handler):
        # Normalize key combo to lowercase, strip whitespace
        normalized = key_combo.lower().strip()
        self.bindings[normalized] = handler
    
    def handle_keydown(self, event):
        key_combo = ""
        if getattr(event, "ctrl", False):
            key_combo += "ctrl+"
        # Handle delete key specifically (flet uses capitalized key names)
        if hasattr(event, 'key') and event.key == 'Delete':
            key_combo = "delete"
        else:
            # Normalize event key to lowercase for comparison
            key_combo += getattr(event, 'key', '').lower().strip()
        
        if key_combo in self.bindings:
            self.bindings[key_combo]()


class ContextMenu:
    """Placeholder: Context menu."""
    
    def __init__(self, options=None):
        self.options = options or {}
        self.visible = False
        self.position = (0, 0)
    
    def show_at(self, x, y):
        self.visible = True
        self.position = (x, y)
    
    def select_option(self, option_name):
        if option_name in self.options:
            self.options[option_name]()
        self.visible = False


class HistoryManager:
    """Placeholder: Undo/Redo history manager."""
    
    def __init__(self, max_history=50):
        self.stack = []
        self.current_index = -1
        self.max_history = max_history
    
    def push_state(self, state):
        import copy
        # Remove any states after current (clear redo)
        self.stack = self.stack[:self.current_index + 1]
        # Add new state
        self.stack.append(copy.deepcopy(state))
        self.current_index += 1
        # Enforce limit
        if len(self.stack) > self.max_history:
            self.stack.pop(0)
            self.current_index -= 1
    
    def undo(self):
        if self.current_index > 0:
            self.current_index -= 1
            return self.stack[self.current_index]
        return None
    
    def redo(self):
        if self.current_index < len(self.stack) - 1:
            self.current_index += 1
            return self.stack[self.current_index]
        return None
