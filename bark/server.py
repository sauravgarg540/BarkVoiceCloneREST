import argparse
from io import BytesIO

import fastapi
import uvicorn
from fastapi.responses import StreamingResponse
from scipy.io import wavfile

import text2voice as t2v
import voice_cloning.embedding_creator as embedding_creator
from bark.model_downloader import download_all_models_init
from bark.settings import DEFAULT_PORT, DEFAULT_SPEAKER_DIR

import os
import numpy as np

from bark.utils import encode_path_safe
from bark.voice2voice import swap_voice_from_audio

app = fastapi.FastAPI(
    title="Bark FastAPI with voice cloning",
    summary="Create audio from text, clone voices and use them. Convert voice2voice",
    version="0.0.1",
    contact={
        "name": "w4hns1nn",
        "url": "https://github.com/w4hns1nn",
    }
)


@app.post("/text2voice")
async def text2voice(
        text: str,
        voice_name_or_embedding_path: str = "en_speaker_3",
        semantic_temp: float = 0.7,
        semantic_top_k: int = 50,
        semantic_top_p: float =0.95,
        coarse_temp: float = 0.7,
        coarse_top_k: int = 50,
        coarse_top_p: float =0.95,
        fine_temp: float = 0.5
    ):
    """
    :param text: the text to be converted
    :param voice_name: the name of the voice to be used. Uses the pretrained voices which are stored in models/speakers folder. It is also possible to provide a full path.
    :return: the audio file as bytes
    """

    # validate parameters
    # remove any illegal characters from text
    text = encode_path_safe(text)


    generated_audio_file, sample_rate = t2v.text2voice(
        text=text,
        voice_name_or_embedding_path=voice_name_or_embedding_path,
        semantic_temp=semantic_temp,
        semantic_top_k=semantic_top_k,
        semantic_top_p=semantic_top_p,
        coarse_temp=coarse_temp,
        coarse_top_k=coarse_top_k,
        coarse_top_p=coarse_top_p,
        fine_temp=fine_temp
    )

    # make a recognizable filename
    filename = text[:15] if len(text) > 15 else text
    filename = f"{filename}_{os.path.basename(voice_name_or_embedding_path)}.wav"

    return StreamingResponse(
        generated_audio_file,
        media_type="audio/wav",
        headers={"Content-Disposition": f"attachment; filename={filename}.wav"}
    )

@app.post("/speaker_embedding_generation")
async def create_speaker_embedding(audio_file: fastapi.UploadFile, speaker_name: str = "new_speaker", save_in_speaker_dir: bool = True):
    """
    :param audio_file: the audio file as bytes 5-20s is good length
    :param speaker_name: how the new speaker / embedding is named
    :param save_in_speaker_dir: if the embedding should be saved in the speaker dir for reusage
    :return: the speaker embedding as bytes
    """
    # convert audio to bytes file
    audio_bytes = await audio_file.read()
    temp_audio_file = BytesIO(audio_bytes)
    # create embedding vector
    codes, semantic_tokens = embedding_creator.clone_voice(temp_audio_file)

    # write speaker embedding to file
    if save_in_speaker_dir:
        speaker_embedding_file = os.path.join(DEFAULT_SPEAKER_DIR, f"{speaker_name}.npz")
        np.savez(speaker_embedding_file, fine_prompt=codes, coarse_prompt=codes[:2, :], semantic_prompt=semantic_tokens)
        # loading it again to temp file to be able to return it as response
        with open(speaker_embedding_file, "rb") as f:
            open_file = BytesIO(f.read())
    else:
        open_file = BytesIO()
        np.savez(open_file, fine_prompt=codes, coarse_prompt=codes[:2, :], semantic_prompt=semantic_tokens)

    return StreamingResponse(
        open_file,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={speaker_name}.npz"}
    )


@app.post("/voice2voice")
async def voice2voice(
        audio_file: fastapi.UploadFile,
        speaker_name: str,
):
    """
    :param audio_file: the audio file as bytes 5-20s is good length
    :param speaker_name: how the new speaker / embedding is named
    :return: the converted audio file as bytes
    """
    # convert audio to bytes file
    audio_bytes = await audio_file.read()
    temp_audio_file = BytesIO(audio_bytes)

    # inference
    audio_array, sample_rate = swap_voice_from_audio(temp_audio_file, speaker_name)

    # write speaker embedding to temp file
    open_file = BytesIO()
    wavfile.write(open_file, rate=sample_rate, data=audio_array)

    return StreamingResponse(
        open_file,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={speaker_name}.npz"}
    )

@app.get("/status")
def status():
    return {"status": "ok"}


# first time load and install models
download_all_models_init()

# start the server on provided port
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--port", type=int, default=DEFAULT_PORT)
args = arg_parser.parse_args()
uvicorn.run(app, host="localhost", port=args.port)