"""Tab de compresión inteligente de videos"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QGroupBox, QFileDialog, QLabel, QComboBox,
                               QSpinBox, QRadioButton, QDoubleSpinBox, QFrame,
                               QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt
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
        # Main container with centering
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Card Frame
        card = QFrame()
        card.setProperty("class", "dashboard_card") # Reuse card style
        card.setFixedWidth(700) # Fixed width for clean look
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(20)
        card_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Comprimir Video")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)
        
        # Selector de archivo
        file_group = QGroupBox("1. Video de Entrada")
        file_layout = QVBoxLayout()
        
        btn_select = QPushButton("📁 Seleccionar Video")
        btn_select.setProperty("class", "secondary_btn")
        btn_select.clicked.connect(self.select_file)
        btn_select.setMinimumHeight(40)
        file_layout.addWidget(btn_select)
        
        self.label_file = QLabel("No hay archivo seleccionado")
        self.label_file.setProperty("class", "file_label")
        self.label_file.setAlignment(Qt.AlignmentFlag.AlignCenter)
        file_layout.addWidget(self.label_file)
        
        self.label_current_size = QLabel("")
        self.label_current_size.setProperty("class", "info_label")
        self.label_current_size.setAlignment(Qt.AlignmentFlag.AlignCenter)
        file_layout.addWidget(self.label_current_size)
        
        file_group.setLayout(file_layout)
        card_layout.addWidget(file_group)
        
        # Modo de compresión
        mode_group = QGroupBox("2. Modo de Compresión")
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
        self.spin_target_size.setMinimumWidth(100)
        size_layout.addWidget(self.spin_target_size)
        size_layout.addStretch()
        mode_layout.addLayout(size_layout)
        
        # Por porcentaje
        self.radio_percentage = QRadioButton("Reducir por porcentaje:")
        mode_layout.addWidget(self.radio_percentage)
        
        percentage_layout = QHBoxLayout()
        percentage_layout.addSpacing(20)
        percentage_layout.addWidget(QLabel("Mantener:"))
        self.spin_percentage = QSpinBox()
        self.spin_percentage.setRange(10, 90)
        self.spin_percentage.setValue(50)
        self.spin_percentage.setSuffix(" %")
        self.spin_percentage.setEnabled(False)
        self.spin_percentage.setMinimumWidth(100)
        percentage_layout.addWidget(self.spin_percentage)
        percentage_layout.addWidget(QLabel("del original"))
        percentage_layout.addStretch()
        mode_layout.addLayout(percentage_layout)
        
        self.radio_target_size.toggled.connect(lambda: self.spin_target_size.setEnabled(True))
        self.radio_target_size.toggled.connect(lambda: self.spin_percentage.setEnabled(False))
        self.radio_percentage.toggled.connect(lambda: self.spin_target_size.setEnabled(False))
        self.radio_percentage.toggled.connect(lambda: self.spin_percentage.setEnabled(True))
        
        mode_group.setLayout(mode_layout)
        card_layout.addWidget(mode_group)
        
        # Opciones de codificación
        encoding_group = QGroupBox("3. Avanzado (Codificador)")
        encoding_layout = QVBoxLayout()
        
        encoder_layout = QHBoxLayout()
        encoder_layout.addWidget(QLabel("Codificador:"))
        self.combo_encoder = QComboBox()
        self.combo_encoder.addItems(["libx264 (CPU)", "h264_nvenc (GPU)", "hevc_nvenc (GPU)"])
        encoder_layout.addWidget(self.combo_encoder)
        encoding_layout.addLayout(encoder_layout)
        
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Velocidad:"))
        self.combo_preset = QComboBox()
        self.combo_preset.addItems(["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow"])
        self.combo_preset.setCurrentText("medium")
        preset_layout.addWidget(self.combo_preset)
        encoding_layout.addLayout(preset_layout)
        
        encoding_group.setLayout(encoding_layout)
        card_layout.addWidget(encoding_group)
        
        # Botón de compresión
        self.btn_compress = QPushButton("🗜️ Comprimir Video")
        self.btn_compress.clicked.connect(self.compress_video)
        self.btn_compress.setMinimumHeight(45)
        self.btn_compress.setEnabled(False)
        self.btn_compress.setProperty("class", "primary_btn")
        self.btn_compress.setCursor(Qt.CursorShape.PointingHandCursor)
        card_layout.addWidget(self.btn_compress)
        
        # --- PROGRESS BAR (No Queue) ---
        status_layout = QVBoxLayout()
        
        self.label_status = QLabel("Listo")
        self.label_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.label_status)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        status_layout.addWidget(self.progress_bar)
        
        card_layout.addLayout(status_layout)
        
        main_layout.addWidget(card)
        self.setLayout(main_layout)
    
    def select_file(self):
        """Abre dialogo para seleccionar archivo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Video",
            "",
            "Videos (*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm *.m4v);;Todos (*.*)"
        )
        if file_path:
            self.current_file = file_path
            self.label_file.setText(f"📄 {os.path.basename(file_path)}")
            self.btn_compress.setEnabled(True)
            
            # Mostrar tamaño actual
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            self.label_current_size.setText(f"💾 Tamaño actual: {size_mb:.2f} MB")
            
    def compress_video(self):
        """Inicia la compresión delegando 1 archivo a la cola"""
        if not self.current_file:
            return
            
        # Local processing
        self.label_status.setText("Iniciando compresión...")
        self.progress_bar.setValue(0)
        
        if self.compress_thread and self.compress_thread.isRunning():
            return
        
        # Generar nombre de salida
        base_name = os.path.splitext(self.current_file)[0]
        ext = os.path.splitext(self.current_file)[1]
        output_file = f"{base_name}_compressed{ext}"
        
        # Confirmar si existe
        if os.path.exists(output_file):
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
            if success:
                QMessageBox.information(self, "Éxito", message)
            else:
                QMessageBox.warning(self, "Error", message)
    
    def update_progress(self, value):
        """Actualiza progreso"""
        self.progress_bar.setValue(value)
        if self.parent_window:
            self.parent_window.update_progress(value)
    
    def log(self, message):
        """Log"""
        self.label_status.setText(message)
        if self.parent_window:
            self.parent_window.log(message)