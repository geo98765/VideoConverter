"""Thread para procesar cola de videos"""
from PyQt6.QtCore import pyqtSignal
from threads.base_thread import BaseThread
from utils.ffmpeg_wrapper import FFmpegWrapper
import os
import re

class QueueProcessorThread(BaseThread):
    """Thread para procesar cola de videos"""
    
    item_finished = pyqtSignal(int, bool, str)  # index, success, message
    all_finished = pyqtSignal(int, int)  # total, successful
    current_file = pyqtSignal(str)  # nombre del archivo actual
    progress_update = pyqtSignal(int, int) # index, percent
    
    def __init__(self, video_files, output_folder, encoder, preset, crf, output_format):
        super().__init__()
        self.video_files = video_files
        self.output_folder = output_folder
        self.encoder = encoder
        self.preset = preset
        self.crf = crf
        self.output_format = output_format
    
    def run(self):
        """Procesa toda la cola"""
        total = len(self.video_files)
        successful = 0
        
        self.emit_log(f"🎬 Iniciando procesamiento de cola: {total} archivos")
        
        for index, video_file in enumerate(self.video_files):
            if not self.is_running:
                self.emit_log("⚠️ Procesamiento de cola cancelado")
                break
            
            filename = video_file.name
            base_name = os.path.splitext(filename)[0]
            
            # Generar nombre de salida único
            if self.output_folder:
                output_dir = self.output_folder
            else:
                output_dir = video_file.directory
                
            output_filename = f"{base_name}_converted.{self.output_format}"
            output_file = os.path.join(output_dir, output_filename)
            
            # Simple uniqueness check
            counter = 1
            while os.path.exists(output_file):
                output_filename = f"{base_name}_converted_{counter}.{self.output_format}"
                output_file = os.path.join(output_dir, output_filename)
                counter += 1
            
            self.current_file.emit(filename)
            self.emit_log(f"\n{'='*50}")
            self.emit_log(f"📹 Procesando [{index+1}/{total}]: {filename} -> {output_filename}")
            
            try:
                # Obtener duración
                duration = FFmpegWrapper.get_video_duration(video_file.path)
                if duration > 0:
                    self.emit_log(f"   Duración: {duration:.2f} segundos")
                
                # Convertir
                process = FFmpegWrapper.convert_video(
                    video_file.path,
                    output_file,
                    self.encoder,
                    self.preset,
                    self.crf
                )
                
                if not process:
                    self.emit_log(f"❌ Error al iniciar conversión de {filename}")
                    self.item_finished.emit(index, False, "Error al iniciar")
                    continue
                
                # Leer progreso
                for line in process.stderr:
                    if not self.is_running:
                        process.kill()
                        break
                    
                    time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
                    if time_match and duration > 0:
                        hours = int(time_match.group(1))
                        minutes = int(time_match.group(2))
                        seconds = float(time_match.group(3))
                        current_time = hours * 3600 + minutes * 60 + seconds
                        
                        progress_percent = int((current_time / duration) * 100)
                        self.emit_progress(min(progress_percent, 100))
                        self.progress_update.emit(index, min(progress_percent, 100))
                
                process.wait()
                
                if process.returncode == 0:
                    self.emit_log(f"✅ {filename} - Conversión exitosa")
                    # Force 100% on success
                    self.emit_progress(100)
                    self.progress_update.emit(index, 100)
                    self.item_finished.emit(index, True, "Exitoso")
                    successful += 1
                else:
                    self.emit_log(f"❌ {filename} - Error en conversión")
                    self.item_finished.emit(index, False, "Error")
                    
            except Exception as e:
                self.emit_log(f"❌ {filename} - Error: {str(e)}")
                self.item_finished.emit(index, False, f"Error: {str(e)}")
            
            self.emit_progress(0)
        
        self.all_finished.emit(total, successful)
        self.emit_log(f"\n{'='*50}")
        self.emit_log(f"🏁 Procesamiento completado: {successful}/{total} exitosos")