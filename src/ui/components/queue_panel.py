"""Panel global de cola de procesamiento"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QFrame, QTableWidget, QHeaderView, QLabel, QAbstractItemView,
                               QProgressBar, QTableWidgetItem)
from PyQt6.QtCore import Qt, pyqtSignal
import os

class QueuePanel(QWidget):
    """
    Panel deslizable/colapsable que muestra la cola de videos.
    Diseñado para ser integrado globalmente en la ventana principal.
    """
    
    # Señales para comunicar acciones a la ventana principal
    request_clear = pyqtSignal()
    request_remove = pyqtSignal(int) # Envía el índice a eliminar
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = None
        # Try to find the main window parent if possible, though signals are preferred
        curr = parent
        while curr:
            if hasattr(curr, 'remove_from_queue_index'):
                self.parent_window = curr
                break
            curr = curr.parent()
            
        self.init_ui()
        
    def init_ui(self):
        # Marco principal con estilo
        self.frame = QFrame()
        self.frame.setProperty("class", "queue_panel")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setStyleSheet("""
            QFrame.queue_panel {
                background-color: #181825; 
                border-top: 1px solid #313244;
                border-radius: 0px;
            }
        """)
        
        layout = QVBoxLayout(self.frame)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header con título y botón de cerrar (opcional, ya que tenemos toggle abajo)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.btn_toggle = QPushButton("▼")
        self.btn_toggle.setFixedSize(24, 24)
        self.btn_toggle.setCheckable(True)
        self.btn_toggle.setChecked(True) # Expandido por defecto
        self.btn_toggle.setStyleSheet("""
            QPushButton { border: none; font-weight: bold; color: #CDD6F4; }
        """)
        self.btn_toggle.toggled.connect(self.toggle_content)
        header_layout.addWidget(self.btn_toggle)
        
        title = QLabel("📋 Cola de Procesamiento")
        title.setStyleSheet("font-weight: bold; color: #CDD6F4;")
        header_layout.addWidget(title)
        
        self.lbl_count = QLabel("0 videos")
        self.lbl_count.setStyleSheet("color: #A6ADC8; margin-left: 10px;")
        header_layout.addWidget(self.lbl_count)
        
        header_layout.addStretch()
        
        # Botones de acción rápida
        self.actions_widget = QWidget()
        actions_layout = QHBoxLayout(self.actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        
        btn_remove = QPushButton("➖ Quitar")
        btn_remove.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_remove.setProperty("class", "secondary_btn")
        btn_remove.setFixedSize(80, 24)
        btn_remove.clicked.connect(self.on_remove_clicked)
        actions_layout.addWidget(btn_remove)
        
        btn_clear = QPushButton("🗑️ Limpiar")
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.setProperty("class", "secondary_btn")
        btn_clear.setFixedSize(80, 24)
        btn_clear.clicked.connect(self.request_clear.emit)
        actions_layout.addWidget(btn_clear)
        
        header_layout.addWidget(self.actions_widget)
        
        layout.addLayout(header_layout)
        
        # Contenido colapsable (Tabla)
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tabla
        self.table_queue = QTableWidget()
        self.table_queue.setColumnCount(5)
        self.table_queue.setHorizontalHeaderLabels(["Archivo", "Estado", "Progreso", "Info", "Acciones"])
        self.table_queue.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_queue.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_queue.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table_queue.setColumnWidth(2, 100)
        self.table_queue.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_queue.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table_queue.setColumnWidth(4, 50)
        
        self.table_queue.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_queue.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_queue.setAlternatingRowColors(True)
        # Estilo para tabla
        self.table_queue.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #313244;
                border-radius: 8px;
                gridline-color: #45475a;
                selection-background-color: #585b70;
                selection-color: #ffffff;
                alternate-background-color: #181825; /* Fix for white rows */
            }
            QHeaderView::section {
                background-color: #11111b; /* Darker header */
                color: #a6adc8;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #313244;
                font-weight: bold;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #313244; /* Separator lines */
            }
            QTableWidget::item:selected {
                background-color: #585b70;
            }
            QScrollBar:vertical {
                border: none;
                background: #1e1e2e;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #45475a;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        content_layout.addWidget(self.table_queue)
        layout.addWidget(self.content_widget)
        
        # Main layout del widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.frame)
        
        # Altura por defecto
        self.setMinimumHeight(250)
        self.setMaximumHeight(400)
        
    def toggle_content(self, checked):
        """Alterna la visibilidad del contenido del panel"""
        self.content_widget.setVisible(checked)
        arrow = "▼" if checked else "▶"
        self.btn_toggle.setText(arrow)
        
    def on_remove_clicked(self):
        row = self.table_queue.currentRow()
        if row >= 0:
            self.request_remove.emit(row)
        elif self.parent_window:
             # Fallback if no specific row selected but method exists
             pass

    def update_count(self, count):
        self.lbl_count.setText(f"{count} videos")
        
    def update_queue(self, queue_data):
        """Actualiza la tabla con los datos de la cola"""
        self.table_queue.setRowCount(len(queue_data))
        
        for row, item in enumerate(queue_data):
            # Archivo
            file_item = QTableWidgetItem(os.path.basename(item['file_path']))
            file_item.setToolTip(item['file_path'])
            self.table_queue.setItem(row, 0, file_item)
            
            # Estado
            status_item = QTableWidgetItem(item['status'])
            if item['status'] == "Completado":
                status_item.setForeground(Qt.GlobalColor.green)
            elif item['status'] == "Error":
                status_item.setForeground(Qt.GlobalColor.red)
            elif item['status'] == "Procesando...":
                status_item.setForeground(Qt.GlobalColor.blue)
            self.table_queue.setItem(row, 1, status_item)
            
            # Progreso
            progress = QProgressBar()
            progress.setValue(item.get('progress', 0))
            progress.setTextVisible(True)
            progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_queue.setCellWidget(row, 2, progress)
            
            # Info
            info_text = item.get('info', "")
            self.table_queue.setItem(row, 3, QTableWidgetItem(info_text))
            
            # Acciones (Boton Eliminar en celda)
            btn_remove = QPushButton("❌")
            btn_remove.setFixedSize(30, 24)
            btn_remove.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_remove.setToolTip("Quitar de la lista")
            # Usamos una lambda con valor por defecto para capturar el row actual
            # NOTA: Esto es tricky en bucles, pero necesario.
            # Mejor usar un objeto que guarde el índice si es posible, o conectar al row seleccionada.
            # Para simplificar, confiaremos en la selección de fila + botón 'Quitar' global,
            # pero el botón en línea es más intuitivo.
            btn_remove.clicked.connect(lambda _, r=row: self.request_remove_index(r))
            
            # Contenedor para centrar
            widget_cell = QWidget()
            layout_cell = QHBoxLayout(widget_cell)
            layout_cell.setContentsMargins(0, 0, 0, 0)
            layout_cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout_cell.addWidget(btn_remove)
            self.table_queue.setCellWidget(row, 4, widget_cell)
            
    def request_remove_index(self, index):
        """Emite la señal de eliminar con el índice específico"""
        self.request_remove.emit(index)

    def clear_table(self):
        self.table_queue.setRowCount(0)
        
    def add_row(self, filename, size, status, path):
        row = self.table_queue.rowCount()
        self.table_queue.insertRow(row)
        
        self.table_queue.setItem(row, 0, QTableWidgetItem(filename))
        self.table_queue.setItem(row, 1, QTableWidgetItem(status))
        # Add basic progress bar
        progress = QProgressBar()
        progress.setValue(0)
        progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table_queue.setCellWidget(row, 2, progress)
        
        self.table_queue.setItem(row, 3, QTableWidgetItem(size)) # Swapping info for size as per call or adjust
        # Wait, the call is: add_row(video.name, video.get_size_formatted(), "Pendiente", video.path)
        # My header is ["Archivo", "Estado", "Progreso", "Info", "Acciones"]
        # So:
        # Col 0: Archivo (filename)
        # Col 1: Estado (status) ("Pendiente")
        # Col 2: Progreso (ProgressBar)
        # Col 3: Info (size?)
        
        self.table_queue.setItem(row, 3, QTableWidgetItem(size)) 
        
        # Action button
        btn_remove = QPushButton("❌")
        btn_remove.setFixedSize(30, 24)
        btn_remove.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_remove.setToolTip("Quitar de la lista")
        btn_remove.clicked.connect(lambda _, r=row: self.request_remove_index(r))
        
        widget_cell = QWidget()
        layout_cell = QHBoxLayout(widget_cell)
        layout_cell.setContentsMargins(0, 0, 0, 0)
        layout_cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_cell.addWidget(btn_remove)
        self.table_queue.setCellWidget(row, 4, widget_cell)
        
    def remove_row(self, row):
        self.table_queue.removeRow(row)

    def update_status(self, row, status, color=None):
        if row < self.table_queue.rowCount():
            item = self.table_queue.item(row, 1)
            if item:
                item.setText(status)
                if color:
                    item.setForeground(color)

    def update_progress(self, row, value):
        """Actualiza la barra de progreso de una fila específica"""
        if row < self.table_queue.rowCount():
            # La barra de progreso está en la columna 2 (índice 2)
            # setCellWidget no devuelve el widget, hay que usar cellWidget
            progress_bar = self.table_queue.cellWidget(row, 2)
            if isinstance(progress_bar, QProgressBar):
                progress_bar.setValue(value)
                
                # Opcional: Cambiar color si está completo
                if value >= 100:
                    progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #a6e3a1; }")
                else:
                    # Reset o estilo default
                     progress_bar.setStyleSheet("""
                        QProgressBar {
                            border: 2px solid #45475a;
                            border-radius: 5px;
                            text-align: center;
                            background-color: #1e1e2e;
                            color: white;
                        }
                        QProgressBar::chunk {
                            background-color: #89b4fa;
                            border-radius: 3px;
                        }
                     """)
