"""Thread para extracción de audio"""
from threads.base_thread import BaseThread
from utils.ffmpeg_wrapper import FFmpegWrapper
from core.audio_extractor import AudioExtractor
import re

class AudioExtractThread(BaseThread):
    """Thread para extraer audio sin bloquear UI"""
    
    def __init__(self, input_file, output_file, format='mp3', bitrate='192k'):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.format = format
        self.bitrate = bitrate
    
    def run(self):
        """Ejecuta la extracción"""
        try:
            self.emit_log(f"🎵 Extrayendo audio...")
            self.emit_log(f"   Formato: {self.format}")
            self.emit_log(f"   Bitrate: {self.bitrate}")
            
            # Obtener duración
            duration = FFmpegWrapper.get_video_duration(self.input_file)
            
            # Extraer audio
            process = AudioExtractor.extract(
                self.input_file,
                self.output_file,
                self.format,
                self.bitrate
            )
            
            if not process:
                self.emit_finished(False, "Error al iniciar extracción")
                return
            
            # Monitorear progreso
            for line in process.stderr:
                if not self.is_running:
                    process.kill()
                    self.emit_finished(False, "Extracción cancelada")
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
                self.emit_finished(True, "✅ Audio extraído exitosamente")
            else:
                self.emit_finished(False, "❌ Error extrayendo audio")
                
        except Exception as e:
            self.emit_finished(False, f"❌ Error: {str(e)}")