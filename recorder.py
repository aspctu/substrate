import datetime
import hashlib
import time

from pydub import AudioSegment
from speech_recognition import AudioData, Microphone, Recognizer

from constants import AUDIO_FORMAT, SAMPLING_RATE, CHANNELS, PHRASE_TIME_LIMIT


class Recorder:
    def __init__(self, transcription_queue, stop_event):
        self.transcription_queue = transcription_queue
        self.stop_event = stop_event

    def record(self):
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
            self.transcription_queue.put(filename)

        # Start listening in the background
        with Microphone(sample_rate=SAMPLING_RATE) as source:
            recognizer.adjust_for_ambient_noise(source)
        
        recognizer.listen_in_background(source, record_callback, phrase_time_limit=PHRASE_TIME_LIMIT)
        print("Starting recording...")

        # Keep this thread alive until stop event is set
        while not self.stop_event.is_set():
            time.sleep(0.1)
