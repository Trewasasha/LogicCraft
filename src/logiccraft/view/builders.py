"""Билдеры для создания UI компонентов главного окна"""
from PyQt6.QtWidgets import (
    QMenu, QMenuBar, QToolBar, QLabel, QComboBox, QWidget, 
    QHBoxLayout, QPushButton, QSpinBox
)
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import Qt
from logiccraft.utils.icon_manager import icon_manager


class MenuBarBuilder:
    """Строитель менюбары"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.menubar = None
    
    def build(self) -> QMenuBar:
        """Построить менюбару"""
        self.menubar = self.main_window.menuBar()
        self._build_file_menu()
        self._build_edit_menu()
        self._build_tools_menu()
        return self.menubar
    
    def _build_file_menu(self):
        """Меню File"""
        file_menu = self.menubar.addMenu("&File")
        
        # Save
        save_action = QAction(icon_manager.get_icon("save"), " Save", self.main_window)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.main_window._on_save_clicked)
        file_menu.addAction(save_action)
        
        # Load
        load_action = QAction(icon_manager.get_icon("folder"), " Load", self.main_window)
        load_action.setShortcut(QKeySequence.StandardKey.Open)
        load_action.triggered.connect(self.main_window._on_load_clicked)
        file_menu.addAction(load_action)
    
    def _build_edit_menu(self):
        """Меню Edit"""
        edit_menu = self.menubar.addMenu("&Edit")
        
        # Undo/Redo
        self.main_window.undo_action = QAction(
            icon_manager.get_icon("undo"), " Undo", self.main_window
        )
        self.main_window.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.main_window.undo_action.triggered.connect(self.main_window._on_undo)
        self.main_window.undo_action.setEnabled(False)
        edit_menu.addAction(self.main_window.undo_action)
        
        self.main_window.redo_action = QAction(
            icon_manager.get_icon("redo"), " Redo", self.main_window
        )
        self.main_window.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.main_window.redo_action.triggered.connect(self.main_window._on_redo)
        self.main_window.redo_action.setEnabled(False)
        edit_menu.addAction(self.main_window.redo_action)
        
        edit_menu.addSeparator()
        
        # Copy/Paste/Duplicate
        copy_action = QAction(icon_manager.get_icon("copy"), " Копировать", self.main_window)
        copy_action.setShortcut(QKeySequence("Ctrl+C"))
        copy_action.triggered.connect(self.main_window._on_copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction(icon_manager.get_icon("duplicate"), " Вставить", self.main_window)
        paste_action.setShortcut(QKeySequence("Ctrl+V"))
        paste_action.triggered.connect(self.main_window._on_paste)
        edit_menu.addAction(paste_action)
        
        duplicate_action = QAction(icon_manager.get_icon("duplicate"), " Дублировать", self.main_window)
        duplicate_action.setShortcut(QKeySequence("Ctrl+D"))
        duplicate_action.triggered.connect(self.main_window._on_duplicate)
        edit_menu.addAction(duplicate_action)
        
        # Select All
        select_all_action = QAction(icon_manager.get_icon("copy"), "Выделить всё", self.main_window)
        select_all_action.setShortcut(QKeySequence("Ctrl+A"))
        select_all_action.triggered.connect(self.main_window._on_select_all)
        edit_menu.addAction(select_all_action)
        
        edit_menu.addSeparator()
        
        # Delete
        delete_action = QAction(icon_manager.get_icon("garbage"), " Delete Selected", self.main_window)
        delete_action.setShortcut(QKeySequence("Del"))
        delete_action.triggered.connect(self.main_window._on_delete_selected)
        edit_menu.addAction(delete_action)
        
        edit_menu.addSeparator()
        
        # Clear All
        clear_action = QAction(icon_manager.get_icon("clear"), " Clear All", self.main_window)
        clear_action.triggered.connect(self.main_window._on_clear_clicked)
        edit_menu.addAction(clear_action)
    
    def _build_tools_menu(self):
        """Меню Tools"""
        tools_menu = self.menubar.addMenu("&Tools")
        
        # Search
        search_action = QAction("🔍 Поиск классов...", self.main_window)
        search_action.setShortcut(QKeySequence("Ctrl+F"))
        search_action.triggered.connect(self.main_window._show_search)
        tools_menu.addAction(search_action)
        
        tools_menu.addSeparator()
        
        # Code Generation
        generate_code_action = QAction(
            icon_manager.get_icon("generate"), " Generate Code", self.main_window
        )
        generate_code_action.setShortcut(QKeySequence("Ctrl+G"))
        generate_code_action.triggered.connect(self.main_window._on_generate_code_clicked)
        tools_menu.addAction(generate_code_action)
        
        # Export Project
        export_project_action = QAction(
            icon_manager.get_icon("folder"), " Export Project...", self.main_window
        )
        export_project_action.setShortcut(QKeySequence("Ctrl+E"))
        export_project_action.triggered.connect(self.main_window._on_export_project_clicked)
        tools_menu.addAction(export_project_action)
        
        # Export Image
        export_image_action = QAction("Export Image (PNG/SVG)...", self.main_window)
        export_image_action.setShortcut(QKeySequence("Ctrl+Shift+E"))
        export_image_action.triggered.connect(self.main_window._on_export_image)
        tools_menu.addAction(export_image_action)
        
        tools_menu.addSeparator()
        
        # Validate
        validate_action = QAction("Валидация диаграммы", self.main_window)
        validate_action.setShortcut(QKeySequence("Ctrl+Shift+V"))
        validate_action.triggered.connect(self.main_window._on_validate)
        tools_menu.addAction(validate_action)
        
        tools_menu.addSeparator()
        
        # Align submenu
        self._build_align_submenu(tools_menu)
    
    def _build_align_submenu(self, parent_menu):
        """Подменю выравнивания"""
        align_menu = parent_menu.addMenu("Выравнивание")
        
        align_actions = [
            ("По левому краю", "Ctrl+Shift+Left", self.main_window._align_left),
            ("По правому краю", "Ctrl+Shift+Right", self.main_window._align_right),
            ("По верхнему краю", "Ctrl+Shift+Up", self.main_window._align_top),
            ("По нижнему краю", "Ctrl+Shift+Down", self.main_window._align_bottom),
            ("По центру (гор.)", None, self.main_window._align_center_h),
            ("По центру (верт.)", None, self.main_window._align_center_v),
        ]
        
        for label, shortcut, slot in align_actions:
            action = QAction(label, self.main_window)
            if shortcut:
                action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(slot)
            align_menu.addAction(action)


class ToolBarBuilder:
    """Строитель тулбара"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.toolbar = None
    
    def build(self) -> QToolBar:
        """Построить тулбар"""
        self.toolbar = self.main_window.addToolBar("Main")
        self.toolbar.setMovable(False)
        self.toolbar.setStyleSheet(self._get_toolbar_style())
        
        self._build_diagram_type_selector()
        self._build_tool_buttons()
        
        return self.toolbar
    
    def _get_toolbar_style(self) -> str:
        """Стили для тулбара"""
        return """
            QToolBar {
                background-color: #FFFFFF;
                border-bottom: 1px solid #E5E0F8;
                spacing: 4px;
                padding: 4px 12px;
            }
            QToolButton {
                background-color: transparent;
                color: #1F1F1F;
                border: none;
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 13px;
            }
            QToolButton:hover {
                background-color: #F3EEFF;
                color: #7C3AED;
            }
        """
    
    def _build_diagram_type_selector(self):
        """Переключатель типов диаграмм"""
        diagram_type_label = QLabel("Тип диаграммы:")
        diagram_type_label.setStyleSheet("color: #666; font-size: 12px; padding: 0 8px;")
        self.toolbar.addWidget(diagram_type_label)
        
        self.main_window.diagram_type_combo = QComboBox()
        self.main_window.diagram_type_combo.addItem("📊 Диаграмма классов", "class")
        self.main_window.diagram_type_combo.addItem("👤 Use Case диаграмма", "use_case")
        self.main_window.diagram_type_combo.setCurrentIndex(0)
        self.main_window.diagram_type_combo.setMinimumWidth(200)
        self.main_window.diagram_type_combo.currentIndexChanged.connect(
            self.main_window._on_diagram_type_changed
        )
        self.toolbar.addWidget(self.main_window.diagram_type_combo)
        
        self.toolbar.addSeparator()
    
    def _build_tool_buttons(self):
        """Кнопки инструментов"""
        tool_actions = [
            ("add", "Добавить элемент", self.main_window._on_add_clicked),
            ("edit", "Редактировать", self.main_window._on_edit_selected),
            ("connection", "Связь", lambda: self.main_window.toolbox_panel.set_connection_mode(True)),
            ("rename", "Переименовать", self.main_window._on_rename_selected),
        ]
        
        for icon_name, tooltip, handler in tool_actions:
            btn = self.toolbar.addAction(icon_manager.get_icon(icon_name), tooltip)
            btn.triggered.connect(handler)


class StatusBarBuilder:
    """Строитель статусбара"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.status_bar = None
    
    def build(self):
        """Построить статусбар"""
        self.status_bar = self.main_window.statusBar()
        self.main_window.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.main_window.status_label)
        
        self._build_zoom_controls()
        self._build_stats_label()
        
        return self.status_bar
    
    def _build_zoom_controls(self):
        """Контролы зума"""
        from PyQt6.QtWidgets import QPushButton
        
        zoom_widget = QWidget()
        zoom_layout = QHBoxLayout(zoom_widget)
        zoom_layout.setContentsMargins(0, 0, 8, 0)
        zoom_layout.setSpacing(4)
        
        zoom_out_btn = QPushButton("−")
        zoom_out_btn.setFixedSize(22, 22)
        zoom_out_btn.setObjectName("ZoomButton")
        zoom_out_btn.clicked.connect(lambda: self.main_window.view._zoom_out())
        
        self.main_window.zoom_label = QLabel("100%")
        self.main_window.zoom_label.setObjectName("ZoomLabel")
        self.main_window.zoom_label.setFixedWidth(44)
        
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedSize(22, 22)
        zoom_in_btn.setObjectName("ZoomButton")
        zoom_in_btn.clicked.connect(lambda: self.main_window.view._zoom_in())
        
        fit_btn = QPushButton("⊡")
        fit_btn.setFixedSize(22, 22)
        fit_btn.setObjectName("ZoomButton")
        fit_btn.setToolTip("Вписать в экран")
        fit_btn.clicked.connect(lambda: self.main_window.view.fit_in_view_all())
        
        reset_btn = QPushButton("1:1")
        reset_btn.setFixedSize(28, 22)
        reset_btn.setObjectName("ZoomButton")
        reset_btn.setToolTip("Сбросить масштаб")
        reset_btn.clicked.connect(lambda: self.main_window.view.reset_zoom())
        
        zoom_layout.addWidget(zoom_out_btn)
        zoom_layout.addWidget(self.main_window.zoom_label)
        zoom_layout.addWidget(zoom_in_btn)
        zoom_layout.addWidget(fit_btn)
        zoom_layout.addWidget(reset_btn)
        
        self.main_window.stats_label = QLabel("")
        self.main_window.stats_label.setObjectName("StatusBarStats")
        
        self.status_bar.addPermanentWidget(self.main_window.stats_label)
        self.status_bar.addPermanentWidget(zoom_widget)
