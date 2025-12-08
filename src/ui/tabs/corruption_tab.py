"""Tab para detectar y reparar videos corruptos"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QGroupBox, QFileDialog, QLabel, QTextEdit)
from threads.corruption_thread import CorruptionThread
from core.corruption_detector import CorruptionDetector
import os

class CorruptionTab(QWidget):
    """Tab para detectar y reparar videos corruptos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.corruption_thread = None
        self.current_file = None
        self.analysis_result = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Selector de archivo
        file_group = QGroupBox("Video a Analizar")
        file_layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()
        btn_select = QPushButton("📁 Seleccionar Video")
        btn_select.clicked.connect(self.select_file)
        btn_select.setMinimumHeight(40)
        btn_layout.addWidget(btn_select)
        
        self.btn_analyze = QPushButton("🔍 Analizar Video")
        self.btn_analyze.clicked.connect(self.analyze_video)
        self.btn_analyze.setMinimumHeight(40)
        self.btn_analyze.setEnabled(False)
        btn_layout.addWidget(self.btn_analyze)
        
        file_layout.addLayout(btn_layout)
        
        self.label_file = QLabel("No hay archivo seleccionado")
        self.label_file.setStyleSheet("padding: 10px; background-color: #f0f0f0;")
        file_layout.addWidget(self.label_file)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Resultado del análisis
        result_group = QGroupBox("Resultado del Análisis")
        result_layout = QVBoxLayout()
        
        self.text_result = QTextEdit()
        self.text_result.setReadOnly(True)
        self.text_result.setPlaceholderText("Los resultados aparecerán aquí...")
        result_layout.addWidget(self.text_result)
        
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        # Botón de reparación
        self.btn_repair = QPushButton("🔧 Intentar Reparar")
        self.btn_repair.clicked.connect(self.repair_video)
        self.btn_repair.setMinimumHeight(50)
        self.btn_repair.setEnabled(False)
        self.btn_repair.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #FF5722; color: white;")
        layout.addWidget(self.btn_repair)
        
        self.setLayout(layout)
    
    def select_file(self):
        """Selecciona archivo para analizar"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar video",
            "",
            "Videos (*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm *.m4v);;Todos (*.*)"
        )
        if file_path:
            self.current_file = file_path
            self.label_file.setText(f"📄 {file_path}")
            self.btn_analyze.setEnabled(True)
            self.btn_repair.setEnabled(False)
            self.text_result.clear()
            if self.parent_window:
                self.parent_window.log(f"Archivo seleccionado para análisis: {file_path}")
    
    def analyze_video(self):
        """Analiza el video en busca de corrupción"""
        if not self.current_file:
            return
        
        if self.corruption_thread and self.corruption_thread.isRunning():
            return
        
        self.btn_analyze.setEnabled(False)
        self.btn_repair.setEnabled(False)
        self.text_result.clear()
        
        # Crear thread
        self.corruption_thread = CorruptionThread(self.current_file)
        self.corruption_thread.progress.connect(self.update_progress)
        self.corruption_thread.log_message.connect(self.log)
        self.corruption_thread.analysis_complete.connect(self.show_analysis)
        self.corruption_thread.finished_signal.connect(self.analysis_finished)
        
        self.corruption_thread.start()
    
    def show_analysis(self, result):
        """Muestra el resultado del análisis"""
        self.analysis_result = result
        
        # Generar reporte
        report = CorruptionDetector.get_corruption_report(result)
        self.text_result.setText(report)
        
        # Habilitar botón de reparación si hay problemas
        if result['status'] in ['minor_issues', 'moderate_corruption', 'severe_corruption']:
            self.btn_repair.setEnabled(True)
    
    def analysis_finished(self, success, message):
        """Callback cuando termina el análisis"""
        self.btn_analyze.setEnabled(True)
        if self.parent_window:
            self.parent_window.log(message)
    
    def repair_video(self):
        """Intenta reparar el video"""
        if not self.current_file:
            return
        
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            "Reparar video",
            "¿Desea intentar reparar el video?\n\n"
            "Nota: La reparación puede tardar varios minutos.\n"
            "Se creará un nuevo archivo con el sufijo '_repaired'.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        # Generar nombre de salida
        base_name = os.path.splitext(self.current_file)[0]
        ext = os.path.splitext(self.current_file)[1]
        output_file = f"{base_name}_repaired{ext}"
        
        if os.path.exists(output_file):
            reply = QMessageBox.question(
                self, "Archivo existe",
                f"El archivo reparado ya existe. ¿Sobrescribir?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        self.btn_repair.setEnabled(False)
        
        # Usar el mismo thread de reparación que ya teníamos
        from threads.base_thread import BaseThread
        from core.corruption_detector import CorruptionDetector
        
        class RepairThread(BaseThread):
            def __init__(self, input_file, output_file):
                super().__init__()
                self.input_file = input_file
                self.output_file = output_file
            
            def run(self):
                try:
                    self.emit_log("🔧 Intentando reparar video...")
                    self.emit_progress(10)
                    
                    process = CorruptionDetector.attempt_repair(self.input_file, self.output_file)
                    
                    if not process:
                        self.emit_finished(False, "Error al iniciar reparación")
                        return
                    
                    self.emit_progress(50)
                    
                    for line in process.stderr:
                        if not self.is_running:
                            process.kill()
                            self.emit_finished(False, "Reparación cancelada")
                            return
                    
                    process.wait()
                    
                    if process.returncode == 0:
                        self.emit_progress(100)
                        self.emit_finished(True, "✅ Video reparado exitosamente")
                    else:
                        self.emit_finished(False, "❌ Error durante la reparación")
                        
                except Exception as e:
                    self.emit_finished(False, f"❌ Error: {str(e)}")
        
        repair_thread = RepairThread(self.current_file, output_file)
        repair_thread.progress.connect(self.update_progress)
        repair_thread.log_message.connect(self.log)
        repair_thread.finished_signal.connect(self.repair_finished)
        
        repair_thread.start()
    
    def repair_finished(self, success, message):
        """Callback cuando termina la reparación"""
        self.btn_repair.setEnabled(True)
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