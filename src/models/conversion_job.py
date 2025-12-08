"""Modelo para representar un trabajo de conversión"""

class ConversionJob:
    """Representa un trabajo de conversión de video"""
    
    def __init__(self, input_file, output_file, encoder, preset='medium', crf=23, output_format='mp4'):
        self.input_file = input_file
        self.output_file = output_file
        self.encoder = encoder
        self.preset = preset
        self.crf = crf
        self.output_format = output_format
        self.status = 'pending'  # pending, processing, completed, failed, cancelled
        self.progress = 0
        self.error_message = None
    
    def is_nvenc(self):
        """Verifica si usa NVENC"""
        return 'nvenc' in self.encoder.lower()
    
    def __repr__(self):
        return f"ConversionJob({self.input_file.name} -> {self.output_format})"