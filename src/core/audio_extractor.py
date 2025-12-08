"""Módulo para extraer audio de videos"""
import subprocess
import os

class AudioExtractor:
    """Extrae audio de archivos de video"""
    
    SUPPORTED_FORMATS = ['mp3', 'aac', 'wav', 'flac', 'ogg', 'm4a']
    
    @staticmethod
    def extract(input_file, output_file, format='mp3', bitrate='192k'):
        """Extrae audio del video"""
        try:
            cmd = [
                'ffmpeg',
                '-i', input_file,
                '-vn',  # No video
                '-progress', 'pipe:2'
            ]
            
            # Configuración específica por formato
            if format == 'mp3':
                cmd.extend(['-codec:a', 'libmp3lame', '-b:a', bitrate])
            elif format == 'aac':
                cmd.extend(['-codec:a', 'aac', '-b:a', bitrate])
            elif format == 'wav':
                cmd.extend(['-codec:a', 'pcm_s16le'])
            elif format == 'flac':
                cmd.extend(['-codec:a', 'flac'])
            elif format == 'ogg':
                cmd.extend(['-codec:a', 'libvorbis', '-b:a', bitrate])
            elif format == 'm4a':
                cmd.extend(['-codec:a', 'aac', '-b:a', bitrate])
            
            cmd.extend([output_file, '-y'])
            
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
            print(f"Error extrayendo audio: {e}")
            return None
    
    @staticmethod
    def get_audio_info(input_file):
        """Obtiene información del audio en el video"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'a:0',
                '-show_entries', 'stream=codec_name,sample_rate,channels,bit_rate',
                '-of', 'default=noprint_wrappers=1',
                input_file
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return result.stdout
            
        except Exception as e:
            print(f"Error obteniendo info de audio: {e}")
            return None