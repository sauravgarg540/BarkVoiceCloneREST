    
# 🐶 Bark with REST API and Voice Cloning

This repository contains code for:
- text2speech synthesis by [Suno.ai](https://github.com/suno-ai). This supports different speakers, languages, emotions & singing.
- speaker generation aka voice cloning by [gitmylo](https://github.com/gitmylo)

All of this is wrapped into a convenient REST API with [FAST_API](https://fastapi.tiangolo.com/)

![image of openapi server](bark_fastapi.PNG)

The repos also simplifies setup of the bark repos and clone-voice repos, because all models are automatically downloaded.


## Disclaimer
This repository is a merge of the orignal [bark repository](https://github.com/suno-ai/bark) and [bark-voice-cloning-HuBert-quantizer](https://github.com/gitmylo/bark-voice-cloning-HuBERT-quantizer/blob/master/readme.md)
The credit goes to the original authors. Like the original authors, I am also not responsible for any misuse of this repository. Use at your own risk, and please act responsibly.


# Setup

1. Clone the repository.
2. (Optional) Create a virtual environment. With `python -m venv venv` and activate it with `venv/Scripts/activate`.
3. Install the requirements.
`pip install -r requirements.txt`
4. Don't forget to install pytorch gpu version (with `pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`)

# Usage

1. Start the server by running the provided .bat file "start_server.bat" 
   2. or by using `python bark/server.py --port 8009` make sure the python PYTHONPATH is set to the root of this repository.
2. To test the server, open `http://localhost:8009/docs` in your browser.

Then make post requests to the server with your favorite tool or library.
Here are some examples to inference with a python client.

Note: The first time you start the server, it will download the models. This can take a while.
If this fails, you can download the files manually or with the model_downloader.py script.

### For text2speech synthesis

```python
import requests
response = requests.post("http://localhost:8009/text2voice", params={ "text" : "please contribute", "speaker": "en_speaker_3"})
```
The response is a .wav file as bytes. You can save it with:

```python
import librosa
from io import BytesIO

# convert to audio file
audio_file, sr = librosa.load(BytesIO(response.content))
# save to file
sf.write(save_file_path, audio_file, sr)
```

### For speaker embedding generation

```python
import requests
with open("myfile.wav", "rb") as f:
    audio = f.read()
response = requests.post("http://localhost:8009/create_speaker_embedding", params={ "speaker_name" : "my_new_speaker"}, files={"audio_file": audio})
```
The response is a .npz file as bytes. 
After the embedding was created it can be used in text2speech synthesis.

### For voice2voice synthesis

```python
import requests
with open("myfile.wav", "rb") as f:
    audio = f.read()
response = requests.post("http://localhost:8009/voice2voice", params={ "speaker_name" : "my_new_speaker"}, files={"audio_file": audio})
```
In this example it is assumed that previously a speaker with name "my_new_speaker" was created with the create_speaker_embedding endpoint.

# Cloud environments

All settings relevant for execution are stored in settings.py and adjustable via environment variables.
When run in docker or a cloud environment, just set the environment variables accordingly.


# Contribute

any help with maintaining and extending the package is welcome. Feel free to open an issue or a pull request.
ToDo: make inference faster by keeping models in memory
