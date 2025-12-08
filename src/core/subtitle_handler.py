"""Módulo para manejo de subtítulos"""
import subprocess
import os

class SubtitleHandler:
    """Maneja subtítulos en videos"""
    
    @staticmethod
    def add_subtitle(input_video, input_subtitle, output_file, encoder='libx264', preset='medium', crf=23):
        """Agrega subtítulo externo al video (soft subtitle)"""
        try:
            cmd = [
                'ffmpeg',
                '-i', input_video,
                '-i', input_subtitle
            ]
            
            if 'nvenc' in encoder:
                cmd.extend(['-hwaccel', 'cuda'])
            
            cmd.extend([
                '-c:v', encoder,
                '-preset', preset,
                '-crf', str(crf),
                '-c:a', 'copy',
                '-c:s', 'mov_text',  # Para MP4
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
            print(f"Error agregando subtítulo: {e}")
            return None
    
    @staticmethod
    def burn_subtitle(input_video, input_subtitle, output_file, encoder='libx264', preset='medium', crf=23):
        """Quema (hardcode) subtítulos en el video"""
        try:
            # Normalizar ruta para filtro de ffmpeg
            subtitle_path = input_subtitle.replace('\\', '/').replace(':', '\\:')
            
            cmd = [
                'ffmpeg',
                '-i', input_video
            ]
            
            if 'nvenc' in encoder:
                cmd.extend(['-hwaccel', 'cuda'])
            
            cmd.extend([
                '-vf', f"subtitles='{subtitle_path}'",
                '-c:v', encoder,
                '-preset', preset,
                '-crf', str(crf),
                '-c:a', 'copy',
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
            print(f"Error quemando subtítulo: {e}")
            return None
    
    @staticmethod
    def extract_subtitle(input_video, output_subtitle, stream_index=0):
        """Extrae subtítulos de un video"""
        try:
            cmd = [
                'ffmpeg',
                '-i', input_video,
                '-map', f'0:s:{stream_index}',
                output_subtitle,
                '-y'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error extrayendo subtítulo: {e}")
            return False
    
    @staticmethod
    def get_subtitle_streams(input_video):
        """Obtiene información de los streams de subtítulos"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 's',
                '-show_entries', 'stream=index,codec_name:stream_tags=language',
                '-of', 'csv=p=0',
                input_video
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            streams = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(',')
                    if len(parts) >= 2:
                        streams.append({
                            'index': parts[0],
                            'codec': parts[1],
                            'language': parts[2] if len(parts) > 2 else 'unknown'
                        })
            
            return streams
            
        except Exception as e:
            print(f"Error obteniendo streams de subtítulos: {e}")
            return []