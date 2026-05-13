"""Виджет мини-карты диаграммы"""
from PyQt6.QtWidgets import QGraphicsView, QWidget
from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtGui import QPainter, QBrush, QColor, QPen


class MiniMapWidget(QGraphicsView):
    """Мини-карта для навигации по большой диаграмме"""
    
    viewport_clicked = pyqtSignal(float, float)  # x, y в координатах сцены
    
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self._main_view = None
        self._viewport_rect = QRectF()
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Настройка UI мини-карты"""
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setInteractive(False)
        self.setFixedSize(200, 150)
        
        # Стиль
        self.setStyleSheet("""
            MiniMapWidget {
                background-color: #F9FAFB;
                border: 2px solid #E5E0F8;
                border-radius: 8px;
            }
        """)
    
    def set_main_view(self, view):
        """Установить главный вид для синхронизации"""
        self._main_view = view
        self._update_viewport_rect()
        self._fit_scene()
    
    def _fit_scene(self):
        """Вписать всю сцену в мини-карту"""
        if self.scene():
            rect = self.scene().itemsBoundingRect()
            if not rect.isEmpty():
                self.fitInView(rect.adjusted(-50, -50, 50, 50), Qt.AspectRatioMode.KeepAspectRatio)
    
    def _update_viewport_rect(self):
        """Обновить прямоугольник видимой области"""
        if not self._main_view:
            return
        
        # Получаем видимую область главного вида в координатах сцены
        visible_rect = self._main_view.mapToScene(self._main_view.viewport().rect()).boundingRect()
        self._viewport_rect = visible_rect
        self.viewport().update()
    
    def update_viewport(self):
        """Обновить отображение видимой области (вызывается извне)"""
        self._update_viewport_rect()
    
    def drawForeground(self, painter, rect):
        """Рисуем прямоугольник видимой области поверх сцены"""
        super().drawForeground(painter, rect)
        
        if not self._viewport_rect.isEmpty():
            # Полупрозрачный синий прямоугольник
            painter.setBrush(QBrush(QColor(124, 58, 237, 50)))  # #7C3AED с прозрачностью
            painter.setPen(QPen(QColor(124, 58, 237), 2))  # #7C3AED
            painter.drawRect(self._viewport_rect)
    
    def mousePressEvent(self, event):
        """Обработка клика - перемещение главного вида"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Преобразуем координаты клика в координаты сцены
            scene_pos = self.mapToScene(event.pos())
            self.viewport_clicked.emit(scene_pos.x(), scene_pos.y())
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Обработка перетаскивания - перемещение главного вида"""
        if event.buttons() & Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            self.viewport_clicked.emit(scene_pos.x(), scene_pos.y())
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def resizeEvent(self, event):
        """При изменении размера - перевписываем сцену"""
        super().resizeEvent(event)
        self._fit_scene()
