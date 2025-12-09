from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel


class AnalysisView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
        header = QLabel("Centro de Diagnóstico")
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)
        
        self.tabs = QTabWidget()
        
        # 1. Unified Analysis Tab
        from ui.tabs.unified_analysis_tab import UnifiedAnalysisTab
        self.unified_tab = UnifiedAnalysisTab(main_window)
        self.tabs.addTab(self.unified_tab, "🔍 Centro de Diagnóstico")
        
        layout.addWidget(self.tabs)
