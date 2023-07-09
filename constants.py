from pathlib import Path

# Constants
SAMPLING_RATE = 16000
CHANNELS = 1
DURATION = 20  # in seconds
PHRASE_TIME_LIMIT = None  # in seconds
PAUSE_THRESHOLD = 1  # in seconds
ENERGY_THRESHOLD = 1000

WHISPER_MODEL = Path("./whisper.cpp/models/ggml-base.en.bin")
AUDIO_FORMAT = "wav"
