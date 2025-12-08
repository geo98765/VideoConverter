"""Tab de perfiles de dispositivo"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QGroupBox, QFileDialog, QLabel, QComboBox, QTextEdit)
from threads.conversion_thread import ConversionThread
from models.conversion_job import ConversionJob
from models.video_file import VideoFile
from core.device_profiles import DeviceProfiles
import os

class DeviceProfileTab(QWidget):
    """Tab para conversión con perfiles de dispositivo"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.conversion_thread = None
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
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Selector de perfil
        profile_group = QGroupBox("Perfil de Dispositivo")
        profile_layout = QVBoxLayout()
        
        profile_select_layout = QHBoxLayout()
        profile_select_layout.addWidget(QLabel("Seleccionar perfil:"))
        self.combo_profile = QComboBox()
        
        # Cargar perfiles
        for profile_id, profile_name in DeviceProfiles.get_profile_list():
            self.combo_profile.addItem(profile_name, profile_id)
        
        self.combo_profile.currentIndexChanged.connect(self.show_profile_details)
        profile_select_layout.addWidget(self.combo_profile)
        profile_layout.addLayout(profile_select_layout)
        
        # Detalles del perfil
        self.text_profile_details = QTextEdit()
        self.text_profile_details.setReadOnly(True)
        self.text_profile_details.setMaximumHeight(150)
        profile_layout.addWidget(self.text_profile_details)
        
        profile_group.setLayout(profile_layout)
        layout.addWidget(profile_group)
        
        # Mostrar detalles del primer perfil
        self.show_profile_details()
        
        # Botón de conversión
        self.btn_convert = QPushButton("🎬 Convertir con Perfil")
        self.btn_convert.clicked.connect(self.convert_video)
        self.btn_convert.setMinimumHeight(50)
        self.btn_convert.setEnabled(False)
        self.btn_convert.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #009688; color: white;")
        layout.addWidget(self.btn_convert)
        
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
            self.btn_convert.setEnabled(True)
            if self.parent_window:
                self.parent_window.log(f"Video seleccionado: {os.path.basename(file_path)}")
    
    def show_profile_details(self):
        """Muestra los detalles del perfil seleccionado"""
        profile_id = self.combo_profile.currentData()
        profile = DeviceProfiles.get_profile(profile_id)
        
        if profile:
            details = f"{'='*40}\n"
            details += f"{profile['name']}\n"
            details += f"{'='*40}\n\n"
            details += f"📝 Descripción: {profile['description']}\n\n"
            details += f"⚙️ Configuración:\n"
            details += f"  • Codificador: {profile['encoder']}\n"
            details += f"  • Preset: {profile['preset']}\n"
            details += f"  • CRF: {profile['crf']}\n"
            details += f"  • Resolución: {profile['width']}x{profile['height']}\n"
            details += f"  • FPS: {profile['fps']}\n"
            details += f"  • Audio: {profile['audio_codec']} @ {profile['audio_bitrate']}\n"
            details += f"  • Formato: {profile['format']}\n"
            
            self.text_profile_details.setText(details)
    
    def convert_video(self):
        """Convierte el video usando el perfil seleccionado"""
        if not self.current_file:
            return
        
        if self.conversion_thread and self.conversion_thread.isRunning():
            return
        
        # Obtener perfil
        profile_id = self.combo_profile.currentData()
        profile = DeviceProfiles.get_profile(profile_id)
        
        if not profile:
            return
        
        # Generar nombre de salida
        base_name = os.path.splitext(self.current_file)[0]
        output_file = f"{base_name}_{profile_id}.{profile['format']}"
        
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
        
        self.btn_convert.setEnabled(False)
        
        # Crear job de conversión
        video_file = VideoFile(self.current_file)
        job = ConversionJob(
            video_file,
            output_file,
            profile['encoder'],
            profile['preset'],
            profile['crf'],
            profile['format']
        )
        
        # Crear thread
        self.conversion_thread = ConversionThread(job)
        self.conversion_thread.progress.connect(self.update_progress)
        self.conversion_thread.log_message.connect(self.log)
        self.conversion_thread.finished_signal.connect(self.convert_finished)
        
        self.conversion_thread.start()
    
    def convert_finished(self, success, message):
        """Callback cuando termina la conversión"""
        self.btn_convert.setEnabled(True)
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