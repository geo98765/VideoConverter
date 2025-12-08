"""Tab para unir múltiples videos"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QGroupBox, QFileDialog, QLabel, QComboBox,
                               QListWidget, QSpinBox)
from threads.join_thread import JoinThread
import os

class JoinTab(QWidget):
    """Tab para unir múltiples videos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.join_thread = None
        self.video_files = []
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Lista de videos
        list_group = QGroupBox("Videos a Unir")
        list_layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("➕ Agregar Videos")
        btn_add.clicked.connect(self.add_videos)
        btn_add.setMinimumHeight(40)
        btn_layout.addWidget(btn_add)
        
        btn_remove = QPushButton("➖ Quitar Seleccionado")
        btn_remove.clicked.connect(self.remove_selected)
        btn_remove.setMinimumHeight(40)
        btn_layout.addWidget(btn_remove)
        
        btn_clear = QPushButton("🗑️ Limpiar Lista")
        btn_clear.clicked.connect(self.clear_list)
        btn_clear.setMinimumHeight(40)
        btn_layout.addWidget(btn_clear)
        
        list_layout.addLayout(btn_layout)
        
        self.list_videos = QListWidget()
        self.list_videos.setMinimumHeight(200)
        list_layout.addWidget(self.list_videos)
        
        # Botones de orden
        order_layout = QHBoxLayout()
        btn_up = QPushButton("⬆️ Subir")
        btn_up.clicked.connect(self.move_up)
        order_layout.addWidget(btn_up)
        
        btn_down = QPushButton("⬇️ Bajar")
        btn_down.clicked.connect(self.move_down)
        order_layout.addWidget(btn_down)
        
        order_layout.addWidget(QLabel("(El orden importa - los videos se unirán en este orden)"))
        list_layout.addLayout(order_layout)
        
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
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
        
        # Botón de unión
        self.btn_join = QPushButton("🔗 Unir Videos")
        self.btn_join.clicked.connect(self.join_videos)
        self.btn_join.setMinimumHeight(50)
        self.btn_join.setEnabled(False)
        self.btn_join.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #00BCD4; color: white;")
        layout.addWidget(self.btn_join)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def add_videos(self):
        """Agrega videos a la lista"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar videos",
            "",
            "Videos (*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm *.m4v);;Todos (*.*)"
        )
        for file_path in file_paths:
            if file_path not in self.video_files:
                self.video_files.append(file_path)
                self.list_videos.addItem(os.path.basename(file_path))
                if self.parent_window:
                    self.parent_window.log(f"Agregado a unir: {os.path.basename(file_path)}")
        
        self.btn_join.setEnabled(len(self.video_files) >= 2)
    
    def remove_selected(self):
        """Quita el video seleccionado"""
        current_row = self.list_videos.currentRow()
        if current_row >= 0:
            self.list_videos.takeItem(current_row)
            self.video_files.pop(current_row)
            self.btn_join.setEnabled(len(self.video_files) >= 2)
    
    def clear_list(self):
        """Limpia la lista"""
        self.list_videos.clear()
        self.video_files.clear()
        self.btn_join.setEnabled(False)
    
    def move_up(self):
        """Mueve el video seleccionado hacia arriba"""
        current_row = self.list_videos.currentRow()
        if current_row > 0:
            item = self.list_videos.takeItem(current_row)
            self.list_videos.insertItem(current_row - 1, item)
            self.list_videos.setCurrentRow(current_row - 1)
            
            self.video_files[current_row], self.video_files[current_row - 1] = \
                self.video_files[current_row - 1], self.video_files[current_row]
    
    def move_down(self):
        """Mueve el video seleccionado hacia abajo"""
        current_row = self.list_videos.currentRow()
        if current_row >= 0 and current_row < self.list_videos.count() - 1:
            item = self.list_videos.takeItem(current_row)
            self.list_videos.insertItem(current_row + 1, item)
            self.list_videos.setCurrentRow(current_row + 1)
            
            self.video_files[current_row], self.video_files[current_row + 1] = \
                self.video_files[current_row + 1], self.video_files[current_row]
    
    def join_videos(self):
        """Une los videos"""
        if len(self.video_files) < 2:
            return
        
        if self.join_thread and self.join_thread.isRunning():
            return
        
        # Seleccionar archivo de salida
        output_file, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar video unido",
            "video_unido.mp4",
            "Videos (*.mp4 *.mkv *.avi)"
        )
        
        if not output_file:
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
        
        self.btn_join.setEnabled(False)
        
        # Crear thread
        self.join_thread = JoinThread(
            self.video_files,
            output_file,
            encoder,
            'medium',
            crf
        )
        
        self.join_thread.progress.connect(self.update_progress)
        self.join_thread.log_message.connect(self.log)
        self.join_thread.finished_signal.connect(self.join_finished)
        
        self.join_thread.start()
    
    def join_finished(self, success, message):
        """Callback cuando termina la unión"""
        self.btn_join.setEnabled(True)
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