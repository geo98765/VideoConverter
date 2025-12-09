from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, QSizePolicy
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QIcon, QFont

class SidebarButton(QPushButton):
    def __init__(self, text, icon_name=None, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFixedHeight(50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setIconSize(QSize(24, 24))
        self.setProperty("class", "sidebar_btn")

class Sidebar(QWidget):
    # Signals to change the page in the main window
    page_changed = pyqtSignal(int) # index of the page

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(250)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(8)
        self.setLayout(layout)

        # Title / Logo Area
        title_label = QLabel("VID CONVERTIDOR")
        title_label.setObjectName("sidebar_title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setObjectName("sidebar_line")
        layout.addWidget(line)

        layout.addSpacing(20)

        # Navigation Buttons
        self.buttons = []
        self.group_1 = self.create_nav_section(layout, "PRINCIPAL")
        self.add_nav_button(layout, "Dashboard", 0, self.group_1)
        self.add_nav_button(layout, "Conversión", 1, self.group_1)
        self.add_nav_button(layout, "Herramientas", 2, self.group_1)
        self.add_nav_button(layout, "Análisis", 3, self.group_1)

        layout.addSpacing(20)
        self.group_2 = self.create_nav_section(layout, "SISTEMA")
        self.add_nav_button(layout, "Configuración", 4, self.group_2)
        
        layout.addStretch()

        # Theme Toggle (Bottom)
        self.theme_btn = QPushButton("🌙 Cambiar Tema")
        self.theme_btn.setObjectName("theme_btn")
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.setProperty("class", "sidebar_action_btn")
        layout.addWidget(self.theme_btn)

        # Select first button by default
        if self.buttons:
            self.buttons[0].setChecked(True)

    def create_nav_section(self, layout, title):
        label = QLabel(title)
        label.setProperty("class", "sidebar_section_label")
        layout.addWidget(label)
        return []

    def add_nav_button(self, layout, text, index, group_list):
        btn = SidebarButton(text)
        btn.clicked.connect(lambda: self.on_button_clicked(index))
        layout.addWidget(btn)
        self.buttons.append(btn)
        # group_list.append(btn) # Can be used for grouping logic later

    def on_button_clicked(self, index):
        # Uncheck all others
        for btn in self.buttons:
            btn.setChecked(False)
        
        # Check sender
        sender = self.sender()
        sender.setChecked(True)
        
        self.page_changed.emit(index)
