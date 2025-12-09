"""Tab de extracción de audio"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QGroupBox, QFileDialog, QLabel, QComboBox, QSpinBox,
                               QProgressBar)
from threads.audio_extract_thread import AudioExtractThread
from PyQt6.QtCore import Qt
import os

class AudioExtractTab(QWidget):
    """Tab para extraer audio de videos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.extract_thread = None
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
        self.label_file.setProperty("class", "file_label")
        file_layout.addWidget(self.label_file)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Opciones de extracción
        options_group = QGroupBox("Opciones de Extracción")
        options_layout = QVBoxLayout()
        
        # Formato
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Formato de audio:"))
        self.combo_format = QComboBox()
        self.combo_format.addItems(["mp3", "aac", "wav", "flac", "ogg", "m4a"])
        format_layout.addWidget(self.combo_format)
        options_layout.addLayout(format_layout)
        
        # Bitrate
        bitrate_layout = QHBoxLayout()
        bitrate_layout.addWidget(QLabel("Bitrate (kbps):"))
        self.combo_bitrate = QComboBox()
        self.combo_bitrate.addItems(["128k", "192k", "256k", "320k"])
        self.combo_bitrate.setCurrentText("192k")
        bitrate_layout.addWidget(self.combo_bitrate)
        options_layout.addLayout(bitrate_layout)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Botón de extracción
        self.btn_extract = QPushButton("🎵 Extraer Audio")
        self.btn_extract.clicked.connect(self.extract_audio)
        self.btn_extract.setMinimumHeight(50)
        self.btn_extract.setEnabled(False)
        self.btn_extract.setProperty("class", "primary_btn")
        self.btn_extract.setProperty("class", "primary_btn")
        layout.addWidget(self.btn_extract)
        
        # ProgressBar
        status_layout = QVBoxLayout()
        self.label_status = QLabel("Listo")
        self.label_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.label_status)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        status_layout.addWidget(self.progress_bar)
        
        layout.addLayout(status_layout)
        
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
            self.btn_extract.setEnabled(True)
            if self.parent_window:
                self.parent_window.log(f"Video seleccionado para extracción: {file_path}")
    
    def extract_audio(self):
        """Extrae el audio del video"""
        if not self.current_file:
            return
        
        if self.extract_thread and self.extract_thread.isRunning():
            return
        
        # Generar nombre de salida
        base_name = os.path.splitext(self.current_file)[0]
        format = self.combo_format.currentText()
        output_file = f"{base_name}_audio.{format}"
        
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
        
        bitrate = self.combo_bitrate.currentText()
        
        self.btn_extract.setEnabled(False)
        self.label_status.setText("Iniciando extracción...")
        self.progress_bar.setValue(0)
        
        # Crear thread
        self.extract_thread = AudioExtractThread(
            self.current_file,
            output_file,
            format,
            bitrate
        )
        
        self.extract_thread.progress.connect(self.update_progress)
        self.extract_thread.log_message.connect(self.log)
        self.extract_thread.finished_signal.connect(self.extract_finished)
        
        self.extract_thread.start()
    
    def extract_finished(self, success, message):
        """Callback cuando termina la extracción"""
        self.btn_extract.setEnabled(True)
        if self.parent_window:
            self.parent_window.log(message)
            from PyQt6.QtWidgets import QMessageBox
            if success:
                QMessageBox.information(self, "Éxito", message)
            else:
                QMessageBox.warning(self, "Error", message)
    
    def update_progress(self, value):
        """Actualiza progreso"""
    def update_progress(self, value):
        """Actualiza progreso"""
        self.progress_bar.setValue(value)
        if self.parent_window:
            self.parent_window.update_progress(value)
    
    def log(self, message):
        """Log"""
    def log(self, message):
        """Log"""
        self.label_status.setText(message)
        if self.parent_window:
            self.parent_window.log(message)