"""Tab de compresión inteligente de videos"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QGroupBox, QFileDialog, QLabel, QComboBox,
                               QSpinBox, QRadioButton, QDoubleSpinBox)
from threads.compress_thread import CompressThread
import os

class CompressTab(QWidget):
    """Tab para compresión inteligente de videos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.compress_thread = None
        self.current_file = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Selector de archivo
        file_group = QGroupBox("Video de Entrada")
        file_layout = QVBoxLayout()
        
        btn_select = QPushButton("📁 Seleccionar Video")
        btn_select.clicked.connect(self.select_file)
        btn_select.setMinimumHeight(40)
        file_layout.addWidget(btn_select)
        
        self.label_file = QLabel("No hay archivo seleccionado")
        self.label_file.setStyleSheet("padding: 10px; background-color: #f0f0f0;")
        file_layout.addWidget(self.label_file)
        
        self.label_current_size = QLabel("")
        self.label_current_size.setStyleSheet("padding: 5px; color: #1976D2; font-weight: bold;")
        file_layout.addWidget(self.label_current_size)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Modo de compresión
        mode_group = QGroupBox("Modo de Compresión")
        mode_layout = QVBoxLayout()
        
        # Por tamaño objetivo
        self.radio_target_size = QRadioButton("Comprimir a tamaño específico:")
        self.radio_target_size.setChecked(True)
        mode_layout.addWidget(self.radio_target_size)
        
        size_layout = QHBoxLayout()
        size_layout.addSpacing(20)
        size_layout.addWidget(QLabel("Tamaño objetivo:"))
        self.spin_target_size = QSpinBox()
        self.spin_target_size.setRange(1, 10000)
        self.spin_target_size.setValue(50)
        self.spin_target_size.setSuffix(" MB")
        size_layout.addWidget(self.spin_target_size)
        mode_layout.addLayout(size_layout)
        
        # Por porcentaje
        self.radio_percentage = QRadioButton("Reducir por porcentaje del tamaño original:")
        mode_layout.addWidget(self.radio_percentage)
        
        percentage_layout = QHBoxLayout()
        percentage_layout.addSpacing(20)
        percentage_layout.addWidget(QLabel("Mantener:"))
        self.spin_percentage = QSpinBox()
        self.spin_percentage.setRange(10, 90)
        self.spin_percentage.setValue(50)
        self.spin_percentage.setSuffix(" %")
        self.spin_percentage.setEnabled(False)
        percentage_layout.addWidget(self.spin_percentage)
        percentage_layout.addWidget(QLabel("del tamaño original"))
        mode_layout.addLayout(percentage_layout)
        
        self.radio_target_size.toggled.connect(lambda: self.spin_target_size.setEnabled(True))
        self.radio_target_size.toggled.connect(lambda: self.spin_percentage.setEnabled(False))
        self.radio_percentage.toggled.connect(lambda: self.spin_target_size.setEnabled(False))
        self.radio_percentage.toggled.connect(lambda: self.spin_percentage.setEnabled(True))
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # Opciones de codificación
        encoding_group = QGroupBox("Opciones de Codificación")
        encoding_layout = QVBoxLayout()
        
        encoder_layout = QHBoxLayout()
        encoder_layout.addWidget(QLabel("Codificador:"))
        self.combo_encoder = QComboBox()
        self.combo_encoder.addItems(["libx264 (CPU)", "h264_nvenc (GPU)", "hevc_nvenc (GPU)"])
        encoder_layout.addWidget(self.combo_encoder)
        encoding_layout.addLayout(encoder_layout)
        
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Preset:"))
        self.combo_preset = QComboBox()
        self.combo_preset.addItems(["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow"])
        self.combo_preset.setCurrentText("medium")
        preset_layout.addWidget(self.combo_preset)
        encoding_layout.addLayout(preset_layout)
        
        encoding_group.setLayout(encoding_layout)
        layout.addWidget(encoding_group)
        
        # Botón de compresión
        self.btn_compress = QPushButton("🗜️ Comprimir Video")
        self.btn_compress.clicked.connect(self.compress_video)
        self.btn_compress.setMinimumHeight(50)
        self.btn_compress.setEnabled(False)
        self.btn_compress.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #9C27B0; color: white;")
        layout.addWidget(self.btn_compress)
        
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
            self.btn_compress.setEnabled(True)
            
            # Mostrar tamaño actual
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            self.label_current_size.setText(f"💾 Tamaño actual: {size_mb:.2f} MB")
            
            if self.parent_window:
                self.parent_window.log(f"Video seleccionado para compresión: {file_path}")
    
    def compress_video(self):
        """Comprime el video"""
        if not self.current_file:
            return
        
        if self.compress_thread and self.compress_thread.isRunning():
            return
        
        # Generar nombre de salida
        base_name = os.path.splitext(self.current_file)[0]
        ext = os.path.splitext(self.current_file)[1]
        output_file = f"{base_name}_compressed{ext}"
        
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
        
        # Obtener configuración
        if self.radio_target_size.isChecked():
            compression_mode = 'size'
            target_value = self.spin_target_size.value()
        else:
            compression_mode = 'percentage'
            target_value = self.spin_percentage.value()
        
        encoder_text = self.combo_encoder.currentText()
        if "libx264" in encoder_text:
            encoder = "libx264"
        elif "h264_nvenc" in encoder_text:
            encoder = "h264_nvenc"
        elif "hevc_nvenc" in encoder_text:
            encoder = "hevc_nvenc"
        else:
            encoder = "libx264"
        
        preset = self.combo_preset.currentText()
        
        self.btn_compress.setEnabled(False)
        
        # Crear thread
        self.compress_thread = CompressThread(
            self.current_file,
            output_file,
            compression_mode,
            target_value,
            encoder,
            preset
        )
        
        self.compress_thread.progress.connect(self.update_progress)
        self.compress_thread.log_message.connect(self.log)
        self.compress_thread.finished_signal.connect(self.compress_finished)
        
        self.compress_thread.start()
    
    def compress_finished(self, success, message):
        """Callback cuando termina la compresión"""
        self.btn_compress.setEnabled(True)
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