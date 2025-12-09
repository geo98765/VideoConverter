"""Ventana principal de la aplicación"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QProgressBar, QStackedWidget, 
                               QMessageBox, QSystemTrayIcon, QFileDialog, QTextEdit,
                               QTableWidgetItem, QScrollArea, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction

# Infrastructure
from ui.styles.theme_manager import ThemeManager
from ui.components.sidebar import Sidebar

# Views
from ui.views.dashboard_home import DashboardHome
from ui.views.conversion_view import ConversionView
from ui.views.tools_view import ToolsView
from ui.views.analysis_view import AnalysisView
from ui.tabs.queue_tab import QueueTab

# Logic
from threads.queue_processor_thread import QueueProcessorThread
from models.video_file import VideoFile
from utils.gpu_detector import detect_nvenc, get_gpu_info

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación - Rediseño Moderno"""
    
    def __init__(self):
        super().__init__()
        # 1. Initialize State Variables FIRST
        self.video_queue = []
        self.queue_panels = []  # Lista de paneles registrados para sincronizar
        self.queue_thread = None
        self.nvenc_available = False
        
        # 2. Initialize Infrastructure
        self.theme_manager = ThemeManager()
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        
        # 3. Initialize UI
        self.init_ui()
        self.detect_hardware()
        
        # 4. Apply default theme
        self.theme_manager.set_theme("dark")

    def init_ui(self):
        """Inicializa la interfaz de usuario moderna"""
        self.setWindowTitle("Video Tool Pro - Dashboard")
        self.setGeometry(100, 100, 1280, 800)
        self.setMinimumSize(624, 468) # Configuración de tamaño mínimo
        
        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)
        
        # 1. Sidebar (Left)
        self.sidebar = Sidebar()
        self.sidebar.page_changed.connect(self.switch_to_page)
        self.sidebar.theme_btn.clicked.connect(self.theme_manager.toggle_theme)
        main_layout.addWidget(self.sidebar)
        
        # 2. Main Content (Right)
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # 2a. Stacked Pages
        self.pages = QStackedWidget()
        
        # Helper to make pages scrollable
        def wrap_scroll(widget):
            from ui.components.smooth_scroll_area import SmoothScrollArea
            scroll = SmoothScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(widget)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            return scroll



        # Page 0: Dashboard
        self.dashboard = DashboardHome(self)
        self.pages.addWidget(wrap_scroll(self.dashboard))
        
        # Page 1: Conversion
        self.conversion_view = ConversionView(self)
        self.pages.addWidget(wrap_scroll(self.conversion_view))
        
        # Page 2: Tools
        self.tools_view = ToolsView(self)
        self.pages.addWidget(wrap_scroll(self.tools_view))
        
        # Page 3: Analysis
        self.analysis_view = AnalysisView(self)
        self.pages.addWidget(wrap_scroll(self.analysis_view))
        
        # Page 4: Settings
        from ui.views.settings_view import SettingsView
        self.settings_view = SettingsView(self)
        self.pages.addWidget(wrap_scroll(self.settings_view))
        
        # Page 5: Queue (Accessible via Dashboard)
        # We keep this for now but it might be redundant with global panel
        self.queue_view = QueueTab(self)
        self.pages.addWidget(wrap_scroll(self.queue_view))
        
        content_layout.addWidget(self.pages)
        
        # Global Progress Bar (Bottom Strip)
        self.status_bar_layout = QHBoxLayout()
        self.status_bar_layout.setContentsMargins(10, 5, 10, 5)
        self.status_bar_layout.setSpacing(10)
        
        self.label_status = QLabel("Listo")
        self.label_status.setStyleSheet("color: #6C7086; font-size: 11px;")
        self.status_bar_layout.addWidget(self.label_status)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False) # Hidden by default
        self.status_bar_layout.addWidget(self.progress_bar)
        
        # Queue Control Buttons (Show only when processing?)
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setFixedSize(80, 24)
        self.btn_cancel.setProperty("class", "danger_btn")
        self.btn_cancel.clicked.connect(self.cancel_process)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.setVisible(False) # Hidden by default
        self.status_bar_layout.addWidget(self.btn_cancel)
        
        content_layout.addLayout(self.status_bar_layout)
        
        main_layout.addLayout(content_layout)

        # Shortcuts logic mapping
        # Maps old references to new locations
        self.unified_tab = self.conversion_view.unified_tab
        self.simple_tab = self.conversion_view.unified_tab 
        # self.queue_tab logic should now point to... wait, we have both view and panel.
        # Let's keep queue_tab pointing to queue_view for legacy references (like accessing table_queue)
        # BUT we should sync them or prefer one.
        # Let's update methods to use queue_panel primarily.
        self.queue_tab = self.queue_view 

    def register_queue_panel(self, panel):
        """Registra un panel de cola para mantenerlo sincronizado"""
        self.queue_panels.append(panel)
        # Sincronizar estado inicial
        panel.request_clear.connect(self.clear_queue)
        panel.request_remove.connect(self.remove_from_queue_index)
        
        # Poblar con datos actuales si hay
        for video in self.video_queue:
            panel.add_row(video.name, video.get_size_formatted(), "Pendiente", video.path)
        panel.update_count(len(self.video_queue))

    def remove_from_queue_index(self, index):
        """Elimina por índice (usado por paneles)"""
        if index >= 0 and index < len(self.video_queue):
            video = self.video_queue.pop(index)
            
            # Sincronizar TODOS los paneles
            for p in self.queue_panels:
                p.remove_row(index)
                p.update_count(len(self.video_queue))
            
            # Sincronizar Tab Legacy
            self.queue_tab.table_queue.removeRow(index)
            self.queue_tab.update_count(len(self.video_queue))
            
            self.log(f"➖ Quitado: {video.name}")

    def process_queue_unified(self, settings):
        """Procesa la cola con settings unificados"""
        if not self.video_queue:
            QMessageBox.warning(self, "Cola vacía", "No hay videos en la cola")
            return
        
        if self.queue_thread and self.queue_thread.isRunning():
            QMessageBox.warning(self, "Procesando", "Ya hay un proceso en curso")
            return
            
        encoder = settings["encoder"]
        preset = settings["preset"]
        crf = settings["crf"]
        output_format = settings["format"]
        output_folder = settings["output_folder"]
        
        reply = QMessageBox.question(
            self, "Confirmar Conversión",
            f"¿Procesar {len(self.video_queue)} video(s)?\n\n"
            f"Codificador: {encoder}\n"
            f"Calidad (CRF): {crf}\n"
            f"Formato: {output_format}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        self.btn_cancel.setEnabled(True)
        self.btn_cancel.setVisible(True)
        self.progress_bar.setVisible(True)
        
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
        # Connect new detailed progress signal
        self.queue_thread.progress_update.connect(self.update_queue_progress)
        
        self.progress_bar.setValue(0)
        self.queue_thread.start()
        
        # Remove auto-navigation distinct from user request
        # self.toggle_queue_panel()

    def switch_to_page(self, index):
        self.pages.setCurrentIndex(index)
        
    def switch_to_tool(self, tool_name):
        # Switch to Tools page (Index 2)
        self.switch_to_page(2)
        # Select specific tool inside ToolsView
        self.tools_view.open_by_name(tool_name)

    def toggle_queue_panel(self):
        # Simply switch to the Queue Page (Index 5)
        self.pages.setCurrentIndex(5)

    def on_theme_changed(self, theme_name):
        self.label_status.setText(f"Tema cambiado a {theme_name}")

    def detect_hardware(self):
        """Detecta hardware disponible"""
        self.nvenc_available = detect_nvenc()
        gpus = get_gpu_info()
        
        if self.nvenc_available and gpus:
            gpu_text = f"✅ NVENC disponible - GPU: {gpus[0]}"
            self.simple_tab.check_gpu.setEnabled(True)
        else:
            gpu_text = "⚠️ NVENC no disponible - Solo se usará CPU"
            self.simple_tab.check_gpu.setEnabled(False)
            self.simple_tab.check_gpu.setChecked(False)
        
        self.label_status.setText(gpu_text)
    
    # --- LOGIC COPIED AND ADAPTED FROM ORIGINAL MAIN WINDOW ---
    
    def log(self, message):
        """Centralized logging (now status bar + potential detailed log)"""
        self.label_status.setText(message)
    
    def clear_queue(self):
        self.video_queue.clear()
        
        # Clear ALL panels
        for p in self.queue_panels:
            p.clear_table()
            p.update_count(0)
            
        # Legacy
        self.queue_tab.table_queue.setRowCount(0)
        self.queue_tab.update_count(0)
        
        self.log("Cola limpiada")

    def add_single_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Seleccionar Video", 
            "", 
            "Videos (*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm *.m4v);;Todos (*.*)"
        )
        if file_path:
            self.add_file_to_queue(file_path)

    def add_multiple_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "Seleccionar Videos", 
            "", 
            "Videos (*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm *.m4v);;Todos (*.*)"
        )
        if files:
            for f in files:
                self.add_file_to_queue(f)

    def add_file_to_queue(self, file_path):
        """Agrega un archivo a la cola y actualiza TODOS los paneles"""
        # Checar duplicados
        for video in self.video_queue:
            if video.path == file_path:
                return

        video = VideoFile(file_path)
        self.video_queue.append(video)
        
        # Actualizar TODOS los paneles
        for p in self.queue_panels:
            p.add_row(video.name, video.get_size_formatted(), "Pendiente", video.path)
            p.update_count(len(self.video_queue))
            
        # Actualizar Legacy Tab
        self.queue_tab.add_video_to_table(video)
        self.queue_tab.update_count(len(self.video_queue))
        
        self.log(f"➕ Agregado: {video.name}")

    def update_progress(self, val):
        self.progress_bar.setValue(val)

    def update_queue_progress(self, index, val):
        """Actualiza el progreso de una fila específica (item de cola)"""
        # Actualizar TODOS los paneles
        for p in self.queue_panels:
            p.update_progress(index, val)

    def update_current_file(self, filename):
        # Update Status in ALL panels?
        # This is tricky because we'd need to find the correct row index for this file
        # For simplicity, we can update status bar
        self.label_status.setText(f"Procesando: {filename}")
        
    def queue_item_finished(self, file_idx, success, message):
        """Actualiza el estado de un item en TODOS los paneles"""
        status_text = "Completado" if success else "Error"
        qt_color = Qt.GlobalColor.green if success else Qt.GlobalColor.red
            
        # Actualizar TODOS los paneles
        for p in self.queue_panels:
            p.update_status(file_idx, status_text, qt_color)
            
        # Legacy update (might behave differently)
        # self.queue_tab.update_status(file_idx, status_text)
    
    def queue_all_finished(self):
        self.progress_bar.setVisible(False)
        self.btn_cancel.setVisible(False)
        self.label_status.setText("✅ Todos los procesos terminados")
        QMessageBox.information(self, "Proceso Completado", "Todos los videos han sido procesados.")
        self.is_processing = False

    def cancel_process(self):
        if self.queue_thread and self.queue_thread.isRunning():
            self.queue_thread.stop()
            self.log("🛑 Cancelando proceso...")
            self.btn_cancel.setEnabled(False)