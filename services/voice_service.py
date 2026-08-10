
import pyttsx3
import re


class VoiceService:

    def __init__(self):

        # Configuración del motor
        self.rate = 175
        self.volume = 1.0

    def speak(self, text: str):

        clean_text = self._clean_for_speech(text)

        if not clean_text:
            return

        try:

            # Crear un motor nuevo para cada respuesta
            engine = pyttsx3.init()

            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)

            engine.say(clean_text)
            engine.runAndWait()

            engine.stop()

        except Exception as e:

            print("Error en VoiceService:", e)

    def _clean_for_speech(self, text: str) -> str:

        # Eliminar URLs
        text = re.sub(
            r"https?://\S+",
            "",
            text
        )

        # Convertir Markdown:
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
        # Lo dejamos preparado para implementar
        # entrada por voz en el futuro.
        pass

    def __repr__(self):
        return "<VoiceService>"

