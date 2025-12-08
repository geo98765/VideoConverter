"""Tab de cola de videos"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QGroupBox, QTableWidget, QHeaderView, QLabel)

class QueueTab(QWidget):
    """Tab de cola de procesamiento"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Tabla de cola
        queue_group = QGroupBox("Cola de Procesamiento")
        queue_layout = QVBoxLayout()
        
        self.table_queue = QTableWidget()
        self.table_queue.setColumnCount(4)
        self.table_queue.setHorizontalHeaderLabels(["Archivo", "Tamaño", "Estado", "Ruta Completa"])
        self.table_queue.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_queue.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_queue.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_queue.setColumnHidden(3, True)
        queue_layout.addWidget(self.table_queue)
        
        # Botones
        queue_buttons = QHBoxLayout()
        
        btn_clear_queue = QPushButton("🗑️ Limpiar Cola")
        btn_clear_queue.clicked.connect(self.clear_queue)
        queue_buttons.addWidget(btn_clear_queue)
        
        btn_remove_selected = QPushButton("➖ Quitar Seleccionado")
        btn_remove_selected.clicked.connect(self.remove_selected)
        queue_buttons.addWidget(btn_remove_selected)
        
        self.label_queue_count = QLabel("Videos en cola: 0")
        self.label_queue_count.setStyleSheet("font-weight: bold;")
        queue_buttons.addWidget(self.label_queue_count)
        
        queue_buttons.addStretch()
        queue_layout.addLayout(queue_buttons)
        
        queue_group.setLayout(queue_layout)
        layout.addWidget(queue_group)
        
        self.setLayout(layout)
    
    def clear_queue(self):
        """Limpia la cola"""
        if self.parent_window:
            self.parent_window.clear_queue()
    
    def remove_selected(self):
        """Quita el seleccionado"""
        if self.parent_window:
            self.parent_window.remove_selected_from_queue()
    
    def update_count(self, count):
        """Actualiza el contador"""
        self.label_queue_count.setText(f"Videos en cola: {count}")