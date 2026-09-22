
import json
import requests
from pathlib import Path


class HecateService:

    def __init__(self, model="granite4:3b"):
        self.model = model
        self.url = "http://localhost:11434/api/chat"

        prompt_path = Path(__file__).parent / "hecate_prompt.txt"

        with open(prompt_path, "r", encoding="utf-8") as f:
            self.prompt = f.read()

    def plan(
        self,
        user_request: str,
        requests_data: list[dict]
    ) -> dict:

        input_data = {
            "user_request": user_request,
            "requests": requests_data
        }

        prompt = f"""
{self.prompt}

DATOS DE ENTRADA:

{json.dumps(input_data, ensure_ascii=False, indent=2)}
"""

        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "think": False,
                "stream": False,
                "options": {
                    "num_predict": 1000
                }
            }
        )

        response.raise_for_status()

        content = response.json()["message"]["content"]

        print("\n--- RAW HÉCATE RESPONSE ---")
        print(content)
        print("--- END RAW HÉCATE RESPONSE ---\n")

        content = content.strip()

        if content.startswith("```json"):
            content = content[7:]

        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()

        return json.loads(content)
