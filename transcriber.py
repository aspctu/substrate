import subprocess
import threading
from pathlib import Path

from constants import WHISPER_MODEL

class Whisper:
    def __init__(self, model_path):
        self.model_path = Path(model_path)

    def transcribe(self, audio_file):
        audio_file_path = Path(audio_file)
        txt_file_path = Path(f"{audio_file_path}.txt")
        try:
            subprocess.run(
                [
                    './whisper.cpp/main', '-m', str(self.model_path), '-f', 
                    str(audio_file_path), '--output-txt'
                ],
                check=True,
                text=True,
                capture_output=True
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

class Transcriber:
    def __init__(self, transcription_queue, stop_event, output_file):
        self.whisper = Whisper(model_path=WHISPER_MODEL)
        self.transcription_queue = transcription_queue
        self.stop_event = stop_event
        self.file_lock = threading.Lock()
        self.output_file = Path(output_file)

    def transcribe(self):
        while not self.stop_event.is_set():
            if not self.transcription_queue.empty():
                audio_file = self.transcription_queue.get()

                try:
                    transcript = self.whisper.transcribe(audio_file)
                    print(transcript)
                except Exception as e:
                    print(f"Failed to transcribe {audio_file}: {e}")
                    continue

                with self.file_lock: 
                    with self.output_file.open('a') as output_file:
                        output_file.write(transcript + '\n')

                Path(audio_file).unlink(missing_ok=True)
                self.transcription_queue.task_done()
