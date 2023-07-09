## substrate
<img src="https://github.com/aspctu/substrate/assets/48742992/9b4749b2-e676-44bc-b153-d5d6bd366388" width="600"/>

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

### credits
❤️ to [whisper.cpp](https://github.com/ggerganov/whisper.cpp) and [speech_recognition](https://github.com/Uberi/speech_recognition)
