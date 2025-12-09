from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel
from ui.tabs.simple_config_tab import SimpleConfigTab
from ui.tabs.advanced_config_tab import AdvancedConfigTab
from ui.tabs.device_profile_tab import DeviceProfileTab
from ui.tabs.multi_format_tab import MultiFormatTab
from ui.tabs.pausable_tab import PausableTab

class ConversionView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
        header = QLabel("Módulo de Conversión")
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Inner tabs for conversion modes
        self.tabs = QTabWidget()
        
        # 1. UNIFIED CONFIG (Replaces Simple & Advanced)
        from ui.tabs.unified_config_tab import UnifiedConfigTab
        self.unified_tab = UnifiedConfigTab(main_window)
        self.tabs.addTab(self.unified_tab, "⚙️ Configuración General")
        
        from ui.tabs.device_profile_tab import DeviceProfileTab
        self.profile_tab = DeviceProfileTab(main_window)
        self.tabs.addTab(self.profile_tab, "📱 Perfiles")
        
        from ui.tabs.multi_format_tab import MultiFormatTab
        self.multi_tab = MultiFormatTab(main_window)
        self.tabs.addTab(self.multi_tab, "🎯 Multi-Formato")
        
        from ui.tabs.pausable_tab import PausableTab
        self.pausable_tab = PausableTab(main_window)
        self.tabs.addTab(self.pausable_tab, "⏯️ Pausable")
        
        layout.addWidget(self.tabs)
