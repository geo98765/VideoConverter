"""Módulo para análisis detallado de videos"""
import subprocess
import json
import re

class VideoAnalyzer:
    """Analiza videos y extrae información detallada"""
    
    @staticmethod
    def analyze(file_path):
        """Analiza un video y retorna información completa"""
        try:
            # Usar ffprobe para obtener información en JSON
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                file_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return None
            
            data = json.loads(result.stdout)
            return VideoAnalyzer._parse_analysis(data, file_path)
            
        except Exception as e:
            print(f"Error analizando video: {e}")
            return None
    
    @staticmethod
    def _parse_analysis(data, file_path):
        """Parsea la información del análisis"""
        analysis = {
            'file_path': file_path,
            'file_size': 0,
            'duration': 0,
            'bitrate': 0,
            'format_name': '',
            'video_streams': [],
            'audio_streams': [],
            'subtitle_streams': []
        }
        
        # Información del formato
        if 'format' in data:
            fmt = data['format']
            analysis['file_size'] = int(fmt.get('size', 0))
            analysis['duration'] = float(fmt.get('duration', 0))
            analysis['bitrate'] = int(fmt.get('bit_rate', 0))
            analysis['format_name'] = fmt.get('format_name', '')
        
        # Información de streams
        if 'streams' in data:
            for stream in data['streams']:
                codec_type = stream.get('codec_type', '')
                
                if codec_type == 'video':
                    video_info = {
                        'codec': stream.get('codec_name', ''),
                        'codec_long': stream.get('codec_long_name', ''),
                        'width': stream.get('width', 0),
                        'height': stream.get('height', 0),
                        'fps': VideoAnalyzer._parse_fps(stream.get('r_frame_rate', '0/0')),
                        'bitrate': int(stream.get('bit_rate', 0)),
                        'pix_fmt': stream.get('pix_fmt', '')
                    }
                    analysis['video_streams'].append(video_info)
                
                elif codec_type == 'audio':
                    audio_info = {
                        'codec': stream.get('codec_name', ''),
                        'codec_long': stream.get('codec_long_name', ''),
                        'sample_rate': stream.get('sample_rate', ''),
                        'channels': stream.get('channels', 0),
                        'bitrate': int(stream.get('bit_rate', 0))
                    }
                    analysis['audio_streams'].append(audio_info)
                
                elif codec_type == 'subtitle':
                    subtitle_info = {
                        'codec': stream.get('codec_name', ''),
                        'language': stream.get('tags', {}).get('language', 'unknown')
                    }
                    analysis['subtitle_streams'].append(subtitle_info)
        
        return analysis
    
    @staticmethod
    def _parse_fps(fps_string):
        """Parsea el FPS desde formato 'num/den'"""
        try:
            if '/' in fps_string:
                num, den = fps_string.split('/')
                if int(den) == 0:
                    return 0
                return round(int(num) / int(den), 2)
            return float(fps_string)
        except:
            return 0
    
    @staticmethod
    def format_analysis(analysis):
        """Formatea el análisis para mostrar en UI"""
        if not analysis:
            return "No se pudo analizar el video"
        
        text = "=== ANÁLISIS DE VIDEO ===\n\n"
        
        # Información general
        text += f"📁 Archivo: {analysis['file_path']}\n"
        text += f"💾 Tamaño: {analysis['file_size'] / (1024*1024):.2f} MB\n"
        text += f"⏱️ Duración: {analysis['duration']:.2f} segundos ({VideoAnalyzer._format_time(analysis['duration'])})\n"
        text += f"📊 Bitrate total: {analysis['bitrate'] / 1000:.0f} kbps\n"
        text += f"📦 Formato: {analysis['format_name']}\n\n"
        
        # Video streams
        if analysis['video_streams']:
            text += "🎥 VIDEO:\n"
            for i, video in enumerate(analysis['video_streams'], 1):
                text += f"  Stream {i}:\n"
                text += f"    Codec: {video['codec']} ({video['codec_long']})\n"
                text += f"    Resolución: {video['width']}x{video['height']}\n"
                text += f"    FPS: {video['fps']}\n"
                text += f"    Bitrate: {video['bitrate'] / 1000:.0f} kbps\n"
                text += f"    Formato pixel: {video['pix_fmt']}\n"
            text += "\n"
        
        # Audio streams
        if analysis['audio_streams']:
            text += "🔊 AUDIO:\n"
            for i, audio in enumerate(analysis['audio_streams'], 1):
                text += f"  Stream {i}:\n"
                text += f"    Codec: {audio['codec']} ({audio['codec_long']})\n"
                text += f"    Sample rate: {audio['sample_rate']} Hz\n"
                text += f"    Canales: {audio['channels']}\n"
                text += f"    Bitrate: {audio['bitrate'] / 1000:.0f} kbps\n"
            text += "\n"
        
        # Subtitles
        if analysis['subtitle_streams']:
            text += "📝 SUBTÍTULOS:\n"
            for i, sub in enumerate(analysis['subtitle_streams'], 1):
                text += f"  Stream {i}: {sub['codec']} ({sub['language']})\n"
            text += "\n"
        
        return text
    
    @staticmethod
    def _format_time(seconds):
        """Formatea segundos a HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"