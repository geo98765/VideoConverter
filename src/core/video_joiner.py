"""Módulo para unir múltiples videos"""
import subprocess
import os
import tempfile

class VideoJoiner:
    """Une múltiples videos en uno solo"""
    
    @staticmethod
    def join_videos(input_files, output_file, encoder='libx264', preset='medium', crf=23):
        """Une múltiples videos en uno solo"""
        try:
            # Crear archivo de lista temporal
            list_file = VideoJoiner._create_concat_list(input_files)
            
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file
            ]
            
            if 'nvenc' in encoder:
                cmd.extend(['-hwaccel', 'cuda'])
            
            cmd.extend([
                '-c:v', encoder,
                '-preset', preset,
                '-crf', str(crf),
                '-c:a', 'aac',
                '-b:a', '192k',
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
            
            return process, list_file
            
        except Exception as e:
            print(f"Error uniendo videos: {e}")
            return None, None
    
    @staticmethod
    def _create_concat_list(input_files):
        """Crea archivo de lista para concatenación"""
        # Crear archivo temporal
        fd, list_file = tempfile.mkstemp(suffix='.txt', text=True)
        
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            for file_path in input_files:
                # Escapar caracteres especiales y usar comillas
                escaped_path = file_path.replace('\\', '/').replace("'", "'\\''")
                f.write(f"file '{escaped_path}'\n")
        
        return list_file
    
    @staticmethod
    def check_compatibility(input_files):
        """Verifica si los videos son compatibles para unir"""
        if not input_files or len(input_files) < 2:
            return False, "Se necesitan al menos 2 videos"
        
        # Obtener información del primer video
        first_info = VideoJoiner._get_video_info(input_files[0])
        if not first_info:
            return False, "No se pudo leer el primer video"
        
        # Comparar con los demás
        for i, file in enumerate(input_files[1:], 2):
            info = VideoJoiner._get_video_info(file)
            if not info:
                return False, f"No se pudo leer el video {i}"
            
            # Verificar dimensiones
            if info['width'] != first_info['width'] or info['height'] != first_info['height']:
                return False, f"Video {i} tiene diferente resolución"
            
            # Verificar FPS (con tolerancia)
            if abs(info['fps'] - first_info['fps']) > 1:
                return False, f"Video {i} tiene diferente FPS"
        
        return True, "Videos compatibles"
    
    @staticmethod
    def _get_video_info(file_path):
        """Obtiene información básica del video"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height,r_frame_rate',
                '-of', 'csv=p=0',
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            parts = result.stdout.strip().split(',')
            
            if len(parts) >= 3:
                width = int(parts[0])
                height = int(parts[1])
                fps_str = parts[2]
                
                # Parse FPS
                if '/' in fps_str:
                    num, den = fps_str.split('/')
                    fps = float(num) / float(den)
                else:
                    fps = float(fps_str)
                
                return {'width': width, 'height': height, 'fps': fps}
            
            return None
        except:
            return None