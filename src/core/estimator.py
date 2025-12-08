"""Módulo para estimar tiempo y tamaño de conversión"""
import os

class ConversionEstimator:
    """Estima tiempo y tamaño de archivo para conversiones"""
    
    # Velocidades aproximadas de conversión (segundos de video por segundo real)
    # Estos valores son aproximados y dependen del hardware
    SPEED_FACTORS = {
        'libx264': {
            'ultrafast': 2.0,
            'superfast': 1.5,
            'veryfast': 1.2,
            'faster': 1.0,
            'fast': 0.8,
            'medium': 0.6,
            'slow': 0.4,
            'slower': 0.3,
            'veryslow': 0.2
        },
        'h264_nvenc': {
            'p1': 10.0,  # Fastest
            'p2': 8.0,
            'p3': 6.0,
            'p4': 5.0,
            'p5': 4.0,
            'p6': 3.0,
            'p7': 2.5,  # Slowest/best quality
            'default': 5.0
        },
        'hevc_nvenc': {
            'p1': 8.0,
            'p2': 6.0,
            'p3': 5.0,
            'p4': 4.0,
            'p5': 3.0,
            'p6': 2.5,
            'p7': 2.0,
            'default': 4.0
        }
    }
    
    @staticmethod
    def estimate_time(duration, encoder='libx264', preset='medium'):
        """Estima el tiempo de conversión en segundos"""
        try:
            if encoder in ConversionEstimator.SPEED_FACTORS:
                speeds = ConversionEstimator.SPEED_FACTORS[encoder]
                
                # Para NVENC, los presets tienen nombres diferentes
                if 'nvenc' in encoder:
                    speed_factor = speeds.get(preset, speeds.get('default', 4.0))
                else:
                    speed_factor = speeds.get(preset, 0.6)
                
                estimated_seconds = duration / speed_factor
                return estimated_seconds
            
            # Default si no se encuentra el encoder
            return duration / 0.6
            
        except Exception as e:
            print(f"Error estimando tiempo: {e}")
            return duration
    
    @staticmethod
    def estimate_size(duration, bitrate=None, crf=23, resolution=None):
        """Estima el tamaño del archivo de salida en bytes"""
        try:
            # Si no se especifica bitrate, estimarlo basado en CRF y resolución
            if bitrate is None:
                bitrate = ConversionEstimator._estimate_bitrate(crf, resolution)
            
            # Tamaño = (bitrate en bits/segundo * duración en segundos) / 8
            estimated_bytes = (bitrate * duration) / 8
            
            # Agregar overhead del contenedor (aproximadamente 2%)
            estimated_bytes *= 1.02
            
            return int(estimated_bytes)
            
        except Exception as e:
            print(f"Error estimando tamaño: {e}")
            return 0
    
    @staticmethod
    def _estimate_bitrate(crf, resolution):
        """Estima el bitrate basado en CRF y resolución"""
        # Bitrates base por resolución (en bps)
        base_bitrates = {
            (3840, 2160): 20_000_000,  # 4K
            (2560, 1440): 10_000_000,  # 1440p
            (1920, 1080): 5_000_000,   # 1080p
            (1280, 720): 2_500_000,    # 720p
            (854, 480): 1_000_000,     # 480p
            (640, 360): 500_000        # 360p
        }
        
        # Encontrar resolución más cercana
        base_bitrate = 5_000_000  # Default 1080p
        if resolution:
            width, height = resolution
            # Buscar la resolución base más cercana
            min_diff = float('inf')
            for (w, h), br in base_bitrates.items():
                diff = abs(width - w) + abs(height - h)
                if diff < min_diff:
                    min_diff = diff
                    base_bitrate = br
        
        # Ajustar por CRF (menor CRF = mayor bitrate)
        # CRF 23 es el punto de referencia (factor 1.0)
        # Cada 6 unidades de CRF duplica o reduce a la mitad el bitrate
        crf_factor = 2 ** ((23 - crf) / 6)
        
        estimated_bitrate = base_bitrate * crf_factor
        
        return int(estimated_bitrate)
    
    @staticmethod
    def format_time(seconds):
        """Formatea segundos a formato legible"""
        if seconds < 60:
            return f"{int(seconds)} segundos"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
    
    @staticmethod
    def format_size(bytes_size):
        """Formatea bytes a formato legible"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} PB"