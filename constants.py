from pathlib import Path

# Constants
SAMPLING_RATE = 16000
CHANNELS = 1
DURATION = 10  # in seconds
PHRASE_TIME_LIMIT = 3 # in seconds

WHISPER_MODEL = Path("./whisper.cpp/models/ggml-base.en.bin")
AUDIO_FORMAT = "wav"
