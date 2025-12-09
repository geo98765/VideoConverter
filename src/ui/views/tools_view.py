from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QStackedWidget, QPushButton, QHBoxLayout, QGridLayout
from PyQt6.QtCore import Qt
from ui.components.card_widget import CardWidget
# Import tool tabs
from ui.tabs.compress_tab import CompressTab
from ui.tabs.join_tab import JoinTab
from ui.tabs.subtitle_tab import SubtitleTab
from ui.tabs.audio_extract_tab import AudioExtractTab
from ui.tabs.resolution_tab import ResolutionTab

class ToolsView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
        # Navigation bar (Breadcrumb like)
        nav_layout = QHBoxLayout()
        self.title_label = QLabel("Herramientas")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        nav_layout.addWidget(self.title_label)
        
        self.back_btn = QPushButton("⬅ Volver")
        self.back_btn.setFixedWidth(100)
        self.back_btn.clicked.connect(self.show_home)
        self.back_btn.hide()
        nav_layout.addWidget(self.back_btn, 0, Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(nav_layout)
        
        # Stacked widget: Index 0 = Menu (Grid), Index 1..N = Specific Tools
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        # --- 1. Menu Grid ---
        self.menu_widget = QWidget()
        menu_layout = QGridLayout()
        self.menu_widget.setLayout(menu_layout)
        
        # Define tools
        self.tools = [
            ("Comprimir", "Reducir tamaño de archivo", "🗜️", CompressTab(main_window)),
            ("Unir Videos", "Concatenar múltiples videos", "🔗", JoinTab(main_window)),
            ("Subtítulos", "Agregar o extraer subtítulos", "📝", SubtitleTab(main_window)),
            ("Extraer Audio", "Guardar audio como MP3/AAC", "🎵", AudioExtractTab(main_window)),
            ("Resolución", "Cambiar tamaño y aspecto", "📐", ResolutionTab(main_window))
        ]
        
        # Create cards
        row = 0
        col = 0
        for i, (name, desc, icon, widget) in enumerate(self.tools):
            card = CardWidget(name, desc, icon)
            # Capture loop variable i with default arg
            card.clicked.connect(lambda idx=i: self.open_tool(idx))
            menu_layout.addWidget(card, row, col)
            col += 1
            if col > 2: # 3 columns
                col = 0
                row += 1
        
        menu_layout.setRowStretch(row + 1, 1) # Push to top
        self.stack.addWidget(self.menu_widget)
        
        # --- 2. Add Tool Widgets ---
        for _, _, _, widget in self.tools:
            self.stack.addWidget(widget)

    def open_tool(self, index):
        # Index 0 is menu, so tool index is index + 1
        tool_name = self.tools[index][0]
        self.title_label.setText(f"Herramientas > {tool_name}")
        self.stack.setCurrentIndex(index + 1)
        self.back_btn.show()

    def show_home(self):
        self.title_label.setText("Herramientas")
        self.stack.setCurrentIndex(0)
        self.back_btn.hide()
        
    def open_by_name(self, name_key):
        # Helper for external navigation
        mapping = {
            "compress": 0,
            "join": 1,
            "subtitle": 2,
            "audio": 3,
            "resolution": 4
        }
        if name_key in mapping:
            self.open_tool(mapping[name_key])
