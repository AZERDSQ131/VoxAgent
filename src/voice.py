import io
import wave
import tempfile
import os
import sounddevice as sd
import numpy as np
from mistralai.client import Mistral

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

    def record(self, callback_start=None, callback_stop=None):
        print("[Parle maintenant...]")
        if callback_start:
            callback_start()

        audio_data = []
        stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=DTYPE,
        )
        stream.start()

        silent_chunks = 0
        max_silent = int(SAMPLE_RATE / 512 * 1.5)
        started = False
        chunks_recorded = 0
        max_chunks = int(SAMPLE_RATE / 512 * RECORDING_TIMEOUT)

        try:
            while chunks_recorded < max_chunks:
                chunk, _ = stream.read(512)
                amplitude = np.max(np.abs(chunk))
                if amplitude > SILENCE_THRESHOLD:
                    if not started:
                        started = True
                    silent_chunks = 0
                    audio_data.append(chunk.copy())
                elif started:
                    silent_chunks += 1
                    audio_data.append(chunk.copy())
                    if silent_chunks > max_silent:
                        break
                chunks_recorded += 1
        finally:
            stream.stop()
            stream.close()

        if not audio_data:
            print("[Aucun son detecte]")
            return None

        audio_array = np.concatenate(audio_data, axis=0)
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_array.tobytes())
        wav_bytes = wav_buffer.getvalue()

        print("[Enregistrement termine]")
        if callback_stop:
            callback_stop()

        return wav_bytes

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
        print(f"[Voix] {text}")
        try:
            res = self.client.audio.speech.complete(
                model=TTS_MODEL,
                input=text,
                voice=TTS_VOICE,
            )
            if hasattr(res, "data") and res.data:
                audio_bytes = res.data
            elif isinstance(res, bytes):
                audio_bytes = res
            else:
                raise ValueError("Format reponse TTS inattendu")
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp.write(audio_bytes)
            tmp.close()
            os.system(f"afplay {tmp.name} && rm {tmp.name}")
        except Exception as e:
            print(f"[TTS erreur, fallback say] {e}")
            os.system(f"say '{text}'")
