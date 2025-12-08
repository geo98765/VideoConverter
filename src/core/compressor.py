"""Módulo para compresión inteligente de videos"""
import subprocess
import os

class VideoCompressor:
    """Comprime videos de manera inteligente"""
    
    @staticmethod
    def compress_by_target_size(input_file, output_file, target_size_mb, encoder='libx264', preset='medium'):
        """Comprime un video a un tamaño objetivo específico"""
        try:
            # Obtener duración del video
            duration = VideoCompressor._get_duration(input_file)
            if duration <= 0:
                return None
            
            # Calcular bitrate necesario (en bits por segundo)
            # target_size_mb * 8 * 1024 * 1024 / duration - audio_bitrate
            audio_bitrate = 128 * 1000  # 128 kbps
            target_bytes = target_size_mb * 1024 * 1024
            target_bits = target_bytes * 8
            
            # Restar el bitrate de audio
            video_bitrate = int((target_bits / duration) - audio_bitrate)
            
            # Asegurar bitrate mínimo
            if video_bitrate < 100000:  # 100 kbps mínimo
                video_bitrate = 100000
            
            cmd = [
                'ffmpeg',
                '-i', input_file
            ]
            
            # Agregar aceleración si es NVENC
            if 'nvenc' in encoder:
                cmd.extend(['-hwaccel', 'cuda'])
            
            cmd.extend([
                '-c:v', encoder,
                '-b:v', str(video_bitrate),
                '-preset', preset,
                '-c:a', 'aac',
                '-b:a', '128k',
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
            print(f"Error comprimiendo video: {e}")
            return None
    
    @staticmethod
    def compress_by_percentage(input_file, output_file, percentage, encoder='libx264', preset='medium'):
        """Comprime un video reduciendo el bitrate en un porcentaje"""
        try:
            # Obtener bitrate actual
            current_bitrate = VideoCompressor._get_bitrate(input_file)
            if current_bitrate <= 0:
                return None
            
            # Calcular nuevo bitrate
            new_bitrate = int(current_bitrate * (percentage / 100))
            
            # Asegurar bitrate mínimo
            if new_bitrate < 100000:
                new_bitrate = 100000
            
            cmd = [
                'ffmpeg',
                '-i', input_file
            ]
            
            if 'nvenc' in encoder:
                cmd.extend(['-hwaccel', 'cuda'])
            
            cmd.extend([
                '-c:v', encoder,
                '-b:v', str(new_bitrate),
                '-preset', preset,
                '-c:a', 'aac',
                '-b:a', '128k',
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
            print(f"Error comprimiendo video: {e}")
            return None
    
    @staticmethod
    def _get_duration(input_file):
        """Obtiene la duración del video"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                input_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return float(result.stdout.strip())
        except:
            return 0
    
    @staticmethod
    def _get_bitrate(input_file):
        """Obtiene el bitrate del video"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=bit_rate',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                input_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return int(result.stdout.strip())
        except:
            return 0