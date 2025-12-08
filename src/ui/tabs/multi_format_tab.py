"""Tab para conversión a múltiples formatos"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QGroupBox, QFileDialog, QLabel, QCheckBox,
                               QTableWidget, QTableWidgetItem, QHeaderView, QComboBox)
from PyQt6.QtGui import QColor
from threads.multi_format_thread import MultiFormatThread
from core.multi_format_converter import MultiFormatConverter
import os

class MultiFormatTab(QWidget):
    """Tab para convertir a múltiples formatos simultáneamente"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.multi_thread = None
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
        
        # Selección de formatos
        format_group = QGroupBox("Formatos de Salida")
        format_layout = QVBoxLayout()
        
        info_label = QLabel("Seleccione los formatos a los que desea convertir:")
        format_layout.addWidget(info_label)
        
        # Tabla de formatos
        self.table_formats = QTableWidget()
        self.table_formats.setColumnCount(4)
        self.table_formats.setHorizontalHeaderLabels(["Formato", "Codificador", "CRF", "Estado"])
        self.table_formats.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_formats.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_formats.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_formats.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        # Agregar formatos comunes
        formats = [
            ('MP4', 'libx264', 23),
            ('MKV', 'libx264', 23),
            ('WebM', 'libvpx-vp9', 30),
            ('AVI', 'libx264', 23)
        ]
        
        for format_name, encoder, crf in formats:
            row = self.table_formats.rowCount()
            self.table_formats.insertRow(row)
            
            # Checkbox para formato
            check = QCheckBox(format_name)
            self.table_formats.setCellWidget(row, 0, check)
            
            # Codificador
            self.table_formats.setItem(row, 1, QTableWidgetItem(encoder))
            
            # CRF
            self.table_formats.setItem(row, 2, QTableWidgetItem(str(crf)))
            
            # Estado
            self.table_formats.setItem(row, 3, QTableWidgetItem("Pendiente"))
        
        format_layout.addWidget(self.table_formats)
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        # Botón de conversión
        self.btn_convert = QPushButton("🎬 Convertir a Formatos Seleccionados")
        self.btn_convert.clicked.connect(self.convert_formats)
        self.btn_convert.setMinimumHeight(50)
        self.btn_convert.setEnabled(False)
        self.btn_convert.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #673AB7; color: white;")
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
    
    def convert_formats(self):
        """Convierte a los formatos seleccionados"""
        if not self.current_file:
            return
        
        if self.multi_thread and self.multi_thread.isRunning():
            return
        
        # Obtener formatos seleccionados
        output_configs = []
        for row in range(self.table_formats.rowCount()):
            check_widget = self.table_formats.cellWidget(row, 0)
            if check_widget and check_widget.isChecked():
                format_name = check_widget.text().lower()
                encoder = self.table_formats.item(row, 1).text()
                crf = int(self.table_formats.item(row, 2).text())
                
                output_configs.append({
                    'format': format_name,
                    'encoder': encoder,
                    'crf': crf,
                    'preset': 'medium'
                })
                
                # Resetear estado
                self.table_formats.item(row, 3).setText("Procesando...")
                self.table_formats.item(row, 3).setForeground(QColor(0, 0, 255))
        
        if not output_configs:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", "No hay formatos seleccionados")
            return
        
        self.btn_convert.setEnabled(False)
        
        # Crear thread
        self.multi_thread = MultiFormatThread(
            self.current_file,
            output_configs
        )
        
        self.multi_thread.progress.connect(self.update_progress)
        self.multi_thread.log_message.connect(self.log)
        self.multi_thread.format_progress.connect(self.update_format_progress)
        self.multi_thread.format_finished.connect(self.format_finished)
        self.multi_thread.finished_signal.connect(self.all_finished)
        
        self.multi_thread.start()
    
    def update_format_progress(self, format_name, progress):
        """Actualiza progreso de un formato específico"""
        for row in range(self.table_formats.rowCount()):
            check_widget = self.table_formats.cellWidget(row, 0)
            if check_widget and check_widget.text().lower() == format_name.lower():
                self.table_formats.item(row, 3).setText(f"Procesando... {progress}%")
                break
    
    def format_finished(self, format_name, success, message):
        """Callback cuando termina un formato"""
        for row in range(self.table_formats.rowCount()):
            check_widget = self.table_formats.cellWidget(row, 0)
            if check_widget and check_widget.text().lower() == format_name.lower():
                item = self.table_formats.item(row, 3)
                if success:
                    item.setText("✅ Completado")
                    item.setForeground(QColor(0, 128, 0))
                else:
                    item.setText("❌ Error")
                    item.setForeground(QColor(255, 0, 0))
                break
    
    def all_finished(self, success, message):
        """Callback cuando terminan todas las conversiones"""
        self.btn_convert.setEnabled(True)
        if self.parent_window:
            self.parent_window.log(message)
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Completado", message)
    
    def update_progress(self, value):
        """Actualiza progreso global"""
        if self.parent_window:
            self.parent_window.update_progress(value)
    
    def log(self, message):
        """Log"""
        if self.parent_window:
            self.parent_window.log(message)