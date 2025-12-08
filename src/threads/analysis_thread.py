"""Thread para análisis de videos"""
from PyQt6.QtCore import pyqtSignal
from threads.base_thread import BaseThread
from core.analyzer import VideoAnalyzer

class AnalysisThread(BaseThread):
    """Thread para analizar videos sin bloquear UI"""
    
    analysis_complete = pyqtSignal(object)  # Envía el análisis completo
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        """Ejecuta el análisis"""
        try:
            self.emit_log(f"🔍 Analizando: {self.file_path}")
            self.emit_progress(10)
            
            analysis = VideoAnalyzer.analyze(self.file_path)
            
            self.emit_progress(90)
            
            if analysis:
                self.emit_progress(100)
                self.analysis_complete.emit(analysis)
                self.emit_finished(True, "✅ Análisis completado")
            else:
                self.emit_finished(False, "❌ Error en el análisis")
                
        except Exception as e:
            self.emit_finished(False, f"❌ Error: {str(e)}")