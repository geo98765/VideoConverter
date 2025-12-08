"""Thread para cambio de resolución"""
from threads.base_thread import BaseThread
from utils.ffmpeg_wrapper import FFmpegWrapper
from core.resolution_changer import ResolutionChanger
import re

class ResolutionThread(BaseThread):
    """Thread para cambiar resolución sin bloquear UI"""
    
    def __init__(self, input_file, output_file, width, height, encoder='libx264', 
                 preset='medium', crf=23, maintain_aspect=True):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.width = width
        self.height = height
        self.encoder = encoder
        self.preset = preset
        self.crf = crf
        self.maintain_aspect = maintain_aspect
    
    def run(self):
        """Ejecuta el cambio de resolución"""
        try:
            self.emit_log(f"📐 Cambiando resolución...")
            self.emit_log(f"   Nueva resolución: {self.width}x{self.height}")
            self.emit_log(f"   Mantener aspecto: {'Sí' if self.maintain_aspect else 'No'}")
            
            # Obtener duración
            duration = FFmpegWrapper.get_video_duration(self.input_file)
            
            # Cambiar resolución
            process = ResolutionChanger.change_resolution(
                self.input_file,
                self.output_file,
                self.width,
                self.height,
                self.encoder,
                self.preset,
                self.crf,
                self.maintain_aspect
            )
            
            if not process:
                self.emit_finished(False, "Error al iniciar cambio de resolución")
                return
            
            # Monitorear progreso
            for line in process.stderr:
                if not self.is_running:
                    process.kill()
                    self.emit_finished(False, "Cambio de resolución cancelado")
                    return
                
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
                self.emit_finished(True, "✅ Resolución cambiada exitosamente")
            else:
                self.emit_finished(False, "❌ Error cambiando resolución")
                
        except Exception as e:
            self.emit_finished(False, f"❌ Error: {str(e)}")