import io
import wave
import tempfile
import os
import threading
import sounddevice as sd
import numpy as np
from mistralai import Mistral

from config import (
    MISTRAL_API_KEY,
    SAMPLE_RATE,
    CHANNELS,
    DTYPE,
    STT_MODEL,
    STT_LANGUAGE,
    TTS_MODEL,
    TTS_VOICE,
    SILENCE_THRESHOLD,
    RECORDING_TIMEOUT,
)


class VoiceEngine:
    def __init__(self):
        if not MISTRAL_API_KEY:
            raise ValueError("MISTRAL_API_KEY non definie. Creez un fichier .env")
        self.client = Mistral(api_key=MISTRAL_API_KEY)

    def record(self, stop_event):
        self.audio_data = None
        chunks = []
        stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=DTYPE,
        )
        stream.start()
        print("[Parle maintenant... (appuie sur Entree pour arreter)]")

        while not stop_event.is_set():
            chunk, _ = stream.read(512)
            chunks.append(chunk.copy())

        stream.stop()
        stream.close()

        if not chunks:
            print("[Aucun son detecte]")
            return

        audio_array = np.concatenate(chunks, axis=0)
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_array.tobytes())

        self.audio_data = wav_buffer.getvalue()
        print("[Enregistrement termine]")

    def transcribe(self, audio_bytes):
        res = self.client.audio.transcriptions.complete(
            model=STT_MODEL,
            file={"file_name": "audio.wav", "content": audio_bytes},
            language=STT_LANGUAGE,
        )
        return res.text.strip()

    def speak(self, text):
        if not text:
            return
        print(f"[Agent] {text}")
        os.system(f"say '{text}'")
