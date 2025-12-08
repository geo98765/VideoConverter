"""Thread para compresión de videos"""
from threads.base_thread import BaseThread
from utils.ffmpeg_wrapper import FFmpegWrapper
from core.compressor import VideoCompressor
import re

class CompressThread(BaseThread):
    """Thread para comprimir videos sin bloquear UI"""
    
    def __init__(self, input_file, output_file, compression_mode, target_value, encoder='libx264', preset='medium'):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.compression_mode = compression_mode  # 'size' o 'percentage'
        self.target_value = target_value
        self.encoder = encoder
        self.preset = preset
    
    def run(self):
        """Ejecuta la compresión"""
        try:
            self.emit_log(f"🗜️ Comprimiendo video...")
            
            if self.compression_mode == 'size':
                self.emit_log(f"   Tamaño objetivo: {self.target_value} MB")
                process = VideoCompressor.compress_by_target_size(
                    self.input_file,
                    self.output_file,
                    self.target_value,
                    self.encoder,
                    self.preset
                )
            else:  # percentage
                self.emit_log(f"   Reducción: {self.target_value}% del tamaño original")
                process = VideoCompressor.compress_by_percentage(
                    self.input_file,
                    self.output_file,
                    self.target_value,
                    self.encoder,
                    self.preset
                )
            
            if not process:
                self.emit_finished(False, "Error al iniciar compresión")
                return
            
            # Obtener duración para progreso
            duration = FFmpegWrapper.get_video_duration(self.input_file)
            
            # Monitorear progreso
            for line in process.stderr:
                if not self.is_running:
                    process.kill()
                    self.emit_finished(False, "Compresión cancelada")
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
                self.emit_finished(True, "✅ Video comprimido exitosamente")
            else:
                self.emit_finished(False, "❌ Error comprimiendo video")
                
        except Exception as e:
            self.emit_finished(False, f"❌ Error: {str(e)}")