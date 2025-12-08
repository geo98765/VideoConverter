"""Tab de cambio de resolución"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QGroupBox, QFileDialog, QLabel, QComboBox, 
                               QCheckBox, QSpinBox, QRadioButton, QButtonGroup)
from threads.resolution_thread import ResolutionThread
from core.resolution_changer import ResolutionChanger
import os

class ResolutionTab(QWidget):
    """Tab para cambiar resolución de videos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.resolution_thread = None
        self.current_file = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Selector de archivo
        file_group = QGroupBox("Video de Entrada")
        file_layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()
        btn_select = QPushButton("📁 Seleccionar Video")
        btn_select.clicked.connect(self.select_file)
        btn_select.setMinimumHeight(40)
        btn_layout.addWidget(btn_select)
        
        self.btn_detect_res = QPushButton("🔍 Detectar Resolución Actual")
        self.btn_detect_res.clicked.connect(self.detect_resolution)
        self.btn_detect_res.setMinimumHeight(40)
        self.btn_detect_res.setEnabled(False)
        btn_layout.addWidget(self.btn_detect_res)
        
        file_layout.addLayout(btn_layout)
        
        self.label_file = QLabel("No hay archivo seleccionado")
        self.label_file.setStyleSheet("padding: 10px; background-color: #f0f0f0;")
        file_layout.addWidget(self.label_file)
        
        self.label_current_res = QLabel("")
        self.label_current_res.setStyleSheet("padding: 5px; color: #1976D2; font-weight: bold;")
        file_layout.addWidget(self.label_current_res)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Opciones de resolución
        resolution_group = QGroupBox("Nueva Resolución")
        resolution_layout = QVBoxLayout()
        
        # Presets comunes
        self.radio_preset = QRadioButton("Usar resolución predefinida:")
        self.radio_preset.setChecked(True)
        resolution_layout.addWidget(self.radio_preset)
        
        preset_layout = QHBoxLayout()
        preset_layout.addSpacing(20)
        self.combo_preset = QComboBox()
        self.combo_preset.addItems(["4K (3840x2160)", "1440p (2560x1440)", "1080p (1920x1080)", 
                                    "720p (1280x720)", "480p (854x480)", "360p (640x360)"])
        self.combo_preset.setCurrentIndex(2)  # 1080p por defecto
        preset_layout.addWidget(self.combo_preset)
        resolution_layout.addLayout(preset_layout)
        
        # Personalizada
        self.radio_custom = QRadioButton("Resolución personalizada:")
        resolution_layout.addWidget(self.radio_custom)
        
        custom_layout = QHBoxLayout()
        custom_layout.addSpacing(20)
        custom_layout.addWidget(QLabel("Ancho:"))
        self.spin_width = QSpinBox()
        self.spin_width.setRange(128, 7680)
        self.spin_width.setValue(1920)
        self.spin_width.setEnabled(False)
        custom_layout.addWidget(self.spin_width)
        custom_layout.addWidget(QLabel("Alto:"))
        self.spin_height = QSpinBox()
        self.spin_height.setRange(128, 4320)
        self.spin_height.setValue(1080)
        self.spin_height.setEnabled(False)
        custom_layout.addWidget(self.spin_height)
        resolution_layout.addLayout(custom_layout)
        
        self.radio_preset.toggled.connect(lambda: self.spin_width.setEnabled(False))
        self.radio_preset.toggled.connect(lambda: self.spin_height.setEnabled(False))
        self.radio_custom.toggled.connect(lambda: self.spin_width.setEnabled(True))
        self.radio_custom.toggled.connect(lambda: self.spin_height.setEnabled(True))
        
        # Mantener aspect ratio
        self.check_maintain_aspect = QCheckBox("Mantener relación de aspecto (recomendado)")
        self.check_maintain_aspect.setChecked(True)
        resolution_layout.addWidget(self.check_maintain_aspect)
        
        resolution_group.setLayout(resolution_layout)
        layout.addWidget(resolution_group)
        
        # Opciones de codificación
        encoding_group = QGroupBox("Opciones de Codificación")
        encoding_layout = QVBoxLayout()
        
        encoder_layout = QHBoxLayout()
        encoder_layout.addWidget(QLabel("Codificador:"))
        self.combo_encoder = QComboBox()
        self.combo_encoder.addItems(["libx264 (CPU)", "h264_nvenc (GPU)", "hevc_nvenc (GPU)"])
        encoder_layout.addWidget(self.combo_encoder)
        encoding_layout.addLayout(encoder_layout)
        
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Calidad (CRF):"))
        self.spin_crf = QSpinBox()
        self.spin_crf.setRange(0, 51)
        self.spin_crf.setValue(23)
        quality_layout.addWidget(self.spin_crf)
        quality_layout.addWidget(QLabel("(menor = mejor)"))
        encoding_layout.addLayout(quality_layout)
        
        encoding_group.setLayout(encoding_layout)
        layout.addWidget(encoding_group)
        
        # Botón de procesamiento
        self.btn_process = QPushButton("📐 Cambiar Resolución")
        self.btn_process.clicked.connect(self.change_resolution)
        self.btn_process.setMinimumHeight(50)
        self.btn_process.setEnabled(False)
        self.btn_process.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #FF9800; color: white;")
        layout.addWidget(self.btn_process)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def select_file(self):
        """Selecciona archivo de video"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar video",
            "",
            "Videos (*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm *.m4v);;Todos (*.*)"
        )
        if file_path:
            self.current_file = file_path
            self.label_file.setText(f"📄 {file_path}")
            self.btn_detect_res.setEnabled(True)
            self.btn_process.setEnabled(True)
            if self.parent_window:
                self.parent_window.log(f"Video seleccionado: {file_path}")
    
    def detect_resolution(self):
        """Detecta la resolución actual del video"""
        if not self.current_file:
            return
        
        width, height = ResolutionChanger.get_current_resolution(self.current_file)
        if width and height:
            self.label_current_res.setText(f"📏 Resolución actual: {width}x{height}")
            if self.parent_window:
                self.parent_window.log(f"Resolución detectada: {width}x{height}")
    
    def change_resolution(self):
        """Cambia la resolución del video"""
        if not self.current_file:
            return
        
        if self.resolution_thread and self.resolution_thread.isRunning():
            return
        
        # Obtener dimensiones
        if self.radio_preset.isChecked():
            preset_text = self.combo_preset.currentText()
            # Extraer números de texto como "1080p (1920x1080)"
            import re
            match = re.search(r'\((\d+)x(\d+)\)', preset_text)
            if match:
                width = int(match.group(1))
                height = int(match.group(2))
            else:
                return
        else:
            width = self.spin_width.value()
            height = self.spin_height.value()
        
        # Generar nombre de salida
        base_name = os.path.splitext(self.current_file)[0]
        ext = os.path.splitext(self.current_file)[1]
        output_file = f"{base_name}_{width}x{height}{ext}"
        
        # Confirmar si existe
        if os.path.exists(output_file):
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self, "Archivo existe",
                f"El archivo ya existe. ¿Sobrescribir?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Obtener encoder
        encoder_text = self.combo_encoder.currentText()
        if "libx264" in encoder_text:
            encoder = "libx264"
        elif "h264_nvenc" in encoder_text:
            encoder = "h264_nvenc"
        elif "hevc_nvenc" in encoder_text:
            encoder = "hevc_nvenc"
        else:
            encoder = "libx264"
        
        crf = self.spin_crf.value()
        maintain_aspect = self.check_maintain_aspect.isChecked()
        
        self.btn_process.setEnabled(False)
        
        # Crear thread
        self.resolution_thread = ResolutionThread(
            self.current_file,
            output_file,
            width,
            height,
            encoder,
            'medium',
            crf,
            maintain_aspect
        )
        
        self.resolution_thread.progress.connect(self.update_progress)
        self.resolution_thread.log_message.connect(self.log)
        self.resolution_thread.finished_signal.connect(self.process_finished)
        
        self.resolution_thread.start()
    
    def process_finished(self, success, message):
        """Callback cuando termina el proceso"""
        self.btn_process.setEnabled(True)
        if self.parent_window:
            self.parent_window.log(message)
            from PyQt6.QtWidgets import QMessageBox
            if success:
                QMessageBox.information(self, "Éxito", message)
            else:
                QMessageBox.warning(self, "Error", message)
    
    def update_progress(self, value):
        """Actualiza progreso"""
        if self.parent_window:
            self.parent_window.update_progress(value)
    
    def log(self, message):
        """Log"""
        if self.parent_window:
            self.parent_window.log(message)