
import io
import re

import numpy as np
import requests
import sounddevice as sd
import soundfile as sf


class VoiceService:

    def __init__(
        self,
        base_url="http://127.0.0.1:3030",
        voice="zeus"
    ):
        self.base_url = base_url
        self.voice = voice

    def speak(self, text: str):

        clean_text = self._clean_for_speech(text)

        if not clean_text:
            return

        try:

            response = requests.post(
                f"{self.base_url}/generate",
                files={
                    "text": (None, clean_text),
                    "voice": (None, self.voice),
                },
                timeout=120
            )

            response.raise_for_status()

            # El WAV permanece completamente en memoria.
            audio_data = response.content

            # Leer directamente el WAV desde RAM.
            audio, sample_rate = sf.read(
                io.BytesIO(audio_data),
                dtype="float32"
            )

            # Reproducir directamente desde RAM.
            sd.play(
                audio,
                samplerate=sample_rate
            )

            # Esperar a que termine.
            sd.wait()

        except requests.RequestException as e:

            print(
                "Error conectando con el servidor TTS:",
                e
            )

        except Exception as e:

            print(
                "Error en VoiceService:",
                e
            )

    def _clean_for_speech(self, text: str) -> str:

        # Eliminar URLs
        text = re.sub(
            r"https?://\S+",
            "",
            text
        )

        # [Leer más](url) -> Leer más
        text = re.sub(
            r"\[([^\]]+)\]\([^)]+\)",
            r"\1",
            text
        )

        # Eliminar negritas
        text = text.replace("**", "")

        # Eliminar cursivas
        text = text.replace("*", "")

        # Eliminar encabezados Markdown
        text = re.sub(
            r"^\s*#+\s*",
            "",
            text,
            flags=re.MULTILINE
        )

        # Eliminar bloques de código
        text = text.replace("```", "")

        # Limpiar listas
        text = re.sub(
            r"^\s*[-•]\s*",
            "",
            text,
            flags=re.MULTILINE
        )

        # Eliminar numeración
        text = re.sub(
            r"^\s*\d+\.\s*",
            "",
            text,
            flags=re.MULTILINE
        )

        # Eliminar espacios repetidos
        text = re.sub(
            r"[ \t]+",
            " ",
            text
        )

        # Eliminar demasiados saltos de línea
        text = re.sub(
            r"\n{2,}",
            "\n",
            text
        )

        return text.strip()

    def listen(self):
        # Preparado para implementar entrada por voz.
        pass

    def __repr__(self):
        return "<VoiceService>"

