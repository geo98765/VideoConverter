"""Thread para conversión de videos"""
from threads.base_thread import BaseThread
from utils.ffmpeg_wrapper import FFmpegWrapper
import os
import re

class ConversionThread(BaseThread):
    """Thread para ejecutar conversión sin bloquear la UI"""
    
    def __init__(self, conversion_job):
        super().__init__()
        self.job = conversion_job
    
    def run(self):
        """Ejecuta la conversión"""
        try:
            self.emit_log(f"🎬 Iniciando conversión...")
            self.emit_log(f"   Archivo: {os.path.basename(self.job.input_file.path)}")
            self.emit_log(f"   Codificador: {self.job.encoder}")
            self.emit_log(f"   Preset: {self.job.preset}")
            
            # Obtener duración total del video
            duration = FFmpegWrapper.get_video_duration(self.job.input_file.path)
            if duration > 0:
                self.emit_log(f"   Duración: {duration:.2f} segundos")
            
            # Iniciar conversión
            process = FFmpegWrapper.convert_video(
                self.job.input_file.path,
                self.job.output_file,
                self.job.encoder,
                self.job.preset,
                self.job.crf
            )
            
            if not process:
                self.emit_finished(False, "Error al iniciar FFmpeg")
                return
            
            # Leer progreso
            for line in process.stderr:
                if not self.is_running:
                    process.kill()
                    self.emit_finished(False, "Conversión cancelada")
                    return
                
                # Buscar tiempo actual en la salida de FFmpeg
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
                self.emit_finished(True, "✅ Conversión completada exitosamente")
            else:
                self.emit_finished(False, "❌ Error durante la conversión")
                
        except Exception as e:
            self.emit_finished(False, f"❌ Error: {str(e)}")