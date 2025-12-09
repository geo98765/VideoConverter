"""Vista de Configuración Unificada (Merge Simple + Avanzado)"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QGroupBox, QCheckBox, QComboBox, QLabel,
                               QRadioButton, QLineEdit, QFileDialog, QSpinBox, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

class UnifiedConfigTab(QWidget):
    """
    Combina la configuración simple y avanzada en una sola interfaz limpia.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.parent_window = parent
        self.output_folder = None
        
        # Mapa de configuraciones recomendadas por formato
        self.RECOMMENDED_SETTINGS = {
            'mp4': {'encoder_cpu': 'libx264', 'encoder_gpu': 'h264_nvenc', 'crf': 23, 'preset': 'medium'},
            'mkv': {'encoder_cpu': 'libx264', 'encoder_gpu': 'h264_nvenc', 'crf': 23, 'preset': 'medium'},
            'webm': {'encoder_cpu': 'libvpx-vp9', 'encoder_gpu': 'libvpx-vp9', 'crf': 30, 'preset': 'medium'}, # VP9 suele usar CRF más alto
            'avi': {'encoder_cpu': 'libx264', 'encoder_gpu': 'h264_nvenc', 'crf': 23, 'preset': 'medium'},
            'mov': {'encoder_cpu': 'libx264', 'encoder_gpu': 'h264_nvenc', 'crf': 23, 'preset': 'medium'},
            'mp3': {'encoder_cpu': 'libmp3lame', 'encoder_gpu': 'libmp3lame', 'crf': 0, 'preset': 'medium'} # Audio only
        }
        
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        
        # --- SECCIÓN 1: Selección de Archivos ---
        file_group = QGroupBox("1. Selección de Archivos")
        file_layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()
        self.btn_add_file = QPushButton("📁 Agregar Video")
        self.btn_add_file.setProperty("class", "primary_btn")
        self.btn_add_file.setMinimumHeight(35)
        
        self.btn_add_multiple = QPushButton("📂 Agregar Carpeta / Múltiples")
        self.btn_add_multiple.setProperty("class", "primary_btn")
        self.btn_add_multiple.setMinimumHeight(35)
        
        btn_layout.addWidget(self.btn_add_file)
        btn_layout.addWidget(self.btn_add_multiple)
        
        file_layout.addLayout(btn_layout)
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        # --- SECCIÓN 2: Opciones de Salida ---
        output_group = QGroupBox("2. Carpeta de Destino")
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
        self.line_output_folder.setProperty("class", "folder_input")
        folder_select_layout.addWidget(self.line_output_folder)
        
        self.btn_select_folder = QPushButton("...")
        self.btn_select_folder.setFixedWidth(40)
        self.btn_select_folder.setProperty("class", "secondary_btn")
        folder_select_layout.addWidget(self.btn_select_folder)
        
        output_layout.addLayout(folder_select_layout)
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)
        
        # --- SECCIÓN 3: Configuración de Conversión ---
        config_group = QGroupBox("3. Configuración de Conversión")
        config_layout = QVBoxLayout()
        
        # Opciones Básicas (Siempre visibles)
        basic_layout = QHBoxLayout()
        
        # Formato
        format_container = QVBoxLayout()
        format_container.addWidget(QLabel("Formato de Salida"))
        self.combo_format = QComboBox()
        self.combo_format.addItems(["mp4", "mkv", "avi", "mov", "webm", "mp3"])
        self.combo_format.setMinimumWidth(100)
        format_container.addWidget(self.combo_format)
        
        # Checkbox Configuración Recomendada
        self.check_recommended = QCheckBox("Configuración Recomendada")
        self.check_recommended.setChecked(True)
        self.check_recommended.setToolTip("Ajusta automáticamente la calidad y codificador según el formato")
        format_container.addWidget(self.check_recommended)
        
        basic_layout.addLayout(format_container)
        
        # Calidad (Preset Simple)
        quality_container = QVBoxLayout()
        quality_container.addWidget(QLabel("Calidad Recomendada"))
        self.combo_quality = QComboBox()
        self.combo_quality.addItems(["Alta Calidad (CRF 18)", "Calidad Estándar (CRF 23)", "Tamaño Pequeño (CRF 28)"])
        self.combo_quality.setCurrentIndex(1) # Medium default
        quality_container.addWidget(self.combo_quality)
        basic_layout.addLayout(quality_container)
        
        # Aceleración por Hardware
        hw_container = QVBoxLayout()
        hw_container.addWidget(QLabel("Aceleración"))
        self.check_gpu = QCheckBox("Usar GPU (NVIDIA)")
        self.check_gpu.setChecked(True)
        hw_container.addWidget(self.check_gpu)
        basic_layout.addLayout(hw_container)
        
        config_layout.addLayout(basic_layout)
        
        # Separador / Toggle Avanzado
        toggle_layout = QHBoxLayout()
        self.btn_toggle_advanced = QPushButton("Mostrar Opciones Avanzadas ▼")
        self.btn_toggle_advanced.setCheckable(True)
        self.btn_toggle_advanced.setFlat(True)
        self.btn_toggle_advanced.setStyleSheet("text-align: left; font-weight: bold; color: #89B4FA;")
        toggle_layout.addWidget(self.btn_toggle_advanced)
        toggle_layout.addStretch()
        config_layout.addLayout(toggle_layout)
        
        # Opciones Avanzadas (Ocultas por defecto)
        self.advanced_frame = QFrame()
        self.advanced_frame.setVisible(False)
        self.advanced_frame.setFrameShape(QFrame.Shape.NoFrame)
        advanced_layout = QVBoxLayout(self.advanced_frame)
        advanced_layout.setContentsMargins(0, 5, 0, 0)
        
        # Encoder Específico
        enc_row = QHBoxLayout()
        enc_row.addWidget(QLabel("Codificador:"))
        self.combo_encoder = QComboBox()
        self.combo_encoder.addItems(["Automático", "libx264 (CPU)", "h264_nvenc (GPU)", "hevc (CPU)", "hevc_nvenc (GPU)"])
        enc_row.addWidget(self.combo_encoder)
        advanced_layout.addLayout(enc_row)
        
        # Preset y CRF Manual
        manual_row = QHBoxLayout()
        
        manual_row.addWidget(QLabel("Preset:"))
        self.combo_preset = QComboBox()
        self.combo_preset.addItems(["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"])
        self.combo_preset.setCurrentText("medium")
        manual_row.addWidget(self.combo_preset)
        
        manual_row.addWidget(QLabel("CRF Manual:"))
        self.spin_crf = QSpinBox()
        self.spin_crf.setRange(0, 51)
        self.spin_crf.setValue(23)
        manual_row.addWidget(self.spin_crf)
        
        advanced_layout.addLayout(manual_row)
        
        # Opciones de Reparación
        advanced_layout.addWidget(QLabel("--- Opciones Extra ---"))
        self.check_fix = QCheckBox("Intentar reparar timestamps corruptos")
        self.check_fix.setChecked(True)
        advanced_layout.addWidget(self.check_fix)
        
        config_layout.addWidget(self.advanced_frame)
        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)
        
        # Botón de Acción Principal (Start)
        self.btn_start = QPushButton("🚀 Iniciar Conversión")
        self.btn_start.setMinimumHeight(50)
        self.btn_start.setProperty("class", "success_btn")
        self.btn_start.setStyleSheet("font-size: 16px; margin-top: 20px;")
        main_layout.addWidget(self.btn_start)
        
        # --- QUEUE PANEL EMBEDDED ---
        from ui.components.queue_panel import QueuePanel
        self.queue_panel = QueuePanel(self)
        main_layout.addWidget(self.queue_panel)
        
        if self.parent_window and hasattr(self.parent_window, 'register_queue_panel'):
            self.parent_window.register_queue_panel(self.queue_panel)
            
        main_layout.addStretch()
        self.setLayout(main_layout)

    def setup_connections(self):
        self.btn_add_file.clicked.connect(self.add_single_file)
        self.btn_add_multiple.clicked.connect(self.add_multiple_files)
        
        self.radio_same_folder.toggled.connect(lambda: self.line_output_folder.setEnabled(False))
        self.radio_custom_folder.toggled.connect(lambda: self.line_output_folder.setEnabled(True))
        self.btn_select_folder.clicked.connect(self.select_output_folder)
        
        self.btn_toggle_advanced.clicked.connect(self.toggle_advanced)
        self.combo_quality.currentIndexChanged.connect(self.update_crf_from_quality)
        self.btn_start.clicked.connect(self.start_process)
        
        # Recommended config connections
        self.combo_format.currentTextChanged.connect(self.on_format_changed)
        self.check_recommended.toggled.connect(self.on_recommended_toggled)
        self.check_gpu.toggled.connect(self.on_gpu_toggled)
        
        # Trigger initial state
        self.on_recommended_toggled(self.check_recommended.isChecked())

    def add_single_file(self):
        if self.parent_window: self.parent_window.add_single_file()

    def add_multiple_files(self):
        if self.parent_window: self.parent_window.add_multiple_files()

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de salida")
        if folder:
            self.output_folder = folder
            self.line_output_folder.setText(folder)
            self.radio_custom_folder.setChecked(True)

    def toggle_advanced(self, checked):
        self.advanced_frame.setVisible(checked)
        self.btn_toggle_advanced.setText("Ocultar Opciones Avanzadas ▲" if checked else "Mostrar Opciones Avanzadas ▼")
        
    def update_crf_from_quality(self, index):
        """Si se cambia la calidad simple, actualizamos el CRF avanzado"""
        crf_map = {0: 18, 1: 23, 2: 28}
        self.spin_crf.setValue(crf_map.get(index, 23))
        
        # Si cambiamos calidad manualmente y está recomendado activado, 
        # tal vez deberíamos desactivar "recomendado" o simplemente dejar que el usuario refine.
        # Por ahora, dejaremos que refine, pero si cambia de formato se reseteará.

    def on_format_changed(self, format_name):
        """Al cambiar el formato, aplicamos la recomendación si está activa"""
        if self.check_recommended.isChecked():
            self.apply_recommended_settings(format_name)

    def on_recommended_toggled(self, checked):
        """Habilita/Deshabilita controles manuales y aplica recomendación"""
        # Deshabilitamos controles manuales si 'Recomendado' está activo para evitar conflictos,
        # O podemos dejarlos habilitados para 'ajuste fino'. 
        # La solicitud dice: "si yo deselecciono la configuracion recomendada me permitira hacer la configuracion manual"
        # Esto implica que si está seleccionada, tal vez debería restringirse o al menos auto-ajustarse.
        
        self.combo_quality.setEnabled(not checked)
        self.combo_encoder.setEnabled(not checked) # En avanzado
        self.spin_crf.setEnabled(not checked)      # En avanzado
        # self.combo_preset.setEnabled(not checked) # Podríamos bloquear este también
        
        if checked:
            self.apply_recommended_settings(self.combo_format.currentText())

    def on_gpu_toggled(self, checked):
        """Si cambia estado GPU, reaplicamos recomendación si está activa"""
        if self.check_recommended.isChecked():
            self.apply_recommended_settings(self.combo_format.currentText())

    def apply_recommended_settings(self, format_name):
        """Aplica la configuración recomendada para un formato"""
        settings = self.RECOMMENDED_SETTINGS.get(format_name.lower())
        if not settings:
            return
            
        use_gpu = self.check_gpu.isChecked()
        
        # 1. Ajustar Codificador
        encoder = settings['encoder_gpu'] if use_gpu else settings['encoder_cpu']
        
        # Intentamos seleccionar el encoder en el combo avanzado si existe
        index = self.combo_encoder.findText(encoder, Qt.MatchFlag.MatchContains)
        if index >= 0:
            self.combo_encoder.setCurrentIndex(index)
        else:
            # Fallback simple
            if "nvenc" in encoder:
                idx = self.combo_encoder.findText("GPU", Qt.MatchFlag.MatchContains)
                if idx >= 0: self.combo_encoder.setCurrentIndex(idx)
            else:
                 idx = self.combo_encoder.findText("CPU", Qt.MatchFlag.MatchContains)
                 if idx >= 0: self.combo_encoder.setCurrentIndex(idx)

        # 2. Ajustar CRF / Calidad
        target_crf = settings['crf']
        self.spin_crf.setValue(target_crf)
        
        # Mapear CRF a las opciones de calidad simple si coincide
        # 18 -> Alta(0), 23 -> Media(1), 28 -> Baja(2)
        self.combo_quality.blockSignals(True)
        try:
            if target_crf <= 18:
                self.combo_quality.setCurrentIndex(0)
            elif target_crf <= 23:
                self.combo_quality.setCurrentIndex(1)
            else:
                self.combo_quality.setCurrentIndex(2)
        finally:
            self.combo_quality.blockSignals(False)

        # 3. Preset
        target_preset = settings['preset']
        preset_idx = self.combo_preset.findText(target_preset)
        if preset_idx >= 0:
            self.combo_preset.setCurrentIndex(preset_idx)

    def get_settings(self):
        """Retorna la configuración lista para procesar"""
        # Output Folder
        output_folder = self.output_folder if self.radio_custom_folder.isChecked() else None
        
        # Format
        out_fmt = self.combo_format.currentText()
        
        # Encoder logic
        # Si avanzado está visible, respetamos lo que diga ahí.
        # Si no, inferimos de "Usar GPU".
        is_advanced = self.btn_toggle_advanced.isChecked()
        
        if is_advanced:
            selected_enc = self.combo_encoder.currentText()
            preset = self.combo_preset.currentText()
            crf = self.spin_crf.value()
            
            # Map combo text to FFmpeg encoder name
            if "h264_nvenc" in selected_enc: encoder = "h264_nvenc"
            elif "hevc_nvenc" in selected_enc: encoder = "hevc_nvenc"
            elif "libx264" in selected_enc: encoder = "libx264"
            elif "hevc" in selected_enc: encoder = "libx265"
            else: # Automático
                encoder = "h264_nvenc" if self.check_gpu.isChecked() else "libx264"
        else:
            # Simple Mode
            encoder = "h264_nvenc" if self.check_gpu.isChecked() else "libx264"
            preset = "medium"
            # CRF mapped from quality combo
            crf = self.spin_crf.value() # This is already updated by update_crf_from_quality
            
        return {
            "output_folder": output_folder,
            "format": out_fmt,
            "encoder": encoder,
            "preset": preset,
            "crf": crf,
            "repair": self.check_fix.isChecked()
        }
        
    def start_process(self):
        """Inicia el proceso llamando al metodo de la ventana principal"""
        if self.parent_window:
             # Aquí podríamos invocar directamente algo como parent.start_queue(self.get_settings())
             # Pero para mantener compatibilidad, llamaremos a process_queue y dejaremos que 
             # él nos pregunte por los settings.
             # PEQUEÑO TRUCO: Reemplazamos el 'simple_tab' del parent con 'self' temporalmente 
             # o actualizamos el método get_encoder_settings para que coincida.
             self.parent_window.process_queue_unified(self.get_settings())
