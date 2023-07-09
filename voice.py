import datetime
import hashlib
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import subprocess
from pathlib import Path
from pydub import AudioSegment
from speech_recognition import Recognizer, Microphone, AudioData

# Constants
SAMPLING_RATE = 16000
CHANNELS = 1
DURATION = 10  # in seconds
PHRASE_TIME_LIMIT = 3 # in seconds

WHISPER_MODEL = Path("./whisper.cpp/models/ggml-base.en.bin")
OUTPUT_DIRECTORY = Path("./transcriptions")
AUDIO_FORMAT = "wav"

transcription_queue = Queue()
stop_event = threading.Event()
file_lock = threading.Lock()

OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

class Whisper:
    def __init__(self, model_path):
        self.model_path = Path(model_path)

    def transcribe(self, audio_file):
        audio_file_path = Path(audio_file)
        txt_file_path = audio_file_path.with_suffix(".txt")
        try:
            # Run whisper command and capture output
            subprocess.run(
                ['./whisper.cpp/main', '-m', str(self.model_path), '-f', str(audio_file_path), '--output-txt'],
                check=True,  # Raises an exception if the command returns a non-zero exit status
                text=True,  # Return stdout and stderr as strings instead of bytes
                capture_output=True  # Capture stdout and stderr
            )
        except subprocess.CalledProcessError as e:
            print(f"Whisper command failed: {e}")
            return None

        # Read in the generate file txt
        with txt_file_path.open("r") as f:
            transcription = f.read()
        
        # Remove the generated file
        txt_file_path.unlink(missing_ok=True)

        return transcription.strip()

def record():
    print("Starting recording...")

    # Instantiate recognizer
    recognizer = Recognizer()
    recognizer.energy_threshold = 1000
    recognizer.dynamic_energy_threshold = False

    # Create a callback to handle audio data
    def record_callback(recognizer: Recognizer, audio: AudioData) -> None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = hashlib.sha1(timestamp.encode()).hexdigest() + "." + AUDIO_FORMAT

        # get raw audio data and save to file
        raw_data = audio.get_raw_data(convert_rate=SAMPLING_RATE, convert_width=2)
        audio_segment = AudioSegment(
            data=raw_data,
            sample_width=2,
            frame_rate=SAMPLING_RATE,
            channels=CHANNELS
        )

        audio_segment.export(filename, format=AUDIO_FORMAT)

        # Add the filename to the queue for transcription
        transcription_queue.put(filename)

    # Start listening in the background
    with Microphone(sample_rate=SAMPLING_RATE) as source:
        recognizer.adjust_for_ambient_noise(source)
    
    recognizer.listen_in_background(source, record_callback, phrase_time_limit=PHRASE_TIME_LIMIT)

    # Keep this thread alive until stop event is set
    while not stop_event.is_set():
        time.sleep(0.1)

def transcribe():
    whisper = Whisper(model_path=WHISPER_MODEL)

    while not stop_event.is_set():
        if not transcription_queue.empty():
            audio_file = transcription_queue.get()

            try:
                transcript = whisper.transcribe(audio_file)
            except Exception as e:
                print(f"Failed to transcribe {audio_file}: {e}")
                continue

            print(transcript)

            daily_file_path = OUTPUT_DIRECTORY / f"{datetime.datetime.now().strftime('%Y-%m-%d')}.txt"

            with file_lock:  # Ensure only one thread writes to the file at a time
                with daily_file_path.open('a') as daily_file:  # Open in append mode
                    daily_file.write(transcript + '\n')

            Path(audio_file).unlink(missing_ok=True)
            transcription_queue.task_done()

if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(record)
        executor.submit(transcribe)

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        stop_event.set()
