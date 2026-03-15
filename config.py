import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    SESSION_STRING = os.getenv("SESSION_STRING")
    ADMIN_IDS = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]
    
    # Audio Settings
    SAMPLE_RATE = 48000
    CHANNELS = 2
    CHUNK_SIZE = 960
    
    # Kernel Audio Processing Defaults
    DEFAULT_GAIN = 2.0  # 200%
    DEFAULT_BASS = 1.5  # 150%
    DEFAULT_MID = 1.0   # 100%
    DEFAULT_TREBLE = 0.5 # 50%
    DEFAULT_ECHO = 0.2
    DEFAULT_REVERB = 0.3
    DEFAULT_NOISE_REDUCTION = 0.1
    DEFAULT_LOUDNESS = 0.8  # 80%
    DEFAULT_DISTORTION = 0.7  # 70%
    DEFAULT_SATURATION = 0.8  # 80%
    DEFAULT_COMPRESSION = 0.9  # 90%
    DEFAULT_CLIP_THRESHOLD = 0.9
    DEFAULT_BIT_DEPTH = 16
    
    # Kernel Presets
    KERNEL_PRESETS = {
        'light': {'gain': 1.5, 'bass': 0.8, 'distortion': 0.3},
        'medium': {'gain': 2.0, 'bass': 1.5, 'distortion': 0.7},
        'heavy': {'gain': 3.0, 'bass': 2.0, 'distortion': 1.0},
        'kernel': {'gain': 4.0, 'bass': 3.0, 'distortion': 1.5, 'saturation': 2.0}
    }

config = Config()