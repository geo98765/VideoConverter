"""Tab de configuración avanzada"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QGroupBox, QCheckBox, QComboBox, QLabel, QSpinBox)

class AdvancedConfigTab(QWidget):
    """Tab de configuración avanzada"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Opciones avanzadas
        advanced_group = QGroupBox("Configuración Avanzada de Codificación")
        advanced_layout = QVBoxLayout()
        
        # Modo de codificación
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Modo de codificación:"))
        self.combo_encoding_mode = QComboBox()
        self.combo_encoding_mode.addItems(["Automático (detectar mejor opción)", "Forzar CPU", "Forzar GPU (NVENC)"])
        mode_layout.addWidget(self.combo_encoding_mode)
        advanced_layout.addLayout(mode_layout)
        
        # Codificador específico
        encoder_layout = QHBoxLayout()
        encoder_layout.addWidget(QLabel("Codificador:"))
        self.combo_encoder_advanced = QComboBox()
        self.combo_encoder_advanced.addItems(["libx264 (CPU - H.264)", "h264_nvenc (GPU - H.264)", "hevc_nvenc (GPU - H.265)"])
        encoder_layout.addWidget(self.combo_encoder_advanced)
        advanced_layout.addLayout(encoder_layout)
        
        # Preset
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Preset (velocidad):"))
        self.combo_preset_advanced = QComboBox()
        self.combo_preset_advanced.addItems(["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"])
        self.combo_preset_advanced.setCurrentText("medium")
        preset_layout.addWidget(self.combo_preset_advanced)
        advanced_layout.addLayout(preset_layout)
        
        # CRF
        crf_layout = QHBoxLayout()
        crf_layout.addWidget(QLabel("CRF (calidad):"))
        self.spin_crf_advanced = QSpinBox()
        self.spin_crf_advanced.setRange(0, 51)
        self.spin_crf_advanced.setValue(23)
        self.spin_crf_advanced.setToolTip("0=mejor calidad (archivo grande), 51=peor calidad (archivo pequeño)")
        crf_layout.addWidget(self.spin_crf_advanced)
        crf_layout.addWidget(QLabel("(menor valor = mejor calidad)"))
        advanced_layout.addLayout(crf_layout)
        
        # Formato
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Formato de salida:"))
        self.combo_format_advanced = QComboBox()
        self.combo_format_advanced.addItems(["mp4", "mkv", "avi", "mov", "webm"])
        format_layout.addWidget(self.combo_format_advanced)
        advanced_layout.addLayout(format_layout)
        
        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)
        
        # Opciones de reparación
        repair_group = QGroupBox("Opciones de Reparación")
        repair_layout = QVBoxLayout()
        
        self.check_ignore_errors = QCheckBox("Ignorar errores durante la reparación")
        self.check_ignore_errors.setChecked(True)
        repair_layout.addWidget(self.check_ignore_errors)
        
        self.check_fix_timestamps = QCheckBox("Corregir timestamps")
        self.check_fix_timestamps.setChecked(True)
        repair_layout.addWidget(self.check_fix_timestamps)
        
        repair_group.setLayout(repair_layout)
        layout.addWidget(repair_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def get_encoder_settings(self):
        """Obtiene configuración del codificador"""
        encoder_text = self.combo_encoder_advanced.currentText()
        if "libx264" in encoder_text:
            encoder = "libx264"
        elif "h264_nvenc" in encoder_text:
            encoder = "h264_nvenc"
        elif "hevc_nvenc" in encoder_text:
            encoder = "hevc_nvenc"
        else:
            encoder = "libx264"
        
        preset = self.combo_preset_advanced.currentText()
        crf = self.spin_crf_advanced.value()
        output_format = self.combo_format_advanced.currentText()
        
        return encoder, preset, crf, output_format