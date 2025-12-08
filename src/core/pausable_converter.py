"""Módulo para conversión pausable"""
import subprocess
import os
import signal
import platform

class PausableConverter:
    """Conversor de video con capacidad de pausar/reanudar"""
    
    def __init__(self, input_file, output_file, encoder='libx264', preset='medium', crf=23):
        self.input_file = input_file
        self.output_file = output_file
        self.encoder = encoder
        self.preset = preset
        self.crf = crf
        self.process = None
        self.is_paused = False
        self.temp_output = None
    
    def start(self):
        """Inicia la conversión"""
        cmd = [
            'ffmpeg',
            '-i', self.input_file
        ]
        
        if 'nvenc' in self.encoder:
            cmd.extend(['-hwaccel', 'cuda'])
        
        cmd.extend([
            '-c:v', self.encoder,
            '-preset', self.preset,
            '-crf', str(self.crf),
            '-c:a', 'aac',
            '-b:a', '192k',
            '-progress', 'pipe:2',
            self.output_file,
            '-y'
        ])
        
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        return self.process
    
    def pause(self):
        """Pausa la conversión"""
        if self.process and not self.is_paused:
            if platform.system() == 'Windows':
                # En Windows usamos suspend
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.DebugActiveProcess(self.process.pid)
                kernel32.DebugSetProcessKillOnExit(False)
            else:
                # En Unix usamos SIGSTOP
                os.kill(self.process.pid, signal.SIGSTOP)
            
            self.is_paused = True
            return True
        return False
    
    def resume(self):
        """Reanuda la conversión"""
        if self.process and self.is_paused:
            if platform.system() == 'Windows':
                # En Windows usamos resume
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.DebugActiveProcessStop(self.process.pid)
            else:
                # En Unix usamos SIGCONT
                os.kill(self.process.pid, signal.SIGCONT)
            
            self.is_paused = False
            return True
        return False
    
    def stop(self):
        """Detiene la conversión"""
        if self.process:
            self.process.kill()
            self.process = None
            self.is_paused = False
            return True
        return False
    
    def get_status(self):
        """Obtiene el estado actual"""
        if not self.process:
            return 'stopped'
        elif self.is_paused:
            return 'paused'
        else:
            return 'running'