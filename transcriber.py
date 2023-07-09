import subprocess
import threading
from pathlib import Path

from constants import WHISPER_MODEL
from rich.console import Console
import queue

console = Console()

class Whisper:
    def __init__(self, model_path: Path = WHISPER_MODEL):
        self.model_path = model_path

    def transcribe(self, audio_file: Path) -> str:
        txt_file_path = Path(f"{audio_file}.txt")
        try:
            subprocess.run(
                [
                    './whisper.cpp/main', '-m', str(self.model_path), '-f',
                    str(audio_file), '--output-txt'
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
    def __init__(
        self,
        transcription_queue: queue.Queue,
        stop_event: threading.Event,
        output_file: Path
    ):
        self.whisper = Whisper()
        self.file_lock = threading.Lock()
        self.transcription_queue = transcription_queue
        self.stop_event = stop_event
        self.output_file = output_file

    def write(self, transcription: str) -> None:
        with self.file_lock:
            with self.output_file.open('a') as output_file:
                output_file.write(transcription + '\n')

    def transcribe(self) -> None:
        while not self.stop_event.is_set():
            if not self.transcription_queue.empty():
                audio_file = Path(self.transcription_queue.get())

                try:
                    transcript = self.whisper.transcribe(audio_file)
                    console.print(f"[green] {transcript.strip()} [/green]")
                except Exception as e:
                    console.print(f"[red]Failed to transcribe {audio_file}: {e}[/red]")
                    audio_file.unlink(missing_ok=True)
                    continue

                self.write(transcription=transcript)

                audio_file.unlink(missing_ok=True)
                self.transcription_queue.task_done()
