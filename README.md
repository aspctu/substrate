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
python3 voice.py
```
Transcriptions will land in `transcriptions` folder under the current date.
