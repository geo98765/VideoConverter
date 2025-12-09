import sys
import os
sys.path.append(os.path.abspath("src"))

from PyQt6.QtWidgets import QApplication
from ui.tabs.unified_config_tab import UnifiedConfigTab

def test_logic():
    print("Starting verification test...")
    app = QApplication(sys.argv)
    # Mock parent
    class MockParent:
        def register_queue_panel(self, panel): pass
        def log(self, msg): print(f"LOG: {msg}")
        
    tab = UnifiedConfigTab(None)
    tab.parent_window = MockParent()
    
    # Check default state
    print(f"Default Recommended Checked: {tab.check_recommended.isChecked()}")
    if not tab.check_recommended.isChecked():
        print("FAILURE: Default should be checked")
        return

    # Test 1: MP4 Default (GPU)
    print("\n--- Test 1: MP4 Default (GPU) ---")
    tab.combo_format.setCurrentText("mp4")
    tab.check_gpu.setChecked(True)
    # Trigger logic manually if needed, but signals should work if event loop was running. 
    # Since we are not running app.exec(), signals might be synchronous or we might need to call slots manually if they are direct connections.
    # In PyQt direct connections (default for same thread) are immediate.
    
    print(f"Format: {tab.combo_format.currentText()}")
    print(f"Encoder Index: {tab.combo_encoder.currentIndex()} (Should be GPU related)")
    print(f"CRF: {tab.spin_crf.value()} (Should be 23)")
    
    # Test 2: WebM (VP9)
    print("\n--- Test 2: WebM (VP9) ---")
    tab.combo_format.setCurrentText("webm")
    # Verify values
    current_crf = tab.spin_crf.value()
    print(f"Format: {tab.combo_format.currentText()}")
    print(f"CRF: {current_crf} (Should be 30)")
    
    if current_crf != 30:
        print(f"FAILURE: Expected CRF 30 for WebM, got {current_crf}")
    else:
        print("SUCCESS: WebM CRF updated correctly")

    # Test 3: Manual Override
    print("\n--- Test 3: Manual Override ---")
    tab.check_recommended.setChecked(False)
    print(f"Recommended Checked: {tab.check_recommended.isChecked()}")
    print(f"Quality Enabled: {tab.combo_quality.isEnabled()} (Should be True)")
    
    tab.spin_crf.setValue(45)
    print(f"Manually set CRF to 45")
    
    # Change format shouldn't touch settings if recommended is OFF? 
    # Actually wait, my implementation says:
    # if self.check_recommended.isChecked(): self.apply_recommended_settings(format_name)
    # So if it is NOT checked, apply_recommended_settings is NOT called.
    
    tab.combo_format.setCurrentText("mkv")
    print(f"Changed format to MKV (Recommended OFF)")
    print(f"CRF: {tab.spin_crf.value()} (Should still be 45)")
    
    if tab.spin_crf.value() == 45:
        print("SUCCESS: Manual settings preserved when changing format with Recommended OFF")
    else:
        print(f"FAILURE: CRF changed to {tab.spin_crf.value()} but should be 45")

    # Test 4: Re-enable Recommended
    print("\n--- Test 4: Re-enable Recommended ---")
    tab.check_recommended.setChecked(True)
    print(f"Re-enabled Recommended (Format is MKV)")
    # Should re-apply MKV defaults (CRF 23)
    print(f"CRF: {tab.spin_crf.value()} (Should be 23)")
    
    if tab.spin_crf.value() == 23:
        print("SUCCESS: Recommended settings applied on re-enable")
    else:
        print(f"FAILURE: CRF is {tab.spin_crf.value()} but should be 23")

if __name__ == "__main__":
    test_logic()
