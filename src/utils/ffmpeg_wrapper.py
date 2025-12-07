import subprocess
import os
import re

class FFmpegWrapper:
    """Wrapper para ejecutar comandos de FFmpeg"""
    
    @staticmethod
    def get_video_duration(input_file):
        """Obtiene la duración del video en segundos"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                input_file
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            duration = float(result.stdout.strip())
            return duration
        except Exception as e:
            print(f"Error obteniendo duración: {e}")
            return 0
    
    @staticmethod
    def get_video_info(input_file):
        """Obtiene información detallada del video"""
        try:
            cmd = [
                'ffmpeg',
                '-i', input_file,
                '-hide_banner'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return result.stderr
        except Exception as e:
            return f"Error: {str(e)}"
    
    @staticmethod
    def convert_video(input_file, output_file, encoder='libx264', preset='medium', crf=23):
        """Convierte video usando FFmpeg con progreso"""
        try:
            cmd = [
                'ffmpeg',
                '-i', input_file,
                '-c:v', encoder,
                '-preset', preset,
                '-crf', str(crf),
                '-c:a', 'aac',
                '-b:a', '192k',
                '-progress', 'pipe:2',  # Enviar progreso a stderr
                output_file,
                '-y'
            ]
            
            # Si es NVENC, agregar aceleración por hardware
            if 'nvenc' in encoder:
                cmd.insert(1, '-hwaccel')
                cmd.insert(2, 'cuda')
            
            print(f"Comando FFmpeg: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            return process
        except Exception as e:
            print(f"Error en conversión: {e}")
            return None
    
    @staticmethod
    def repair_video(input_file, output_file):
        """Repara video corrupto usando FFmpeg"""
        try:
            cmd = [
                'ffmpeg',
                '-err_detect', 'ignore_err',
                '-i', input_file,
                '-c', 'copy',
                '-progress', 'pipe:2',
                output_file,
                '-y'
            ]
            
            print(f"Comando reparación: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            return process
        except Exception as e:
            print(f"Error en reparación: {e}")
            return None

if __name__ == "__main__":
    wrapper = FFmpegWrapper()
    print("FFmpegWrapper listo")