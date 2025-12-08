"""Thread base para todas las operaciones"""
from PyQt6.QtCore import QThread, pyqtSignal

class BaseThread(QThread):
    """Clase base para todos los threads"""
    
    progress = pyqtSignal(int)
    log_message = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self):
        super().__init__()
        self.is_running = True
    
    def stop(self):
        """Detiene el thread"""
        self.is_running = False
    
    def emit_log(self, message):
        """Emite mensaje de log"""
        self.log_message.emit(message)
    
    def emit_progress(self, value):
        """Emite progreso"""
        self.progress.emit(value)
    
    def emit_finished(self, success, message):
        """Emite señal de finalización"""
        self.finished_signal.emit(success, message)