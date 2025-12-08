"""Módulo para convertir a múltiples formatos simultáneamente"""
import subprocess
import os
from threading import Thread

class MultiFormatConverter:
    """Convierte un video a múltiples formatos al mismo tiempo"""
    
    @staticmethod
    def convert_to_formats(input_file, output_configs, base_output_name=None):
        """
        Convierte a múltiples formatos
        output_configs: lista de diccionarios con configuración de cada formato
        Ejemplo: [
            {'format': 'mp4', 'encoder': 'libx264', 'crf': 23, 'preset': 'medium'},
            {'format': 'webm', 'encoder': 'libvpx-vp9', 'crf': 30, 'preset': 'medium'}
        ]
        """
        if base_output_name is None:
            base_output_name = os.path.splitext(input_file)[0]
        
        processes = []
        
        for config in output_configs:
            output_file = f"{base_output_name}.{config['format']}"
            
            cmd = [
                'ffmpeg',
                '-i', input_file
            ]
            
            encoder = config.get('encoder', 'libx264')
            
            # Agregar aceleración si es NVENC
            if 'nvenc' in encoder:
                cmd.extend(['-hwaccel', 'cuda'])
            
            cmd.extend([
                '-c:v', encoder,
                '-preset', config.get('preset', 'medium'),
                '-crf', str(config.get('crf', 23)),
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
            
            processes.append({
                'process': process,
                'config': config,
                'output_file': output_file
            })
        
        return processes
    
    @staticmethod
    def get_default_encoder_for_format(format_name):
        """Obtiene el codificador por defecto para cada formato"""
        encoders = {
            'mp4': 'libx264',
            'mkv': 'libx264',
            'webm': 'libvpx-vp9',
            'avi': 'libx264',
            'mov': 'libx264'
        }
        return encoders.get(format_name, 'libx264')