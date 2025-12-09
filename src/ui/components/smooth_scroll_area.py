
from PyQt6.QtWidgets import QScrollArea
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QWheelEvent

class SmoothScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vertical_scroll_bar = self.verticalScrollBar()
        self.fps = 60
        self.duration = 400
        self.step_ratio = 1.5
        
        self.current_y = 0
        self.target_y = 0
        self._float_y = 0.0
        self._is_auto_scrolling = False # Flag to distinguish auto vs manual
        
        # Timer for animation
        self.scroll_timer = QTimer(self)
        self.scroll_timer.setInterval(1000 // self.fps)
        self.scroll_timer.timeout.connect(self.update_scroll)
        
        # Connect valid signal
        self.vertical_scroll_bar.valueChanged.connect(self.on_value_changed)

    def on_value_changed(self, value):
        """Si el cambio NO fue por el timer, actualizamos el target (Usuario/Manual)"""
        if not self._is_auto_scrolling:
            self.target_y = value
            self._float_y = float(value)
            self.scroll_timer.stop()

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            super().wheelEvent(event)
            return

        # Initialize targets if not moving
        if not self.scroll_timer.isActive():
            self.target_y = self.vertical_scroll_bar.value()
            self._float_y = float(self.target_y)

        # Calculate delta
        delta = event.angleDelta().y()
        
        # We want to scroll roughly 'step' pixels
        step = -delta * self.step_ratio
        
        self.target_y += step
        
        # Clamp target
        min_val = self.vertical_scroll_bar.minimum()
        max_val = self.vertical_scroll_bar.maximum()
        self.target_y = max(min_val, min(self.target_y, max_val))
        
        if not self.scroll_timer.isActive():
            self.scroll_timer.start()
            
        event.accept()

    def update_scroll(self):
        diff = self.target_y - self._float_y
        
        # Finish if close enough
        if abs(diff) < 1.0:
            self._float_y = self.target_y
            self._is_auto_scrolling = True
            self.vertical_scroll_bar.setValue(int(self._float_y))
            self._is_auto_scrolling = False
            self.scroll_timer.stop()
            return
            
        # Move a fraction of the distance
        speed = 0.2
        change = diff * speed
        
        self._float_y += change
        
        # Set flag before setting value to ignore this specific change event
        self._is_auto_scrolling = True
        self.vertical_scroll_bar.setValue(int(self._float_y))
        self._is_auto_scrolling = False
