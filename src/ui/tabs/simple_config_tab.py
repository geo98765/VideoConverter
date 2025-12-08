"""Tab de configuración simple"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QGroupBox, QCheckBox, QComboBox, QLabel,
                               QRadioButton, QLineEdit, QFileDialog)

class SimpleConfigTab(QWidget):
    """Tab de configuración recomendada/simple"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.output_folder = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Selector de archivos
        file_group = QGroupBox("Archivos de Video")
        file_layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()
        btn_add_file = QPushButton("📁 Agregar Video")
        btn_add_file.clicked.connect(self.add_single_file)
        btn_add_file.setMinimumHeight(40)
        btn_layout.addWidget(btn_add_file)
        
        btn_add_multiple = QPushButton("📂 Agregar Múltiples Videos")
        btn_add_multiple.clicked.connect(self.add_multiple_files)
        btn_add_multiple.setMinimumHeight(40)
        btn_layout.addWidget(btn_add_multiple)
        
        file_layout.addLayout(btn_layout)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Carpeta de salida
        output_group = QGroupBox("Carpeta de Salida")
        output_layout = QVBoxLayout()
        
        self.radio_same_folder = QRadioButton("Guardar en la misma carpeta del video original")
        self.radio_same_folder.setChecked(True)
        output_layout.addWidget(self.radio_same_folder)
        
        self.radio_custom_folder = QRadioButton("Guardar en carpeta personalizada:")
        output_layout.addWidget(self.radio_custom_folder)
        
        folder_select_layout = QHBoxLayout()
        self.line_output_folder = QLineEdit()
        self.line_output_folder.setPlaceholderText("Selecciona una carpeta...")
        self.line_output_folder.setEnabled(False)
        folder_select_layout.addWidget(self.line_output_folder)
        
        btn_select_folder = QPushButton("📁 Seleccionar Carpeta")
        btn_select_folder.clicked.connect(self.select_output_folder)
        folder_select_layout.addWidget(btn_select_folder)
        
        output_layout.addLayout(folder_select_layout)
        
        self.radio_same_folder.toggled.connect(lambda: self.line_output_folder.setEnabled(False))
        self.radio_custom_folder.toggled.connect(lambda: self.line_output_folder.setEnabled(True))
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # Opciones simples
        simple_options_group = QGroupBox("Opciones de Conversión")
        simple_layout = QVBoxLayout()
        
        # Usar GPU
        self.check_use_gpu = QCheckBox("✨ Usar aceleración por GPU (NVENC) - Recomendado si está disponible")
        self.check_use_gpu.setChecked(True)
        simple_layout.addWidget(self.check_use_gpu)
        
        # Calidad
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Calidad:"))
        self.combo_quality_simple = QComboBox()
        self.combo_quality_simple.addItems(["Alta (CRF 18)", "Media (CRF 23) - Recomendado", "Baja (CRF 28)"])
        self.combo_quality_simple.setCurrentIndex(1)
        quality_layout.addWidget(self.combo_quality_simple)
        simple_layout.addLayout(quality_layout)
        
        # Formato
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Formato de salida:"))
        self.combo_format_simple = QComboBox()
        self.combo_format_simple.addItems(["mp4", "mkv", "avi", "mov"])
        format_layout.addWidget(self.combo_format_simple)
        simple_layout.addLayout(format_layout)
        
        simple_options_group.setLayout(simple_layout)
        layout.addWidget(simple_options_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def add_single_file(self):
        """Agrega un solo archivo"""
        if self.parent_window:
            self.parent_window.add_single_file()
    
    def add_multiple_files(self):
        """Agrega múltiples archivos"""
        if self.parent_window:
            self.parent_window.add_multiple_files()
    
    def select_output_folder(self):
        """Selecciona carpeta de salida"""
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de salida")
        if folder:
            self.output_folder = folder
            self.line_output_folder.setText(folder)
            self.radio_custom_folder.setChecked(True)
            if self.parent_window:
                self.parent_window.log(f"📁 Carpeta de salida: {folder}")
    
    def get_output_folder(self):
        """Obtiene la carpeta de salida"""
        if self.radio_custom_folder.isChecked() and self.output_folder:
            return self.output_folder
        return None
    
    def get_encoder_settings(self):
        """Obtiene configuración del codificador"""
        if self.check_use_gpu.isChecked():
            encoder = "h264_nvenc"
        else:
            encoder = "libx264"
        
        quality_map = {
            "Alta (CRF 18)": 18,
            "Media (CRF 23) - Recomendado": 23,
            "Baja (CRF 28)": 28
        }
        crf = quality_map.get(self.combo_quality_simple.currentText(), 23)
        preset = "medium"
        output_format = self.combo_format_simple.currentText()
        
        return encoder, preset, crf, output_format