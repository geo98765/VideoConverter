"""Vista de Análisis Unificado (Metadatos + Salud)"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QGroupBox, QTextEdit, QFileDialog, QLabel, QFrame,
                               QGridLayout, QMessageBox)
from PyQt6.QtCore import Qt
from threads.analysis_thread import AnalysisThread
from threads.corruption_thread import CorruptionThread
from core.analyzer import VideoAnalyzer
from core.corruption_detector import CorruptionDetector
import os

class UnifiedAnalysisTab(QWidget):
    """
    Combina Análisis de Video y Detección de Corrupción en una vista moderna.
    Reemplaza texto plano con tarjetas de información.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.current_file = None
        self.analysis_thread = None
        self.corruption_thread = None
        self.current_analysis = None
        self.scan_result = None
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # --- SECCIÓN 1: Selección ---
        top_bar = QHBoxLayout()
        
        self.btn_select = QPushButton("📁 Seleccionar Video")
        self.btn_select.setProperty("class", "primary_btn")
        self.btn_select.setMinimumHeight(45)
        self.btn_select.clicked.connect(self.select_file)
        top_bar.addWidget(self.btn_select)
        
        self.label_file = QLabel("Ningún archivo seleccionado")
        self.label_file.setStyleSheet("color: #A6ADC8; font-style: italic; margin-left: 10px;")
        top_bar.addWidget(self.label_file)
        top_bar.addStretch()
        
        main_layout.addLayout(top_bar)
        
        # --- SECCIÓN 2: Grid de Resultados ---
        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(15)
        
        # Tarjeta 1: Información Básica (Metadatos)
        self.card_meta = self.create_info_card("📋 Metadatos", "Analice un video para ver detalles.")
        self.cards_layout.addWidget(self.card_meta, 0, 0)
        
        # Tarjeta 2: Salud del Archivo (Corrupción)
        self.card_health = self.create_info_card("🏥 Salud del Archivo", "Escanee para detectar corrupción.")
        self.cards_layout.addWidget(self.card_health, 0, 1)
        
        main_layout.addLayout(self.cards_layout)
        
        # --- SECCIÓN 3: Acciones ---
        actions_layout = QHBoxLayout()
        actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        actions_layout.setSpacing(20)
        
        self.btn_analyze = QPushButton("🔍 Analizar Metadatos")
        self.btn_analyze.setMinimumHeight(40)
        self.btn_analyze.setFixedWidth(200)
        self.btn_analyze.clicked.connect(self.run_detailed_analysis)
        self.btn_analyze.setEnabled(False)
        actions_layout.addWidget(self.btn_analyze)
        
        self.btn_scan = QPushButton("🩺 Escanear Corrupción")
        self.btn_scan.setMinimumHeight(40)
        self.btn_scan.setFixedWidth(200)
        self.btn_scan.clicked.connect(self.run_corruption_scan)
        self.btn_scan.setEnabled(False)
        actions_layout.addWidget(self.btn_scan)
        
        self.btn_repair = QPushButton("🔧 Reparar Archivo")
        self.btn_repair.setMinimumHeight(40)
        self.btn_repair.setFixedWidth(200)
        self.btn_repair.setProperty("class", "danger_btn")
        self.btn_repair.clicked.connect(self.repair_video)
        self.btn_repair.setEnabled(False) # Solo enable si detecta error
        self.btn_repair.setVisible(False)
        actions_layout.addWidget(self.btn_repair)
        
        main_layout.addLayout(actions_layout)
        
        # --- SECCIÓN 4: Log / Detalles Texto (Opcional, expandible) ---
        self.detail_area = QTextEdit()
        self.detail_area.setMaximumHeight(100)
        self.detail_area.setPlaceholderText("Detalles técnicos adicionales aparecerán aquí...")
        self.detail_area.setReadOnly(True)
        self.detail_area.setVisible(False)
        main_layout.addWidget(self.detail_area)
        
        main_layout.addStretch()
        self.setLayout(main_layout)
        
    def create_info_card(self, title, placeholder):
        frame = QFrame()
        frame.setProperty("class", "dashboard_card")
        frame.setMinimumHeight(200)
        
        layout = QVBoxLayout(frame)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 5px;")
        layout.addWidget(lbl_title)
        
        content = QLabel(placeholder)
        content.setWordWrap(True)
        content.setAlignment(Qt.AlignmentFlag.AlignTop)
        content.setObjectName(f"content_{title.split()[1]}") # content_Metadatos, content_Salud
        layout.addWidget(content)
        layout.addStretch()
        
        return frame

    def update_card_content(self, card, new_text, is_error=False):
        # Find the content label inside the card layout (index 1)
        # Layout: Title (0), Content (1), Stretch (2)
        layout = card.layout()
        if layout.count() > 1:
            lbl = layout.itemAt(1).widget()
            if isinstance(lbl, QLabel):
                lbl.setText(new_text)
                if is_error:
                    lbl.setStyleSheet("color: #F38BA8; font-weight: bold;")
                else:
                    lbl.setStyleSheet("color: #CDD6F4;") # Normal text color

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar video", "", 
            "Videos (*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm *.m4v);;Todos (*.*)"
        )
        if file_path:
            self.current_file = file_path
            self.label_file.setText(os.path.basename(file_path))
            self.btn_analyze.setEnabled(True)
            self.btn_scan.setEnabled(True)
            self.btn_repair.setVisible(False)
            
            # Reset cards
            self.update_card_content(self.card_meta, "Listo para analizar metadatos.")
            self.update_card_content(self.card_health, "Listo para escanear integridad.")
            self.detail_area.setVisible(False)

    def run_detailed_analysis(self):
        if not self.current_file: return
        self.btn_analyze.setEnabled(False)
        self.update_card_content(self.card_meta, "⏳ Analizando metadatos...")
        
        self.analysis_thread = AnalysisThread(self.current_file)
        self.analysis_thread.analysis_complete.connect(self.on_analysis_complete)
        self.analysis_thread.finished_signal.connect(lambda s, m: self.btn_analyze.setEnabled(True))
        self.analysis_thread.start()

    def on_analysis_complete(self, data):
        self.current_analysis = data
        if not data:
            self.update_card_content(self.card_meta, "❌ Error al leer metadatos.", is_error=True)
            return

        # Construir resumen bonito con iconos
        duration = data.get('duration', 0)
        fmt_duration = f"{int(duration//60)}m {int(duration%60)}s"
        size_mb = data.get('size', 0) / (1024*1024)
        
        # Info Video
        v_stream = data['video_streams'][0] if data['video_streams'] else {}
        res = f"{v_stream.get('width','?')}x{v_stream.get('height','?')}"
        codec = v_stream.get('codec_name', 'Desconocido')
        fps = v_stream.get('r_frame_rate', '?')
        
        # Info Audio
        a_stream = data['audio_streams'][0] if data['audio_streams'] else {}
        a_codec = a_stream.get('codec_name', 'Sin Audio')
        
        summary = (
            f"⏱️ **Duración:** {fmt_duration}\n"
            f"💾 **Tamaño:** {size_mb:.2f} MB\n"
            f"🎬 **Resolución:** {res}\n"
            f"🎞️ **Codec Video:** {codec} ({fps} fps)\n"
            f"🔊 **Codec Audio:** {a_codec}"
        )
        self.update_card_content(self.card_meta, summary)
        
    def run_corruption_scan(self):
        if not self.current_file: return
        self.btn_scan.setEnabled(False)
        self.btn_repair.setVisible(False)
        self.update_card_content(self.card_health, "⏳ Escaneando integridad (puede tardar)...")
        
        self.corruption_thread = CorruptionThread(self.current_file)
        self.corruption_thread.analysis_complete.connect(self.on_scan_complete)
        self.corruption_thread.finished_signal.connect(lambda s, m: self.btn_scan.setEnabled(True))
        self.corruption_thread.start()

    def on_scan_complete(self, result):
        self.scan_result = result
        status = result.get('status', 'unknown')
        
        if status == 'healthy':
            msg = "✅ **Archivo Saludable**\nNo se detectaron errores de decodificación."
            self.update_card_content(self.card_health, msg)
        else:
            errors = len(result.get('errors', []))
            msg = (
                f"⚠️ **Problemas Detectados**\n"
                f"Estado: {status}\n"
                f"Errores encontrados: {errors}\n\n"
                "Se recomienda intentar reparar el archivo."
            )
            self.update_card_content(self.card_health, msg, is_error=True)
            self.btn_repair.setVisible(True)
            self.btn_repair.setEnabled(True)
            
            # Show details in text area
            report = CorruptionDetector.get_corruption_report(result)
            self.detail_area.setText(report)
            self.detail_area.setVisible(True)

    def repair_video(self):
        if not self.current_file: return
        
        reply = QMessageBox.question(self, "Reparar", "¿Intentar reparar timestamps y headers corruptos?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No: return
        
        # Reuse logic from CorruptionTab roughly
        base, ext = os.path.splitext(self.current_file)
        out_file = f"{base}_repaired{ext}"
        
        self.btn_repair.setEnabled(False)
        self.btn_repair.setText("Reparando...")
        
        # Simple blocking call for now or reuse thread logic? 
        # Ideally reimplement RepairThread loop here, but for brevity let's use the one from CorruptionTab logic via import
        # Or better, just inline a simple Thread since I can't easily import inner classes from other tabs without refactoring
        
        from threads.base_thread import BaseThread
        
        class RepairWorker(BaseThread):
            def __init__(self, i, o):
                super().__init__()
                self.i = i
                self.o = o
            def run(self):
                self.emit_log("Iniciando reparación...")
                # Call core logic
                proc = CorruptionDetector.attempt_repair(self.i, self.o)
                if proc:
                    proc.wait()
                    if proc.returncode == 0:
                        self.emit_finished(True, "Reparado exitosamente")
                    else:
                        self.emit_finished(False, "Falló la reparación ffmpeg")
                else:
                    self.emit_finished(False, "No pudo iniciar ffmpeg")

        self.worker = RepairWorker(self.current_file, out_file)
        self.worker.finished_signal.connect(self.on_repair_finished)
        self.worker.start()

    def on_repair_finished(self, success, msg):
        self.btn_repair.setText("🔧 Reparar Archivo")
        self.btn_repair.setEnabled(True)
        QMessageBox.information(self, "Resultado", msg)
