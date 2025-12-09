import sys
import os
sys.path.append(os.path.abspath("src"))

from PyQt6.QtWidgets import QApplication
from ui.components.queue_panel import QueuePanel

def test_queue_add_row():
    app = QApplication(sys.argv)
    panel = QueuePanel()
    
    print("Testing add_row...")
    try:
        panel.add_row("test_video.mp4", "100 MB", "Pendiente", "/path/to/test_video.mp4")
        print("SUCCESS: add_row executed without error.")
    except AttributeError as e:
        print(f"FAILURE: {e}")
    except Exception as e:
        print(f"FAILURE: Unexpected error: {e}")

if __name__ == "__main__":
    test_queue_add_row()
