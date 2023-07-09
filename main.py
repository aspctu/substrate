import argparse
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from queue import Queue

from recorder import Recorder
from transcriber import Transcriber

if __name__ == "__main__":
    arguments = argparse.ArgumentParser()
    arguments.add_argument("--output", type=str, default="output.txt")
    args = arguments.parse_args()

    transcription_queue = Queue()
    stop_event = threading.Event()

    recorder = Recorder(transcription_queue, stop_event)
    transcriber = Transcriber(
        transcription_queue,
        stop_event,
        Path(args.output)
    )

    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(recorder.record)
        executor.submit(transcriber.transcribe)

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        stop_event.set()
