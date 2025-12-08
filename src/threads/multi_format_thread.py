"""Thread para conversión a múltiples formatos"""
from PyQt6.QtCore import pyqtSignal
from threads.base_thread import BaseThread
from core.multi_format_converter import MultiFormatConverter
from utils.ffmpeg_wrapper import FFmpegWrapper
import re
import os

class MultiFormatThread(BaseThread):
    """Thread para convertir a múltiples formatos simultáneamente"""
    
    format_progress = pyqtSignal(str, int)  # formato, progreso
    format_finished = pyqtSignal(str, bool, str)  # formato, success, message
    
    def __init__(self, input_file, output_configs, base_output_name=None):
        super().__init__()
        self.input_file = input_file
        self.output_configs = output_configs
        self.base_output_name = base_output_name or os.path.splitext(input_file)[0]
        self.processes = []
    
    def run(self):
        """Ejecuta las conversiones"""
        try:
            self.emit_log(f"🎬 Iniciando conversión a {len(self.output_configs)} formatos...")
            
            # Obtener duración
            duration = FFmpegWrapper.get_video_duration(self.input_file)
            
            # Iniciar todas las conversiones
            self.processes = MultiFormatConverter.convert_to_formats(
                self.input_file,
                self.output_configs,
                self.base_output_name
            )
            
            self.emit_log(f"✅ {len(self.processes)} conversiones iniciadas")
            
            # Monitorear progreso de cada proceso
            active_processes = self.processes.copy()
            
            while active_processes and self.is_running:
                for proc_info in active_processes[:]:
                    process = proc_info['process']
                    format_name = proc_info['config']['format']
                    
                    # Leer una línea
                    try:
                        line = process.stderr.readline()
                        if line:
                            # Buscar progreso
                            time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
                            if time_match and duration > 0:
                                hours = int(time_match.group(1))
                                minutes = int(time_match.group(2))
                                seconds = float(time_match.group(3))
                                current_time = hours * 3600 + minutes * 60 + seconds
                                
                                progress_percent = int((current_time / duration) * 100)
                                self.format_progress.emit(format_name, min(progress_percent, 100))
                    except:
                        pass
                    
                    # Verificar si terminó
                    if process.poll() is not None:
                        if process.returncode == 0:
                            self.format_progress.emit(format_name, 100)
                            self.format_finished.emit(format_name, True, f"✅ {format_name.upper()} completado")
                            self.emit_log(f"✅ Formato {format_name.upper()} completado")
                        else:
                            self.format_finished.emit(format_name, False, f"❌ {format_name.upper()} falló")
                            self.emit_log(f"❌ Formato {format_name.upper()} falló")
                        
                        active_processes.remove(proc_info)
            
            if self.is_running:
                self.emit_progress(100)
                self.emit_finished(True, "✅ Todas las conversiones completadas")
            else:
                # Cancelar procesos restantes
                for proc_info in active_processes:
                    proc_info['process'].kill()
                self.emit_finished(False, "Conversiones canceladas")
                
        except Exception as e:
            self.emit_finished(False, f"❌ Error: {str(e)}")
    
    def stop(self):
        """Detiene todas las conversiones"""
        self.is_running = False
        for proc_info in self.processes:
            try:
                proc_info['process'].kill()
            except:
                pass