import datetime
import hashlib
import time
from pathlib import Path
import queue
import threading

from pydub import AudioSegment
from rich.console import Console
from speech_recognition import AudioData, Microphone, Recognizer

from constants import (
    AUDIO_FORMAT,
    CHANNELS,
    PHRASE_TIME_LIMIT,
    SAMPLING_RATE,
    PAUSE_THRESHOLD,
    ENERGY_THRESHOLD
)
console = Console()


class Recorder:
    """A recorder that listens to the microphone and adds audio data to a
    queue.

    This recorder utilizes the speech_recognition library to continuously
    listen and chunk phrases. When a phrase is detected, the audio data is
    serialized to disk and the file path is added to a queue for transcription.

    Attributes:
        transcription_queue (queue.Queue): The queue where audio file paths
            are placed.
        stop_event (threading.Event): An event that can be set to stop the
            recording.
        recognizer (Recognizer): The Recognizer instance used to capture audio.
    """
    def __init__(
        self,
        transcription_queue: queue.Queue,
        stop_event: threading.Event
    ):
        self.transcription_queue = transcription_queue
        self.stop_event = stop_event
        self.recognizer = Recognizer()
        self.recognizer.energy_threshold = ENERGY_THRESHOLD
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.pause_threshold = PAUSE_THRESHOLD


    def serialize_buffer(self, audio: AudioData) -> Path:
        """Converts AudioData to the specified audio format and saves it to disk.

        Args:
            audio (AudioData): The raw audio data to convert and save.

        Returns:
            Path: The path of the saved audio file.
        """
        def _generate_filename() -> str:
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            return f"{hashlib.sha1(timestamp.encode()).hexdigest()}.{AUDIO_FORMAT}"

        raw_data = audio.get_raw_data(
            convert_rate=SAMPLING_RATE,
            convert_width=2,
        )
        audio_segment = AudioSegment(
            data=raw_data,
            sample_width=2,
            frame_rate=SAMPLING_RATE,
            channels=CHANNELS
        )

        serialize_path = Path(_generate_filename())
        audio_segment.export(serialize_path, format=AUDIO_FORMAT)
        return serialize_path

    def record(self) -> None:
        """Starts recording audio from the microphone in the background and adds it
        to a queue for transcription when a phrase is detected."""
        def record_callback(recognizer: Recognizer, audio: AudioData) -> None:
            filename = self.serialize_buffer(audio)
            self.transcription_queue.put(filename)

        # Start listening in the background
        with Microphone(sample_rate=SAMPLING_RATE) as source:
            self.recognizer.adjust_for_ambient_noise(source)

        self.recognizer.listen_in_background(
            source,
            record_callback,
            phrase_time_limit=PHRASE_TIME_LIMIT
        )

        console.print("[bold green]Starting recording...")

        # Keep this thread alive until stop event is set
        while not self.stop_event.is_set():
            time.sleep(0.1)
