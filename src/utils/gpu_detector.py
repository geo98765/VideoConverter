import subprocess

def detect_nvenc():
    """Detecta si NVENC está disponible en FFmpeg"""
    try:
        result = subprocess.run(
            ['ffmpeg', '-encoders'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        has_nvenc = 'h264_nvenc' in result.stdout
        return has_nvenc
    except Exception as e:
        print(f"Error detectando NVENC: {e}")
        return False

def get_gpu_info():
    """Obtiene información de las GPUs NVIDIA instaladas"""
    try:
        import pynvml
        pynvml.nvmlInit()
        
        device_count = pynvml.nvmlDeviceGetCount()
        gpus = []
        
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle)
            gpus.append(name)
        
        pynvml.nvmlShutdown()
        return gpus
    except Exception as e:
        print(f"Error obteniendo info de GPU: {e}")
        return []

def get_available_encoders():
    """Retorna lista de codificadores disponibles"""
    encoders = ["libx264"]  # CPU siempre disponible
    
    if detect_nvenc():
        encoders.extend(["h264_nvenc", "hevc_nvenc"])
    
    return encoders

if __name__ == "__main__":
    print(f"NVENC disponible: {detect_nvenc()}")
    print(f"GPUs detectadas: {get_gpu_info()}")
    print(f"Codificadores disponibles: {get_available_encoders()}")