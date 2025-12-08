"""Ventana principal de la aplicación"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QFileDialog, QTextEdit,
                               QProgressBar, QGroupBox, QMessageBox, QTabWidget,
                               QTableWidgetItem)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

from ui.tabs.simple_config_tab import SimpleConfigTab
from ui.tabs.advanced_config_tab import AdvancedConfigTab
from ui.tabs.queue_tab import QueueTab
from threads.queue_processor_thread import QueueProcessorThread
from models.video_file import VideoFile
from utils.gpu_detector import detect_nvenc, get_gpu_info

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    
    def __init__(self):
        super().__init__()
        self.video_queue = []
        self.queue_thread = None
        self.nvenc_available = False
        self.init_ui()
        self.detect_hardware()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Video Tool Pro - Conversor y Reparador")
        self.setGeometry(100, 100, 1100, 850)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Título
        title = QLabel("Video Tool Pro - Conversor y Reparador de Videos")
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Información del sistema
        system_group = QGroupBox("Información del Sistema")
        system_layout = QVBoxLayout()
        self.label_gpu = QLabel("Detectando hardware...")
        system_layout.addWidget(self.label_gpu)
        system_group.setLayout(system_layout)
        main_layout.addWidget(system_group)
        
        # Tabs
        # Tabs
        self.tabs = QTabWidget()
        
        self.simple_tab = SimpleConfigTab(self)
        self.tabs.addTab(self.simple_tab, "⚙️ Configuración Recomendada")
        
        self.advanced_tab = AdvancedConfigTab(self)
        self.tabs.addTab(self.advanced_tab, "🔧 Configuración Avanzada")
        
        self.queue_tab = QueueTab(self)
        self.tabs.addTab(self.queue_tab, "📋 Cola de Videos")
        
        # NUEVOS TABS - FASE 1
        from ui.tabs.analysis_tab import AnalysisTab
        from ui.tabs.audio_extract_tab import AudioExtractTab
        from ui.tabs.resolution_tab import ResolutionTab
        from ui.tabs.compress_tab import CompressTab
        from ui.tabs.join_tab import JoinTab
        from ui.tabs.subtitle_tab import SubtitleTab
        from ui.tabs.corruption_tab import CorruptionTab
        from ui.tabs.device_profile_tab import DeviceProfileTab
        from ui.tabs.multi_format_tab import MultiFormatTab
        from ui.tabs.pausable_tab import PausableTab

        self.profile_tab = DeviceProfileTab(self)
        self.tabs.addTab(self.profile_tab, "📱 Perfiles de Dispositivo")
        
        self.multi_format_tab = MultiFormatTab(self)
        self.tabs.addTab(self.multi_format_tab, "🎯 Múltiples Formatos")
        
        self.pausable_tab = PausableTab(self)
        self.tabs.addTab(self.pausable_tab, "⏯️ Conversión Pausable")
        
        self.compress_tab = CompressTab(self)
        self.tabs.addTab(self.compress_tab, "🗜️ Comprimir Video")
        
        self.join_tab = JoinTab(self)
        self.tabs.addTab(self.join_tab, "🔗 Unir Videos")
        
        self.subtitle_tab = SubtitleTab(self)
        self.tabs.addTab(self.subtitle_tab, "📝 Subtítulos")
        
        self.corruption_tab = CorruptionTab(self)
        self.tabs.addTab(self.corruption_tab, "🔍 Detectar Corrupción")

        self.analysis_tab = AnalysisTab(self)
        self.tabs.addTab(self.analysis_tab, "🔍 Análisis de Video")
        
        self.audio_tab = AudioExtractTab(self)
        self.tabs.addTab(self.audio_tab, "🎵 Extraer Audio")
        
        self.resolution_tab = ResolutionTab(self)
        self.tabs.addTab(self.resolution_tab, "📐 Cambiar Resolución")
        main_layout.addWidget(self.tabs)
        
        # Progreso
        progress_group = QGroupBox("Progreso")
        progress_layout = QVBoxLayout()
        
        self.label_current_file = QLabel("Esperando...")
        progress_layout.addWidget(self.label_current_file)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)
        
        # Botones de control
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
        
        # Logs
        log_label = QLabel("📝 Registro de actividad:")
        main_layout.addWidget(log_label)
        
        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        self.text_log.setMaximumHeight(180)
        main_layout.addWidget(self.text_log)
        
        self.btn_clear_log = QPushButton("🗑️ Limpiar registro")
        self.btn_clear_log.clicked.connect(self.clear_log)
        main_layout.addWidget(self.btn_clear_log)
    
    def detect_hardware(self):
        """Detecta hardware disponible"""
        self.nvenc_available = detect_nvenc()
        gpus = get_gpu_info()
        
        if self.nvenc_available and gpus:
            gpu_text = f"✅ NVENC disponible - GPU: {gpus[0]}"
            self.simple_tab.check_use_gpu.setEnabled(True)
        else:
            gpu_text = "⚠️ NVENC no disponible - Solo se usará CPU"
            self.simple_tab.check_use_gpu.setEnabled(False)
            self.simple_tab.check_use_gpu.setChecked(False)
        
        self.label_gpu.setText(gpu_text)
        self.log(gpu_text)
    
    def add_single_file(self):
        """Agrega un archivo a la cola"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar video",
            "",
            "Videos (*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm *.m4v);;Todos (*.*)"
        )
        if file_path:
            self.add_file_to_queue(file_path)
    
    def add_multiple_files(self):
        """Agrega múltiples archivos a la cola"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar videos",
            "",
            "Videos (*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm *.m4v);;Todos (*.*)"
        )
        for file_path in file_paths:
            self.add_file_to_queue(file_path)
    
    def add_file_to_queue(self, file_path):
        """Agrega un archivo a la cola"""
        # Verificar duplicados
        for video in self.video_queue:
            if video.path == file_path:
                self.log(f"⚠️ Ya está en cola: {video.name}")
                return
        
        video_file = VideoFile(file_path)
        self.video_queue.append(video_file)
        
        # Agregar a tabla
        row = self.queue_tab.table_queue.rowCount()
        self.queue_tab.table_queue.insertRow(row)
        self.queue_tab.table_queue.setItem(row, 0, QTableWidgetItem(video_file.name))
        self.queue_tab.table_queue.setItem(row, 1, QTableWidgetItem(video_file.get_size_formatted()))
        self.queue_tab.table_queue.setItem(row, 2, QTableWidgetItem("Pendiente"))
        self.queue_tab.table_queue.setItem(row, 3, QTableWidgetItem(file_path))
        
        self.queue_tab.update_count(len(self.video_queue))
        self.log(f"✅ Agregado: {video_file.name}")
    
    def clear_queue(self):
        """Limpia la cola"""
        if self.video_queue:
            reply = QMessageBox.question(
                self, "Confirmar", "¿Limpiar cola?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.video_queue.clear()
                self.queue_tab.table_queue.setRowCount(0)
                self.queue_tab.update_count(0)
                self.log("🗑️ Cola limpiada")
    
    def remove_selected_from_queue(self):
        """Quita elemento seleccionado"""
        current_row = self.queue_tab.table_queue.currentRow()
        if current_row >= 0:
            file_name = self.queue_tab.table_queue.item(current_row, 0).text()
            self.queue_tab.table_queue.removeRow(current_row)
            self.video_queue.pop(current_row)
            self.queue_tab.update_count(len(self.video_queue))
            self.log(f"➖ Quitado: {file_name}")
    
    def process_queue(self):
        """Procesa la cola"""
        if not self.video_queue:
            QMessageBox.warning(self, "Cola vacía", "No hay videos en la cola")
            return
        
        if self.queue_thread and self.queue_thread.isRunning():
            QMessageBox.warning(self, "Procesando", "Ya hay un proceso en curso")
            return
        
        # Obtener configuración
        encoder, preset, crf, output_format = self.simple_tab.get_encoder_settings()
        output_folder = self.simple_tab.get_output_folder()
        
        reply = QMessageBox.question(
            self, "Confirmar",
            f"¿Procesar {len(self.video_queue)} video(s)?\n\n"
            f"Codificador: {encoder}\nCRF: {crf}\nFormato: {output_format}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        self.btn_process_queue.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        
        self.queue_thread = QueueProcessorThread(
            self.video_queue.copy(),
            output_folder,
            encoder,
            preset,
            crf,
            output_format
        )
        
        self.queue_thread.progress.connect(self.update_progress)
        self.queue_thread.log_message.connect(self.log)
        self.queue_thread.item_finished.connect(self.queue_item_finished)
        self.queue_thread.all_finished.connect(self.queue_all_finished)
        self.queue_thread.current_file.connect(self.update_current_file)
        
        self.progress_bar.setValue(0)
        self.queue_thread.start()
    
    def queue_item_finished(self, index, success, message):
        """Item procesado"""
        if index < self.queue_tab.table_queue.rowCount():
            status_item = QTableWidgetItem(message)
            if success:
                status_item.setForeground(QColor(0, 128, 0))
            else:
                status_item.setForeground(QColor(255, 0, 0))
            self.queue_tab.table_queue.setItem(index, 2, status_item)
    
    def queue_all_finished(self, total, successful):
        """Cola completada"""
        self.btn_process_queue.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.label_current_file.setText("Completado")
        
        QMessageBox.information(
            self, "Completado",
            f"Procesados {successful}/{total} videos exitosamente"
        )
    
    def update_current_file(self, filename):
        """Actualiza archivo actual"""
        self.label_current_file.setText(f"Procesando: {filename}")
    
    def cancel_process(self):
        """Cancela proceso"""
        if self.queue_thread and self.queue_thread.isRunning():
            reply = QMessageBox.question(
                self, "Cancelar", "¿Cancelar procesamiento?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.queue_thread.stop()
                self.log("⚠️ Cancelando...")
    
    def update_progress(self, value):
        """Actualiza progreso"""
        self.progress_bar.setValue(value)
    
    def log(self, message):
        """Agrega log"""
        self.text_log.append(message)
        self.text_log.verticalScrollBar().setValue(
            self.text_log.verticalScrollBar().maximum()
        )
    
    def clear_log(self):
        """Limpia log"""
        self.text_log.clear()
        self.log("📋 Registro limpiado")