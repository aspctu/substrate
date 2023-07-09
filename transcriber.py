import subprocess
import threading
from pathlib import Path

from constants import WHISPER_MODEL
from rich.console import Console

console = Console()

class Whisper:
    def __init__(self, model_path):
        self.model_path = Path(model_path)

    def transcribe(self, audio_file: str) -> str:
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
            console.print(f"[red]Whisper command failed: {e}[/red]")
            return None

        # Read in the generate file txt
        transcription = txt_file_path.read_text()
        
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

    def write(self, transcription: str) -> None:
        with self.file_lock:
            with self.output_file.open('a') as output_file:
                output_file.write(transcription + '\n')

    def transcribe(self):
        while not self.stop_event.is_set():
            if not self.transcription_queue.empty():
                audio_file = self.transcription_queue.get()

                try:
                    transcript = self.whisper.transcribe(audio_file)
                    console.print(f"[blue]{transcript} [/blue]")
                except Exception as e:
                    console.print(f"[red]Failed to transcribe {audio_file}: {e}[/red]")
                    continue

                self.write(transcription=transcript)

                Path(audio_file).unlink(missing_ok=True)
                self.transcription_queue.task_done()
