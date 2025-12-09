"""Vista de Configuración Global"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QGroupBox, QLabel, QFrame, QCheckBox, QMessageBox, QComboBox)
from PyQt6.QtCore import Qt
from utils.gpu_detector import get_gpu_info, detect_nvenc

class SettingsView(QWidget):
    """
    Vista para configuraciones generales del sistema y detección de hardware.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()
        self.refresh_hardware_info()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        header = QLabel("Configuración del Sistema")
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # --- TARJETA DE HARDWARE ---
        hw_card = self.create_card("🖥️ Hardware de Video")
        hw_layout = QVBoxLayout(hw_card)
        hw_layout.setContentsMargins(20, 20, 20, 20)
        
        self.lbl_cpu = QLabel("CPU: Detectando...")
        self.lbl_cpu.setStyleSheet("font-size: 14px;")
        hw_layout.addWidget(self.lbl_cpu)
        
        self.lbl_gpu = QLabel("GPU: Detectando...")
        self.lbl_gpu.setStyleSheet("font-size: 14px; font-weight: bold; color: #89B4FA;")
        hw_layout.addWidget(self.lbl_gpu)
        
        self.lbl_nvenc = QLabel("Estado NVENC: ...")
        hw_layout.addWidget(self.lbl_nvenc)
        
        btn_refresh = QPushButton("🔄 Redetectar Hardware")
        btn_refresh.setFixedWidth(200)
        btn_refresh.setProperty("class", "secondary_btn")
        btn_refresh.clicked.connect(self.refresh_hardware_info)
        hw_layout.addWidget(btn_refresh)
        
        layout.addWidget(hw_card)
        
        # --- PREFERENCIAS DE USUARIO ---
        prefs_card = self.create_card("⚙️ Preferencias Generales")
        prefs_layout = QVBoxLayout(prefs_card)
        prefs_layout.setContentsMargins(20, 20, 20, 20)
        
        # Idioma (Placeholder)
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Idioma:"))
        combo_lang = QComboBox()
        combo_lang.addItems(["Español", "English (Próximamente)"])
        lang_layout.addWidget(combo_lang)
        lang_layout.addStretch()
        prefs_layout.addLayout(lang_layout)
        
        # Checkbox ejemplo
        self.check_updates = QCheckBox("Buscar actualizaciones al inicio")
        self.check_updates.setChecked(True)
        prefs_layout.addWidget(self.check_updates)
        
        self.check_clean = QCheckBox("Limpiar cola al terminar exitosamente")
        self.check_clean.setChecked(False)
        prefs_layout.addWidget(self.check_clean)
        
        layout.addWidget(prefs_card)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def create_card(self, title):
        card = QFrame()
        card.setProperty("class", "dashboard_card")
        # Add basic layout to insert title? Or just return frame. 
        # Actually better to build inside init_ui for flexibility, but let's stick to simple card frame.
        # But wait, we need a title.
        return card

    # Override create_card logic slightly to match structure
    def create_card(self, title):
        card = QFrame()
        card.setProperty("class", "dashboard_card")
        
        # We return the card, layout is set externally? No, let's set it here?
        # But we need access to layout to add widgets.
        # Let's just return the card widget and let init_ui add a layout to it.
        # BUT, to keep title consistent, let's add title here if we used a wrapper class.
        # Since we are using plain QFrame, we'll manually add title in init_ui or...
        # Let's do this: 
        # Actually QFrame usage in previous tabs was: layout(card).
        # We'll stick to that manual approach in init_ui for full control.
        return card

    def refresh_hardware_info(self):
        from platform import processor
        cpu_name = processor() or "CPU Genérica"
        self.lbl_cpu.setText(f"🧠CPU: {cpu_name}")
        
        gpus = get_gpu_info()
        has_nvenc = detect_nvenc()
        
        if gpus:
            self.lbl_gpu.setText(f"🚀GPU Detectada: {gpus[0]}")
        else:
            self.lbl_gpu.setText("⚠️ GPU: No se detectó GPU dedicada compatible")
            
        if has_nvenc:
            self.lbl_nvenc.setText("✅NVENC Disponible: Aceleración por hardware activa.")
            self.lbl_nvenc.setStyleSheet("color: #A6E3A1") # Green
        else:
            self.lbl_nvenc.setText("❌NVENC No Disponible: Solo codificación por software (CPU).")
            self.lbl_nvenc.setStyleSheet("color: #F38BA8") # Red
