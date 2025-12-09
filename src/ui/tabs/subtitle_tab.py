"""Tab para manejo de subtítulos"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QGroupBox, QFileDialog, QLabel, QComboBox, QRadioButton)
from threads.subtitle_thread import SubtitleThread
from core.subtitle_handler import SubtitleHandler
import os

class SubtitleTab(QWidget):
    """Tab para agregar, quemar y extraer subtítulos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.subtitle_thread = None
        self.video_file = None
        self.subtitle_file = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Selector de video
        video_group = QGroupBox("Video")
        video_layout = QVBoxLayout()
        
        btn_select_video = QPushButton("📁 Seleccionar Video")
        btn_select_video.clicked.connect(self.select_video)
        btn_select_video.setMinimumHeight(40)
        video_layout.addWidget(btn_select_video)
        
        self.label_video = QLabel("No hay video seleccionado")
        self.label_video.setProperty("class", "file_label")
        video_layout.addWidget(self.label_video)
        
        video_group.setLayout(video_layout)
        layout.addWidget(video_group)
        
        # Operaciones
        operation_group = QGroupBox("Operación")
        operation_layout = QVBoxLayout()
        
        # Agregar subtítulos (soft)
        self.radio_add = QRadioButton("Agregar subtítulos (soft - se pueden activar/desactivar)")
        self.radio_add.setChecked(True)
        operation_layout.addWidget(self.radio_add)
        
        # Quemar subtítulos (hard)
        self.radio_burn = QRadioButton("Quemar subtítulos (hard - permanentes en el video)")
        operation_layout.addWidget(self.radio_burn)
        
        # Extraer subtítulos
        self.radio_extract = QRadioButton("Extraer subtítulos del video")
        operation_layout.addWidget(self.radio_extract)
        
        operation_group.setLayout(operation_layout)
        layout.addWidget(operation_group)
        
        # Selector de subtítulo (para add/burn)
        subtitle_group = QGroupBox("Archivo de Subtítulos")
        subtitle_layout = QVBoxLayout()
        
        btn_select_subtitle = QPushButton("📄 Seleccionar Subtítulos (SRT/ASS/VTT)")
        btn_select_subtitle.clicked.connect(self.select_subtitle)
        btn_select_subtitle.setMinimumHeight(40)
        subtitle_layout.addWidget(btn_select_subtitle)
        
        self.label_subtitle = QLabel("No hay subtítulo seleccionado")
        self.label_subtitle.setProperty("class", "file_label")
        subtitle_layout.addWidget(self.label_subtitle)
        
        subtitle_group.setLayout(subtitle_layout)
        layout.addWidget(subtitle_group)
        
        # Deshabilitar selector de subtítulos si se selecciona extraer
        self.radio_extract.toggled.connect(lambda checked: btn_select_subtitle.setEnabled(not checked))
        
        # Opciones de codificación (solo para add/burn)
        encoding_group = QGroupBox("Opciones de Codificación")
        encoding_layout = QVBoxLayout()
        
        encoder_layout = QHBoxLayout()
        encoder_layout.addWidget(QLabel("Codificador:"))
        self.combo_encoder = QComboBox()
        self.combo_encoder.addItems(["libx264 (CPU)", "h264_nvenc (GPU)", "hevc_nvenc (GPU)"])
        encoder_layout.addWidget(self.combo_encoder)
        encoding_layout.addLayout(encoder_layout)
        
        encoding_group.setLayout(encoding_layout)
        layout.addWidget(encoding_group)
        
        # Botón de procesamiento
        self.btn_process = QPushButton("▶️ Procesar")
        self.btn_process.clicked.connect(self.process)
        self.btn_process.setMinimumHeight(50)
        self.btn_process.setEnabled(False)
        self.btn_process.setProperty("class", "primary_btn")
        layout.addWidget(self.btn_process)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def select_video(self):
        """Selecciona video"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar video",
            "",
            "Videos (*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm *.m4v);;Todos (*.*)"
        )
        if file_path:
            self.video_file = file_path
            self.label_video.setText(f"📄 {file_path}")
            self.check_ready()
            if self.parent_window:
                self.parent_window.log(f"Video seleccionado: {os.path.basename(file_path)}")
    
    def select_subtitle(self):
        """Selecciona archivo de subtítulos"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar subtítulos",
            "",
            "Subtítulos (*.srt *.ass *.ssa *.vtt);;Todos (*.*)"
        )
        if file_path:
            self.subtitle_file = file_path
            self.label_subtitle.setText(f"📄 {file_path}")
            self.check_ready()
            if self.parent_window:
                self.parent_window.log(f"Subtítulos seleccionados: {os.path.basename(file_path)}")
    
    def check_ready(self):
        """Verifica si está listo para procesar"""
        if self.radio_extract.isChecked():
            self.btn_process.setEnabled(self.video_file is not None)
        else:
            self.btn_process.setEnabled(self.video_file is not None and self.subtitle_file is not None)
    
    def process(self):
        """Procesa la operación seleccionada"""
        if not self.video_file:
            return
        
        if self.subtitle_thread and self.subtitle_thread.isRunning():
            return
        
        # Determinar operación
        if self.radio_add.isChecked():
            operation = 'add'
            base_name = os.path.splitext(self.video_file)[0]
            ext = os.path.splitext(self.video_file)[1]
            output_file = f"{base_name}_with_subs{ext}"
        elif self.radio_burn.isChecked():
            operation = 'burn'
            base_name = os.path.splitext(self.video_file)[0]
            ext = os.path.splitext(self.video_file)[1]
            output_file = f"{base_name}_burned_subs{ext}"
        else:  # extract
            operation = 'extract'
            base_name = os.path.splitext(self.video_file)[0]
            output_file = f"{base_name}_subtitles.srt"
        
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
        
        self.btn_process.setEnabled(False)
        
        # Crear thread
        self.subtitle_thread = SubtitleThread(
            operation,
            self.video_file,
            output_file,
            self.subtitle_file,
            encoder,
            'medium',
            23
        )
        
        self.subtitle_thread.progress.connect(self.update_progress)
        self.subtitle_thread.log_message.connect(self.log)
        self.subtitle_thread.finished_signal.connect(self.process_finished)
        
        self.subtitle_thread.start()
    
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