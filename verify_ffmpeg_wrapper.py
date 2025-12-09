import sys
import os
sys.path.append(os.path.abspath("src"))

from utils.ffmpeg_wrapper import FFmpegWrapper
import subprocess

def test_command_generation():
    # Mock subprocess.Popne or modify wrapper? 
    # Wrapper prints the command. We can capture stdout or just inspect the code behavior by mocking subprocess.Popen
    
    orig_popen = subprocess.Popen
    last_cmd = []
    
    def mock_popen(cmd, **kwargs):
        nonlocal last_cmd
        last_cmd = cmd
        return None # Return None as we don't need a real process
        
    subprocess.Popen = mock_popen
    
    print("--- Test 1: MP4 (x264) ---")
    FFmpegWrapper.convert_video("input.mp4", "output.mp4", encoder="libx264", preset="medium", crf=23)
    print(f"CMD: {last_cmd}")
    if "-preset" in last_cmd and "medium" in last_cmd:
        print("SUCCESS: MP4 uses preset")
    else:
        print("FAILURE: MP4 missing preset")

    print("\n--- Test 2: WebM (libvpx-vp9) ---")
    FFmpegWrapper.convert_video("input.mkv", "output.webm", encoder="libvpx-vp9", preset="medium", crf=30)
    print(f"CMD: {last_cmd}")
    if "-deadline" in last_cmd and "good" in last_cmd:
        print("SUCCESS: WebM use deadline good (mapped from medium)")
    elif "-preset" in last_cmd:
        print("FAILURE: WebM should not use preset")
    else:
        print("FAILURE: WebM missing deadline")
        
    print("\n--- Test 3: WebM (libvpx-vp9) Fast ---")
    FFmpegWrapper.convert_video("input.mkv", "output.webm", encoder="libvpx-vp9", preset="ultrafast", crf=30)
    print(f"CMD: {last_cmd}")
    if "-deadline" in last_cmd and "realtime" in last_cmd:
        print("SUCCESS: WebM use deadline realtime (mapped from ultrafast)")
    else:
        print(f"FAILURE: WebM mapped incorrectly: {last_cmd}")

    subprocess.Popen = orig_popen

if __name__ == "__main__":
    test_command_generation()
