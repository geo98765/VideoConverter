"""Módulo para cambiar resolución de videos"""
import subprocess

class ResolutionChanger:
    """Cambia la resolución de videos"""
    
    COMMON_RESOLUTIONS = {
        '4K': (3840, 2160),
        '1440p': (2560, 1440),
        '1080p': (1920, 1080),
        '720p': (1280, 720),
        '480p': (854, 480),
        '360p': (640, 360)
    }
    
    @staticmethod
    def change_resolution(input_file, output_file, width, height, encoder='libx264', 
                         preset='medium', crf=23, maintain_aspect=True):
        """Cambia la resolución del video"""
        try:
            cmd = [
                'ffmpeg',
                '-i', input_file
            ]
            
            # Agregar aceleración por hardware si es NVENC
            if 'nvenc' in encoder:
                cmd.extend(['-hwaccel', 'cuda'])
            
            # Filtro de escala
            if maintain_aspect:
                # Mantener aspect ratio, escalar al ancho especificado
                scale_filter = f"scale={width}:-2"
            else:
                # Escalar a dimensiones exactas
                scale_filter = f"scale={width}:{height}"
            
            cmd.extend([
                '-vf', scale_filter,
                '-c:v', encoder,
                '-preset', preset,
                '-crf', str(crf),
                '-c:a', 'copy',  # Copiar audio sin re-encodear
                '-progress', 'pipe:2',
                output_file,
                '-y'
            ])
            
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
            print(f"Error cambiando resolución: {e}")
            return None
    
    @staticmethod
    def get_current_resolution(input_file):
        """Obtiene la resolución actual del video"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height',
                '-of', 'csv=p=0',
                input_file
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                width, height = result.stdout.strip().split(',')
                return int(width), int(height)
            
            return None, None
            
        except Exception as e:
            print(f"Error obteniendo resolución: {e}")
            return None, None