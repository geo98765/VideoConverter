"""Thread para manejo de subtítulos"""
from threads.base_thread import BaseThread
from utils.ffmpeg_wrapper import FFmpegWrapper
from core.subtitle_handler import SubtitleHandler
import re

class SubtitleThread(BaseThread):
    """Thread para operaciones con subtítulos sin bloquear UI"""
    
    def __init__(self, operation, input_video, output_file, subtitle_file=None, 
                 encoder='libx264', preset='medium', crf=23):
        super().__init__()
        self.operation = operation  # 'add', 'burn', 'extract'
        self.input_video = input_video
        self.output_file = output_file
        self.subtitle_file = subtitle_file
        self.encoder = encoder
        self.preset = preset
        self.crf = crf
    
    def run(self):
        """Ejecuta la operación con subtítulos"""
        try:
            if self.operation == 'add':
                self.emit_log(f"📝 Agregando subtítulos (soft)...")
                process = SubtitleHandler.add_subtitle(
                    self.input_video,
                    self.subtitle_file,
                    self.output_file,
                    self.encoder,
                    self.preset,
                    self.crf
                )
            elif self.operation == 'burn':
                self.emit_log(f"🔥 Quemando subtítulos (hard)...")
                process = SubtitleHandler.burn_subtitle(
                    self.input_video,
                    self.subtitle_file,
                    self.output_file,
                    self.encoder,
                    self.preset,
                    self.crf
                )
            elif self.operation == 'extract':
                self.emit_log(f"📤 Extrayendo subtítulos...")
                success = SubtitleHandler.extract_subtitle(
                    self.input_video,
                    self.output_file
                )
                if success:
                    self.emit_progress(100)
                    self.emit_finished(True, "✅ Subtítulos extraídos exitosamente")
                else:
                    self.emit_finished(False, "❌ Error extrayendo subtítulos")
                return
            else:
                self.emit_finished(False, "Operación desconocida")
                return
            
            if not process:
                self.emit_finished(False, "Error al iniciar operación")
                return
            
            # Obtener duración para progreso
            duration = FFmpegWrapper.get_video_duration(self.input_video)
            
            # Monitorear progreso
            for line in process.stderr:
                if not self.is_running:
                    process.kill()
                    self.emit_finished(False, "Operación cancelada")
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
                self.emit_finished(True, "✅ Operación completada exitosamente")
            else:
                self.emit_finished(False, "❌ Error en la operación")
                
        except Exception as e:
            self.emit_finished(False, f"❌ Error: {str(e)}")