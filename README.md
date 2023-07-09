## quickstart

### installation
First, install whisper.cpp in this directory
```
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp
make
```

Second, install other reqs
```
brew install portaudio ffmpeg
poetry install
```

### usage
```
poetry shell
python3 main.py
```

Transcriptions will land in `output.txt` in real-time unless invoked with `output` flag

```
python3 main.py --output="path/to/my/file"
```
