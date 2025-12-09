from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication

class ThemeManager(QObject):
    _instance = None
    theme_changed = pyqtSignal(str)  # signal emitting 'dark' or 'light'

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance.current_theme = "dark"  # Default to dark
        return cls._instance

    def __init__(self):
        super().__init__()
    
    def toggle_theme(self):
        if self.current_theme == "dark":
            self.set_theme("light")
        else:
            self.set_theme("dark")

    def set_theme(self, theme_name):
        self.current_theme = theme_name
        self.apply_theme()
        self.theme_changed.emit(theme_name)

    def apply_theme(self):
        app = QApplication.instance()
        if not app:
            return
            
        if self.current_theme == "dark":
            style_file = "src/ui/styles/dark_theme.qss"
        else:
            style_file = "src/ui/styles/light_theme.qss"
            
        try:
            with open(style_file, "r", encoding="utf-8") as f:
                stylesheet = f.read()
                app.setStyleSheet(stylesheet)
                
                # Force update of properties for dynamic widgets
                for widget in app.allWidgets():
                    widget.style().unpolish(widget)
                    widget.style().polish(widget)
                    
        except FileNotFoundError:
            print(f"Error: Theme file {style_file} not found.")
