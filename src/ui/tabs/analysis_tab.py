"""Tab de análisis de videos"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QGroupBox, QTextEdit, QFileDialog, QLabel)
from threads.analysis_thread import AnalysisThread
from core.analyzer import VideoAnalyzer
from core.estimator import ConversionEstimator

class AnalysisTab(QWidget):
    """Tab para análisis de videos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.analysis_thread = None
        self.current_file = None
        self.current_analysis = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Selector de archivo
        file_group = QGroupBox("Archivo a Analizar")
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
        self.label_file.setProperty("class", "file_label")
        file_layout.addWidget(self.label_file)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Área de resultados
        results_group = QGroupBox("Resultados del Análisis")
        results_layout = QVBoxLayout()
        
        self.text_analysis = QTextEdit()
        self.text_analysis.setReadOnly(True)
        self.text_analysis.setPlaceholderText("Los resultados del análisis aparecerán aquí...")
        results_layout.addWidget(self.text_analysis)
        
        # Estimaciones
        self.label_estimations = QLabel("")
        self.label_estimations.setProperty("class", "note_label")
        self.label_estimations.setWordWrap(True)
        results_layout.addWidget(self.label_estimations)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
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
            if self.parent_window:
                self.parent_window.log(f"Archivo seleccionado para análisis: {file_path}")
    
    def analyze_video(self):
        """Inicia el análisis del video"""
        if not self.current_file:
            return
        
        if self.analysis_thread and self.analysis_thread.isRunning():
            return
        
        self.btn_analyze.setEnabled(False)
        self.text_analysis.clear()
        self.label_estimations.clear()
        
        # Crear thread de análisis
        self.analysis_thread = AnalysisThread(self.current_file)
        self.analysis_thread.progress.connect(self.update_progress)
        self.analysis_thread.log_message.connect(self.log)
        self.analysis_thread.analysis_complete.connect(self.show_analysis)
        self.analysis_thread.finished_signal.connect(self.analysis_finished)
        
        self.analysis_thread.start()
    
    def show_analysis(self, analysis):
        """Muestra los resultados del análisis"""
        self.current_analysis = analysis
        formatted = VideoAnalyzer.format_analysis(analysis)
        self.text_analysis.setText(formatted)
        
        # Mostrar estimaciones
        self.show_estimations(analysis)
    
    def show_estimations(self, analysis):
        """Muestra estimaciones de conversión"""
        if not analysis or not analysis['video_streams']:
            return
        
        duration = analysis['duration']
        video = analysis['video_streams'][0]
        resolution = (video['width'], video['height'])
        
        # Estimar para diferentes configuraciones
        text = "📊 ESTIMACIONES DE CONVERSIÓN:\n\n"
        
        configs = [
            ("CPU (libx264, medium, CRF 23)", 'libx264', 'medium', 23),
            ("GPU (h264_nvenc, p5, CRF 23)", 'h264_nvenc', 'p5', 23),
            ("Alta calidad (libx264, slow, CRF 18)", 'libx264', 'slow', 18),
        ]
        
        for name, encoder, preset, crf in configs:
            time_est = ConversionEstimator.estimate_time(duration, encoder, preset)
            size_est = ConversionEstimator.estimate_size(duration, crf=crf, resolution=resolution)
            
            text += f"{name}:\n"
            text += f"  ⏱️ Tiempo estimado: {ConversionEstimator.format_time(time_est)}\n"
            text += f"  💾 Tamaño estimado: {ConversionEstimator.format_size(size_est)}\n\n"
        
        self.label_estimations.setText(text)
    
    def analysis_finished(self, success, message):
        """Callback cuando termina el análisis"""
        self.btn_analyze.setEnabled(True)
        if self.parent_window:
            self.parent_window.log(message)
    
    def update_progress(self, value):
        """Actualiza progreso"""
        if self.parent_window:
            self.parent_window.update_progress(value)
    
    def log(self, message):
        """Log de mensaje"""
        if self.parent_window:
            self.parent_window.log(message)