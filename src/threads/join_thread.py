"""Thread para unir videos"""
from PyQt6.QtCore import pyqtSignal
from threads.base_thread import BaseThread
from utils.ffmpeg_wrapper import FFmpegWrapper
from core.video_joiner import VideoJoiner
import re
import os

class JoinThread(BaseThread):
    """Thread para unir videos sin bloquear UI"""
    
    def __init__(self, input_files, output_file, encoder='libx264', preset='medium', crf=23):
        super().__init__()
        self.input_files = input_files
        self.output_file = output_file
        self.encoder = encoder
        self.preset = preset
        self.crf = crf
        self.temp_list_file = None
    
    def run(self):
        """Ejecuta la unión"""
        try:
            self.emit_log(f"🔗 Uniendo {len(self.input_files)} videos...")
            
            # Verificar compatibilidad
            compatible, message = VideoJoiner.check_compatibility(self.input_files)
            if not compatible:
                self.emit_finished(False, f"❌ Videos incompatibles: {message}")
                return
            
            self.emit_log(f"✅ {message}")
            
            # Unir videos
            process, self.temp_list_file = VideoJoiner.join_videos(
                self.input_files,
                self.output_file,
                self.encoder,
                self.preset,
                self.crf
            )
            
            if not process:
                self.emit_finished(False, "Error al iniciar unión")
                return
            
            # Calcular duración total aproximada
            total_duration = sum(FFmpegWrapper.get_video_duration(f) for f in self.input_files)
            
            # Monitorear progreso
            for line in process.stderr:
                if not self.is_running:
                    process.kill()
                    self._cleanup()
                    self.emit_finished(False, "Unión cancelada")
                    return
                
                time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
                if time_match and total_duration > 0:
                    hours = int(time_match.group(1))
                    minutes = int(time_match.group(2))
                    seconds = float(time_match.group(3))
                    current_time = hours * 3600 + minutes * 60 + seconds
                    
                    progress_percent = int((current_time / total_duration) * 100)
                    self.emit_progress(min(progress_percent, 100))
            
            process.wait()
            
            self._cleanup()
            
            if process.returncode == 0:
                self.emit_progress(100)
                self.emit_finished(True, "✅ Videos unidos exitosamente")
            else:
                self.emit_finished(False, "❌ Error uniendo videos")
                
        except Exception as e:
            self._cleanup()
            self.emit_finished(False, f"❌ Error: {str(e)}")
    
    def _cleanup(self):
        """Limpia archivos temporales"""
        if self.temp_list_file and os.path.exists(self.temp_list_file):
            try:
                os.remove(self.temp_list_file)
            except:
                pass