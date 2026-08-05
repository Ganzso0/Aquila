import speech_recognition as sr


class VoiceService:

    def listen(self):

        recognizer = sr.Recognizer()

        with sr.Microphone(device_index=1) as source:

            print("Calibrando ruido...")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

            print("Escuchando...")

            audio = recognizer.listen(source)


        try:

            text = recognizer.recognize_google(
                audio,
                language="es-ES"
            )

            return text


        except sr.UnknownValueError:

            return ""

        except sr.RequestError as e:

            print(e)
            return ""