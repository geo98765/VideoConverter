"""Modelo para presets de conversión"""

class Preset:
    """Representa un preset de configuración de conversión"""
    
    def __init__(self, name, encoder, preset, crf, output_format, description=""):
        self.name = name
        self.encoder = encoder
        self.preset = preset
        self.crf = crf
        self.output_format = output_format
        self.description = description
    
    def to_dict(self):
        """Convierte el preset a diccionario"""
        return {
            'name': self.name,
            'encoder': self.encoder,
            'preset': self.preset,
            'crf': self.crf,
            'output_format': self.output_format,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crea un preset desde un diccionario"""
        return cls(
            name=data['name'],
            encoder=data['encoder'],
            preset=data['preset'],
            crf=data['crf'],
            output_format=data['output_format'],
            description=data.get('description', '')
        )
    
    def __repr__(self):
        return f"Preset({self.name})"