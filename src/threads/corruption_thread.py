"""Thread para detección de corrupción"""
from PyQt6.QtCore import pyqtSignal
from threads.base_thread import BaseThread
from core.corruption_detector import CorruptionDetector

class CorruptionThread(BaseThread):
    """Thread para detectar corrupción sin bloquear UI"""
    
    analysis_complete = pyqtSignal(object)  # Envía resultado del análisis
    
    def __init__(self, input_file):
        super().__init__()
        self.input_file = input_file
    
    def run(self):
        """Ejecuta el análisis de corrupción"""
        try:
            self.emit_log(f"🔍 Analizando video en busca de corrupción...")
            self.emit_progress(10)
            
            result = CorruptionDetector.analyze_video(self.input_file)
            
            self.emit_progress(100)
            self.analysis_complete.emit(result)
            self.emit_finished(True, result['message'])
            
        except Exception as e:
            self.emit_finished(False, f"❌ Error: {str(e)}")