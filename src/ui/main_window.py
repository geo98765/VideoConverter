from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QFileDialog, QComboBox, 
                               QTextEdit, QProgressBar, QGroupBox, QSpinBox,
                               QMessageBox, QTableWidget, QTableWidgetItem,
                               QHeaderView, QCheckBox, QLineEdit, QRadioButton,
                               QButtonGroup, QTabWidget)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor
from utils.gpu_detector import detect_nvenc, get_gpu_info
from utils.ffmpeg_wrapper import FFmpegWrapper
import os
import re

class ConversionThread(QThread):
    """Thread para ejecutar conversión sin bloquear la UI"""
    progress = pyqtSignal(int)
    log_message = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, input_file, output_file, encoder, preset='medium', crf=23):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.encoder = encoder
        self.preset = preset
        self.crf = crf
        self.is_running = True
    
    def run(self):
        """Ejecuta la conversión"""
        try:
            self.log_message.emit(f"🎬 Iniciando conversión...")
            self.log_message.emit(f"   Archivo: {os.path.basename(self.input_file)}")
            self.log_message.emit(f"   Codificador: {self.encoder}")
            self.log_message.emit(f"   Preset: {self.preset}")
            
            # Obtener duración total del video
            duration = FFmpegWrapper.get_video_duration(self.input_file)
            if duration > 0:
                self.log_message.emit(f"   Duración: {duration:.2f} segundos")
            
            # Iniciar conversión
            process = FFmpegWrapper.convert_video(
                self.input_file, 
                self.output_file, 
                self.encoder, 
                self.preset,
                self.crf
            )
            
            if not process:
                self.finished_signal.emit(False, "Error al iniciar FFmpeg")
                return
            
            # Leer progreso
            for line in process.stderr:
                if not self.is_running:
                    process.kill()
                    self.finished_signal.emit(False, "Conversión cancelada")
                    return
                
                # Buscar tiempo actual en la salida de FFmpeg
                time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
                if time_match and duration > 0:
                    hours = int(time_match.group(1))
                    minutes = int(time_match.group(2))
                    seconds = float(time_match.group(3))
                    current_time = hours * 3600 + minutes * 60 + seconds
                    
                    progress_percent = int((current_time / duration) * 100)
                    self.progress.emit(min(progress_percent, 100))
            
            process.wait()
            
            if process.returncode == 0:
                self.progress.emit(100)
                self.finished_signal.emit(True, "✅ Conversión completada exitosamente")
            else:
                self.finished_signal.emit(False, "❌ Error durante la conversión")
                
        except Exception as e:
            self.finished_signal.emit(False, f"❌ Error: {str(e)}")
    
    def stop(self):
        """Detiene la conversión"""
        self.is_running = False

class QueueProcessorThread(QThread):
    """Thread para procesar cola de videos"""
    progress = pyqtSignal(int)
    log_message = pyqtSignal(str)
    item_finished = pyqtSignal(int, bool, str)  # index, success, message
    all_finished = pyqtSignal(int, int)  # total, successful
    current_file = pyqtSignal(str)  # nombre del archivo actual
    
    def __init__(self, queue_items, output_folder, encoder, preset, crf, output_format):
        super().__init__()
        self.queue_items = queue_items
        self.output_folder = output_folder
        self.encoder = encoder
        self.preset = preset
        self.crf = crf
        self.output_format = output_format
        self.is_running = True
    
    def run(self):
        """Procesa toda la cola"""
        total = len(self.queue_items)
        successful = 0
        
        self.log_message.emit(f"🎬 Iniciando procesamiento de cola: {total} archivos")
        
        for index, item in enumerate(self.queue_items):
            if not self.is_running:
                self.log_message.emit("⚠️ Procesamiento de cola cancelado")
                break
            
            input_file = item['path']
            filename = os.path.basename(input_file)
            base_name = os.path.splitext(filename)[0]
            
            # Generar nombre de salida
            if self.output_folder:
                output_file = os.path.join(self.output_folder, f"{base_name}_converted.{self.output_format}")
            else:
                output_dir = os.path.dirname(input_file)
                output_file = os.path.join(output_dir, f"{base_name}_converted.{self.output_format}")
            
            self.current_file.emit(filename)
            self.log_message.emit(f"\n{'='*50}")
            self.log_message.emit(f"📹 Procesando [{index+1}/{total}]: {filename}")
            
            try:
                # Obtener duración
                duration = FFmpegWrapper.get_video_duration(input_file)
                if duration > 0:
                    self.log_message.emit(f"   Duración: {duration:.2f} segundos")
                
                # Convertir
                process = FFmpegWrapper.convert_video(
                    input_file,
                    output_file,
                    self.encoder,
                    self.preset,
                    self.crf
                )
                
                if not process:
                    self.log_message.emit(f"❌ Error al iniciar conversión de {filename}")
                    self.item_finished.emit(index, False, "Error al iniciar")
                    continue
                
                # Leer progreso
                for line in process.stderr:
                    if not self.is_running:
                        process.kill()
                        break
                    
                    time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
                    if time_match and duration > 0:
                        hours = int(time_match.group(1))
                        minutes = int(time_match.group(2))
                        seconds = float(time_match.group(3))
                        current_time = hours * 3600 + minutes * 60 + seconds
                        
                        progress_percent = int((current_time / duration) * 100)
                        self.progress.emit(min(progress_percent, 100))
                
                process.wait()
                
                if process.returncode == 0:
                    self.log_message.emit(f"✅ {filename} - Conversión exitosa")
                    self.item_finished.emit(index, True, "Exitoso")
                    successful += 1
                else:
                    self.log_message.emit(f"❌ {filename} - Error en conversión")
                    self.item_finished.emit(index, False, "Error")
                    
            except Exception as e:
                self.log_message.emit(f"❌ {filename} - Error: {str(e)}")
                self.item_finished.emit(index, False, f"Error: {str(e)}")
            
            self.progress.emit(0)
        
        self.all_finished.emit(total, successful)
        self.log_message.emit(f"\n{'='*50}")
        self.log_message.emit(f"🏁 Procesamiento completado: {successful}/{total} exitosos")
    
    def stop(self):
        """Detiene el procesamiento"""
        self.is_running = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_file = None
        self.conversion_thread = None
        self.queue_thread = None
        self.output_folder = None
        self.video_queue = []
        self.nvenc_available = False
        self.init_ui()
        self.detect_hardware()
    
    def init_ui(self):
        self.setWindowTitle("Video Tool Pro - Conversor y Reparador")
        self.setGeometry(100, 100, 1100, 850)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Título
        title = QLabel("Video Tool Pro - Conversor y Reparador de Videos")
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Grupo: Información del sistema
        system_group = QGroupBox("Información del Sistema")
        system_layout = QVBoxLayout()
        self.label_gpu = QLabel("Detectando hardware...")
        system_layout.addWidget(self.label_gpu)
        system_group.setLayout(system_layout)
        main_layout.addWidget(system_group)
        
        # Tabs para configuración
        tabs = QTabWidget()
        
        # Tab 1: Configuración Simple
        tab_simple = QWidget()
        self.setup_simple_tab(tab_simple)
        tabs.addTab(tab_simple, "⚙️ Configuración Recomendada")
        
        # Tab 2: Configuración Avanzada
        tab_advanced = QWidget()
        self.setup_advanced_tab(tab_advanced)
        tabs.addTab(tab_advanced, "🔧 Configuración Avanzada")
        
        # Tab 3: Cola de Videos
        tab_queue = QWidget()
        self.setup_queue_tab(tab_queue)
        tabs.addTab(tab_queue, "📋 Cola de Videos")
        
        main_layout.addWidget(tabs)
        
        # Barra de progreso global
        progress_group = QGroupBox("Progreso")
        progress_layout = QVBoxLayout()
        
        self.label_current_file = QLabel("Esperando...")
        progress_layout.addWidget(self.label_current_file)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)
        
        # Botones de control global
        control_layout = QHBoxLayout()
        
        self.btn_process_queue = QPushButton("▶️ Procesar Cola")
        self.btn_process_queue.clicked.connect(self.process_queue)
        self.btn_process_queue.setMinimumHeight(50)
        self.btn_process_queue.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #4CAF50; color: white;")
        control_layout.addWidget(self.btn_process_queue)
        
        self.btn_cancel = QPushButton("❌ Cancelar")
        self.btn_cancel.clicked.connect(self.cancel_process)
        self.btn_cancel.setMinimumHeight(50)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.setStyleSheet("font-size: 14px; background-color: #f44336; color: white;")
        control_layout.addWidget(self.btn_cancel)
        
        main_layout.addLayout(control_layout)
        
        # Área de logs
        log_label = QLabel("📝 Registro de actividad:")
        main_layout.addWidget(log_label)
        
        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        self.text_log.setMaximumHeight(180)
        main_layout.addWidget(self.text_log)
        
        # Botón para limpiar logs
        self.btn_clear_log = QPushButton("🗑️ Limpiar registro")
        self.btn_clear_log.clicked.connect(self.clear_log)
        main_layout.addWidget(self.btn_clear_log)
    
    def setup_simple_tab(self, tab):
        """Configura el tab de configuración simple"""
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
        tab.setLayout(layout)
    
    def setup_advanced_tab(self, tab):
        """Configura el tab de configuración avanzada"""
        layout = QVBoxLayout()
        
        # Opciones avanzadas
        advanced_group = QGroupBox("Configuración Avanzada de Codificación")
        advanced_layout = QVBoxLayout()
        
        # Forzar modo
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
        
        # Formato de salida
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
        tab.setLayout(layout)
    
    def setup_queue_tab(self, tab):
        """Configura el tab de cola de videos"""
        layout = QVBoxLayout()
        
        # Tabla de cola
        queue_group = QGroupBox("Cola de Procesamiento")
        queue_layout = QVBoxLayout()
        
        self.table_queue = QTableWidget()
        self.table_queue.setColumnCount(4)
        self.table_queue.setHorizontalHeaderLabels(["Archivo", "Tamaño", "Estado", "Ruta Completa"])
        self.table_queue.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_queue.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_queue.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_queue.setColumnHidden(3, True)  # Ocultar ruta completa
        queue_layout.addWidget(self.table_queue)
        
        # Botones de gestión de cola
        queue_buttons = QHBoxLayout()
        
        btn_clear_queue = QPushButton("🗑️ Limpiar Cola")
        btn_clear_queue.clicked.connect(self.clear_queue)
        queue_buttons.addWidget(btn_clear_queue)
        
        btn_remove_selected = QPushButton("➖ Quitar Seleccionado")
        btn_remove_selected.clicked.connect(self.remove_selected_from_queue)
        queue_buttons.addWidget(btn_remove_selected)
        
        self.label_queue_count = QLabel("Videos en cola: 0")
        self.label_queue_count.setStyleSheet("font-weight: bold;")
        queue_buttons.addWidget(self.label_queue_count)
        
        queue_buttons.addStretch()
        queue_layout.addLayout(queue_buttons)
        
        queue_group.setLayout(queue_layout)
        layout.addWidget(queue_group)
        
        tab.setLayout(layout)
    
    def detect_hardware(self):
        """Detecta el hardware disponible"""
        self.nvenc_available = detect_nvenc()
        gpus = get_gpu_info()
        
        if self.nvenc_available and gpus:
            gpu_text = f"✅ NVENC disponible - GPU: {gpus[0]}"
            self.check_use_gpu.setEnabled(True)
        else:
            gpu_text = "⚠️ NVENC no disponible - Solo se usará CPU"
            self.check_use_gpu.setEnabled(False)
            self.check_use_gpu.setChecked(False)
        
        self.label_gpu.setText(gpu_text)
        self.log(gpu_text)
    
    def add_single_file(self):
        """Agrega un solo archivo a la cola"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar video",
            "",
            "Videos (*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm *.m4v);;Todos los archivos (*.*)"
        )
        if file_path:
            self.add_file_to_queue(file_path)
    
    def add_multiple_files(self):
        """Agrega múltiples archivos a la cola"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar videos",
            "",
            "Videos (*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm *.m4v);;Todos los archivos (*.*)"
        )
        for file_path in file_paths:
            self.add_file_to_queue(file_path)
    
    def add_file_to_queue(self, file_path):
        """Agrega un archivo a la cola"""
        # Verificar si ya existe
        for item in self.video_queue:
            if item['path'] == file_path:
                self.log(f"⚠️ El archivo ya está en la cola: {os.path.basename(file_path)}")
                return
        
        # Obtener información del archivo
        file_size = os.path.getsize(file_path)
        size_mb = file_size / (1024 * 1024)
        
        # Agregar a la lista
        queue_item = {
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': f"{size_mb:.2f} MB",
            'status': 'Pendiente'
        }
        self.video_queue.append(queue_item)
        
        # Agregar a la tabla
        row = self.table_queue.rowCount()
        self.table_queue.insertRow(row)
        self.table_queue.setItem(row, 0, QTableWidgetItem(queue_item['name']))
        self.table_queue.setItem(row, 1, QTableWidgetItem(queue_item['size']))
        self.table_queue.setItem(row, 2, QTableWidgetItem(queue_item['status']))
        self.table_queue.setItem(row, 3, QTableWidgetItem(file_path))
        
        self.update_queue_count()
        self.log(f"✅ Agregado a la cola: {queue_item['name']}")
    
    def clear_queue(self):
        """Limpia toda la cola"""
        if self.video_queue:
            reply = QMessageBox.question(
                self,
                "Confirmar",
                "¿Desea limpiar toda la cola?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.video_queue.clear()
                self.table_queue.setRowCount(0)
                self.update_queue_count()
                self.log("🗑️ Cola limpiada")
    
    def remove_selected_from_queue(self):
        """Quita el elemento seleccionado de la cola"""
        current_row = self.table_queue.currentRow()
        if current_row >= 0:
            file_name = self.table_queue.item(current_row, 0).text()
            self.table_queue.removeRow(current_row)
            self.video_queue.pop(current_row)
            self.update_queue_count()
            self.log(f"➖ Quitado de la cola: {file_name}")
    
    def update_queue_count(self):
        """Actualiza el contador de cola"""
        count = len(self.video_queue)
        self.label_queue_count.setText(f"Videos en cola: {count}")
    
    def select_output_folder(self):
        """Selecciona carpeta de salida"""
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de salida")
        if folder:
            self.output_folder = folder
            self.line_output_folder.setText(folder)
            self.radio_custom_folder.setChecked(True)
            self.log(f"📁 Carpeta de salida: {folder}")
    
    def get_encoder_settings(self):
        """Obtiene la configuración del codificador según el modo activo"""
        # Determinar si usar configuración simple o avanzada
        # Para este ejemplo, usaremos la configuración simple como base
        
        if self.check_use_gpu.isChecked() and self.nvenc_available:
            encoder = "h264_nvenc"
        else:
            encoder = "libx264"
        
        # Mapear calidad simple a CRF
        quality_map = {
            "Alta (CRF 18)": 18,
            "Media (CRF 23) - Recomendado": 23,
            "Baja (CRF 28)": 28
        }
        crf = quality_map.get(self.combo_quality_simple.currentText(), 23)
        preset = "medium"
        output_format = self.combo_format_simple.currentText()
        
        return encoder, preset, crf, output_format
    
    def get_output_folder(self):
        """Obtiene la carpeta de salida configurada"""
        if self.radio_custom_folder.isChecked() and self.output_folder:
            return self.output_folder
        return None
    
    def process_queue(self):
        """Procesa toda la cola de videos"""
        if not self.video_queue:
            QMessageBox.warning(self, "Cola vacía", "No hay videos en la cola para procesar")
            return
        
        if self.queue_thread and self.queue_thread.isRunning():
            QMessageBox.warning(self, "Procesando", "Ya hay un procesamiento en curso")
            return
        
        # Obtener configuración
        encoder, preset, crf, output_format = self.get_encoder_settings()
        output_folder = self.get_output_folder()
        
        # Confirmar inicio
        reply = QMessageBox.question(
            self,
            "Confirmar procesamiento",
            f"¿Iniciar procesamiento de {len(self.video_queue)} video(s)?\n\n"
            f"Codificador: {encoder}\n"
            f"Calidad (CRF): {crf}\n"
            f"Formato: {output_format}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        # Deshabilitar botones
        self.btn_process_queue.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        
        # Crear thread de procesamiento
        self.queue_thread = QueueProcessorThread(
            self.video_queue.copy(),
            output_folder,
            encoder,
            preset,
            crf,
            output_format
        )
        
        # Conectar señales
        self.queue_thread.progress.connect(self.update_progress)
        self.queue_thread.log_message.connect(self.log)
        self.queue_thread.item_finished.connect(self.queue_item_finished)
        self.queue_thread.all_finished.connect(self.queue_all_finished)
        self.queue_thread.current_file.connect(self.update_current_file)
        
        # Iniciar
        self.progress_bar.setValue(0)
        self.queue_thread.start()
    
    def queue_item_finished(self, index, success, message):
        """Actualiza el estado de un item en la tabla"""
        if index < self.table_queue.rowCount():
            status_item = QTableWidgetItem(message)
            if success:
                status_item.setForeground(QColor(0, 128, 0))  # Verde
            else:
                status_item.setForeground(QColor(255, 0, 0))  # Rojo
            self.table_queue.setItem(index, 2, status_item)
    
    def queue_all_finished(self, total, successful):
        """Callback cuando termina el procesamiento de toda la cola"""
        self.btn_process_queue.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.label_current_file.setText("Procesamiento completado")
        
        QMessageBox.information(
            self,
            "Procesamiento completado",
            f"Se procesaron {successful} de {total} videos exitosamente"
        )
    
    def update_current_file(self, filename):
        """Actualiza el nombre del archivo actual"""
        self.label_current_file.setText(f"Procesando: {filename}")
    
    def cancel_process(self):
        """Cancela el proceso actual"""
        if self.queue_thread and self.queue_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "Cancelar",
                "¿Desea cancelar el procesamiento?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.queue_thread.stop()
                self.log("⚠️ Cancelando procesamiento...")
    
    def update_progress(self, value):
        """Actualiza la barra de progreso"""
        self.progress_bar.setValue(value)
    
    def log(self, message):
        """Agrega mensaje al área de logs"""
        self.text_log.append(message)
        self.text_log.verticalScrollBar().setValue(
            self.text_log.verticalScrollBar().maximum()
        )
    
    def clear_log(self):
        """Limpia el área de logs"""
        self.text_log.clear()
        self.log("📋 Registro limpiado")