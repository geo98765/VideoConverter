
import sys
import os
sys.path.append(os.path.abspath("src"))

from PyQt6.QtWidgets import QApplication

def verify_tabs():
    app = QApplication(sys.argv)
    
    print("Checking CompressTab...")
    try:
        from ui.tabs.compress_tab import CompressTab
        tab = CompressTab()
        if not hasattr(tab, 'progress_bar'):
            print("FAILURE: CompressTab missing progress_bar")
        else:
            print("SUCCESS: CompressTab instantiated")
    except Exception as e:
        print(f"FAILURE CompressTab: {e}")

    print("\nChecking AudioExtractTab...")
    try:
        from ui.tabs.audio_extract_tab import AudioExtractTab
        tab = AudioExtractTab()
        if not hasattr(tab, 'progress_bar'):
            print("FAILURE: AudioExtractTab missing progress_bar")
        else:
            print("SUCCESS: AudioExtractTab instantiated")
    except Exception as e:
        print(f"FAILURE AudioExtractTab: {e}")

    print("\nChecking ResolutionTab...")
    try:
        from ui.tabs.resolution_tab import ResolutionTab
        tab = ResolutionTab()
        if not hasattr(tab, 'progress_bar'):
            print("FAILURE: ResolutionTab missing progress_bar")
        else:
            print("SUCCESS: ResolutionTab instantiated")
    except Exception as e:
        print(f"FAILURE ResolutionTab: {e}")

    print("\nChecking CorruptionTab...")
    try:
        from ui.tabs.corruption_tab import CorruptionTab
        tab = CorruptionTab()
        if not hasattr(tab, 'progress_bar'):
            print("FAILURE: CorruptionTab missing progress_bar")
        else:
            print("SUCCESS: CorruptionTab instantiated")
    except Exception as e:
        print(f"FAILURE CorruptionTab: {e}")

    print("\nChecking JoinTab...")
    try:
        from ui.tabs.join_tab import JoinTab
        tab = JoinTab()
        if not hasattr(tab, 'progress_bar'):
            print("FAILURE: JoinTab missing progress_bar")
        else:
            print("SUCCESS: JoinTab instantiated")
    except Exception as e:
        print(f"FAILURE JoinTab: {e}")

if __name__ == "__main__":
    verify_tabs()
