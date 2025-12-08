"""Modelo para representar un archivo de video"""
import os

class VideoFile:
    """Representa un archivo de video con su información"""
    
    def __init__(self, file_path):
        self.path = file_path
        self.name = os.path.basename(file_path)
        self.directory = os.path.dirname(file_path)
        self.extension = os.path.splitext(file_path)[1]
        self.size = 0
        self.duration = 0
        self.codec = None
        self.resolution = None
        self.fps = None
        self.bitrate = None
        self.status = 'Pendiente'
        
        # Calcular tamaño
        if os.path.exists(file_path):
            self.size = os.path.getsize(file_path)
    
    def get_size_mb(self):
        """Retorna el tamaño en MB"""
        return self.size / (1024 * 1024)
    
    def get_size_formatted(self):
        """Retorna el tamaño formateado"""
        mb = self.get_size_mb()
        if mb < 1024:
            return f"{mb:.2f} MB"
        else:
            gb = mb / 1024
            return f"{gb:.2f} GB"
    
    def __repr__(self):
        return f"VideoFile({self.name})"