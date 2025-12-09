"""Tab para conversión pausable"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QGroupBox, QFileDialog, QLabel, QComboBox, QSpinBox)
from threads.pausable_thread import PausableConversionThread
import os

class PausableTab(QWidget):
    """Tab para conversión con pausa/reanudación"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.pausable_thread = None
        self.current_file = None
        self.is_converting = False
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
        encoding_layout.addLayout(quality_layout)
        
        encoding_group.setLayout(encoding_layout)
        layout.addWidget(encoding_group)
        
        # Estado
        status_group = QGroupBox("Estado")
        status_layout = QVBoxLayout()
        
        self.label_status = QLabel("⏹️ Detenido")
        self.label_status.setProperty("class", "info_label")
        status_layout.addWidget(self.label_status)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Botones de control
        control_layout = QHBoxLayout()
        
        self.btn_start = QPushButton("▶️ Iniciar")
        self.btn_start.clicked.connect(self.start_conversion)
        self.btn_start.setMinimumHeight(50)
        self.btn_start.setEnabled(False)
        self.btn_start.setProperty("class", "success_btn")
        control_layout.addWidget(self.btn_start)
        
        self.btn_pause = QPushButton("⏸️ Pausar")
        self.btn_pause.clicked.connect(self.pause_conversion)
        self.btn_pause.setMinimumHeight(50)
        self.btn_pause.setEnabled(False)
        self.btn_pause.setProperty("class", "warning_btn")
        control_layout.addWidget(self.btn_pause)
        
        self.btn_resume = QPushButton("▶️ Reanudar")
        self.btn_resume.clicked.connect(self.resume_conversion)
        self.btn_resume.setMinimumHeight(50)
        self.btn_resume.setEnabled(False)
        self.btn_resume.setProperty("class", "primary_btn")
        control_layout.addWidget(self.btn_resume)
        
        self.btn_stop = QPushButton("⏹️ Detener")
        self.btn_stop.clicked.connect(self.stop_conversion)
        self.btn_stop.setMinimumHeight(50)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setProperty("class", "danger_btn")
        control_layout.addWidget(self.btn_stop)
        
        layout.addLayout(control_layout)
        
        # Nota
        note = QLabel("ℹ️ Nota: La pausa/reanudación puede no funcionar en todas las plataformas")
        note.setProperty("class", "note_label")
        note.setWordWrap(True)
        layout.addWidget(note)
        
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
            self.btn_start.setEnabled(True)
            if self.parent_window:
                self.parent_window.log(f"Video seleccionado: {os.path.basename(file_path)}")
    
    def start_conversion(self):
        """Inicia la conversión"""
        if not self.current_file:
            return
        
        # Generar nombre de salida
        base_name = os.path.splitext(self.current_file)[0]
        ext = os.path.splitext(self.current_file)[1]
        output_file = f"{base_name}_converted{ext}"
        
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
        
        # Deshabilitar/habilitar botones
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_stop.setEnabled(True)
        self.is_converting = True
        
        # Crear thread
        self.pausable_thread = PausableConversionThread(
            self.current_file,
            output_file,
            encoder,
            'medium',
            crf
        )
        
        self.pausable_thread.progress.connect(self.update_progress)
        self.pausable_thread.log_message.connect(self.log)
        self.pausable_thread.status_changed.connect(self.status_changed)
        self.pausable_thread.finished_signal.connect(self.conversion_finished)
        
        self.pausable_thread.start()
    
    def pause_conversion(self):
        """Pausa la conversión"""
        if self.pausable_thread:
            self.pausable_thread.pause_conversion()
            self.btn_pause.setEnabled(False)
            self.btn_resume.setEnabled(True)
    
    def resume_conversion(self):
        """Reanuda la conversión"""
        if self.pausable_thread:
            self.pausable_thread.resume_conversion()
            self.btn_pause.setEnabled(True)
            self.btn_resume.setEnabled(False)
    
    def stop_conversion(self):
        """Detiene la conversión"""
        if self.pausable_thread:
            self.pausable_thread.stop()
    
    def status_changed(self, status):
        """Callback cuando cambia el estado"""
        status_icons = {
            'running': '▶️ En ejecución',
            'paused': '⏸️ Pausado',
            'stopped': '⏹️ Detenido'
        }
        self.label_status.setText(status_icons.get(status, status))
    
    def conversion_finished(self, success, message):
        """Callback cuando termina la conversión"""
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_resume.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.is_converting = False
        
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