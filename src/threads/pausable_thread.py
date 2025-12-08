"""Thread para conversión pausable"""
from PyQt6.QtCore import pyqtSignal
from threads.base_thread import BaseThread
from core.pausable_converter import PausableConverter
from utils.ffmpeg_wrapper import FFmpegWrapper
import re

class PausableConversionThread(BaseThread):
    """Thread para conversión con pausa/reanudación"""
    
    status_changed = pyqtSignal(str)  # 'running', 'paused', 'stopped'
    
    def __init__(self, input_file, output_file, encoder='libx264', preset='medium', crf=23):
        super().__init__()
        self.converter = PausableConverter(input_file, output_file, encoder, preset, crf)
        self.input_file = input_file
    
    def run(self):
        """Ejecuta la conversión"""
        try:
            self.emit_log(f"🎬 Iniciando conversión pausable...")
            
            # Obtener duración
            duration = FFmpegWrapper.get_video_duration(self.input_file)
            
            # Iniciar conversión
            process = self.converter.start()
            self.status_changed.emit('running')
            
            if not process:
                self.emit_finished(False, "Error al iniciar conversión")
                return
            
            # Monitorear progreso
            for line in process.stderr:
                if not self.is_running:
                    self.converter.stop()
                    self.emit_finished(False, "Conversión cancelada")
                    return
                
                # Verificar si está pausado (el proceso sigue pero no avanza)
                if self.converter.is_paused:
                    continue
                
                # Buscar tiempo actual
                time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
                if time_match and duration > 0:
                    hours = int(time_match.group(1))
                    minutes = int(time_match.group(2))
                    seconds = float(time_match.group(3))
                    current_time = hours * 3600 + minutes * 60 + seconds
                    
                    progress_percent = int((current_time / duration) * 100)
                    self.emit_progress(min(progress_percent, 100))
            
            process.wait()
            
            if process.returncode == 0:
                self.emit_progress(100)
                self.status_changed.emit('stopped')
                self.emit_finished(True, "✅ Conversión completada exitosamente")
            else:
                self.status_changed.emit('stopped')
                self.emit_finished(False, "❌ Error durante la conversión")
                
        except Exception as e:
            self.status_changed.emit('stopped')
            self.emit_finished(False, f"❌ Error: {str(e)}")
    
    def pause_conversion(self):
        """Pausa la conversión"""
        if self.converter.pause():
            self.status_changed.emit('paused')
            self.emit_log("⏸️ Conversión pausada")
            return True
        return False
    
    def resume_conversion(self):
        """Reanuda la conversión"""
        if self.converter.resume():
            self.status_changed.emit('running')
            self.emit_log("▶️ Conversión reanudada")
            return True
        return False
    
    def stop(self):
        """Detiene la conversión"""
        self.is_running = False
        self.converter.stop()