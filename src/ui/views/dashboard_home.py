from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout
from PyQt6.QtCore import Qt
from ui.components.card_widget import CardWidget

class DashboardHome(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window # Reference to main window to switch pages
        
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        self.setLayout(layout)
        
        # Welcome Header
        welcome = QLabel("Vid Convertidor")
        welcome.setObjectName("view_title")
        layout.addWidget(welcome)
        
        subtitle = QLabel("Selecciona una herramienta para comenzar")
        subtitle.setObjectName("view_subtitle")
        layout.addWidget(subtitle)
        
        # Quick Actions Grid
        grid = QGridLayout()
        grid.setSpacing(20)
        
        # Shortcuts
        self.card_convert = CardWidget("Conversión Rápida", "Convierte videos a MP4, AVI, MKV...", "🔄")
        self.card_convert.clicked.connect(lambda: self.main_window.switch_to_page(1)) # Index 1 = Conversion
        grid.addWidget(self.card_convert, 0, 0)
        
        self.card_compress = CardWidget("Comprimir Video", "Reduce el tamaño sin perder mucha calidad", "🗜️")
        self.card_compress.clicked.connect(lambda: self.main_window.switch_to_tool("compress"))
        grid.addWidget(self.card_compress, 0, 1)

        self.card_analysis = CardWidget("Analizar Video", "Ver codecs, bitrate y detectar corrupción", "🔍")
        self.card_analysis.clicked.connect(lambda: self.main_window.switch_to_page(3)) # Index 3 = Analysis
        grid.addWidget(self.card_analysis, 1, 0)
        
        self.card_queue = CardWidget("Ver Cola", "Gestiona los procesos pendientes", "📋")
        self.card_queue.clicked.connect(lambda: self.main_window.toggle_queue_panel())
        grid.addWidget(self.card_queue, 1, 1)

        layout.addLayout(grid)
        layout.addStretch()
