import requests


class TTSService:
    def __init__(self, base_url="http://127.0.0.1:3030"):
        self.base_url = base_url

    def synthesize(self, text, voice="zeus"):
        response = requests.post(
            f"{self.base_url}/generate",
            data={
                "text": text,
                "voice": voice,
            },
        )

        response.raise_for_status()

        return response.content