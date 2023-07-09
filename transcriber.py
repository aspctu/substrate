import subprocess
import queue
import threading
from pathlib import Path
from rich.console import Console

from constants import WHISPER_MODEL

console = Console()

class Whisper:
    """Handles the transcription of audio files using Whisper.cpp"""
    def __init__(self, model_name: str = WHISPER_MODEL):
        self.model_path = f"./whisper.cpp/models/ggml-{model_name}.bin"

    def transcribe(self, audio_file: Path) -> str:
        """Transcribes an audio file
        
        Args:
            audio_file (Path): The path to the audio file to transcribe.
        
        Returns:
            str: The transcription of the audio file.
        """
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
    """Transcribes queued audio files in a separate thread.

    This class continuously processes audio files for transcription
    via usage of the transcription queue.
    """
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
        """Writes the transcription to the output file.

        Args:
            transcription (str): The transcription to write.
        """
        with self.file_lock:
            with self.output_file.open('a') as output_file:
                output_file.write(transcription + '\n')

    def transcribe(self) -> None:
        """Transcribes audio files from the transcription queue, writes
        the transcription to the output file, and deletes the audio file.
        """
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
