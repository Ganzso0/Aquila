import json
import requests

from pathlib import Path

from core.models.interpretation_result import InterpretationResult
from core.models.result import AgentResult


class LogosService:

    def __init__(
        self,
        prompt_path = Path(__file__).parent / "logos_prompt.txt",
        url: str = "http://localhost:11434/api/chat",
        model: str = "granite4:3b",
    ):
        self.url = url
        self.model = model

        self.prompt_template = Path(
            prompt_path
        ).read_text(
            encoding="utf-8"
        )

    def generate_response(
        self,
        text: str,
        interpretation: InterpretationResult,
        results: list[AgentResult],
        history: list[dict],
    ) -> str:

        history_text = self._build_history(history)
        requests_text = self._build_requests(interpretation)
        results_text = self._build_results(results)

        prompt = f"""
{self.prompt_template}

HISTORIAL DE LA CONVERSACIÓN

{history_text}

PETICIÓN ACTUAL

{text}

INTERPRETACIÓN DE NOUS

Planning required:
{interpretation.planning_required}

Requests:

{requests_text}

RESULTADOS DE LOS AGENTES

{results_text}

Genera únicamente la respuesta final que debe recibir el usuario.
"""

        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "stream": False,
                "think": False,
                "options": {
                    "num_predict": 500,
                },
            },
        )

        response.raise_for_status()

        data = response.json()

        print(
            "Tiempo total respuesta:",
            data.get("total_duration", 0) / 1_000_000_000,
        )

        print(
            "Carga modelo respuesta:",
            data.get("load_duration", 0) / 1_000_000_000,
        )

        print(
            "Evaluación prompt respuesta:",
            data.get("prompt_eval_duration", 0) / 1_000_000_000,
        )

        print(
            "Generación respuesta:",
            data.get("eval_duration", 0) / 1_000_000_000,
        )

        print(
            "Tokens generados respuesta:",
            data.get("eval_count", 0),
        )

        return data["message"]["content"].strip()

    def _build_history(
        self,
        history: list[dict],
    ) -> str:

        if not history:
            return "(Sin historial)"

        history_text = ""

        for message in history:

            role = (
                "Usuario"
                if message["role"] == "user"
                else "Logos"
            )

            history_text += (
                f"{role}: {message['content']}\n"
            )

        return history_text

    def _build_requests(
        self,
        interpretation: InterpretationResult,
    ) -> str:

        if not interpretation.requests:
            return "(Sin peticiones interpretadas)"

        requests_text = ""

        for i, request in enumerate(
            interpretation.requests,
            1,
        ):

            requests_text += f"""
Petición {i}:

Intent:
{request.intent}

Action:
{request.action}

Parameters:
{json.dumps(
    request.parameters,
    ensure_ascii=False,
    indent=2,
)}

Context:
{json.dumps(
    request.context,
    ensure_ascii=False,
    indent=2,
)}
"""

        return requests_text

    def _build_results(
        self,
        results: list[AgentResult],
    ) -> str:

        if not results:
            return "(No se obtuvieron resultados de los agentes)"

        results_text = ""

        for result in results:

            results_text += f"""
Agente:
{result.agent_name}

Tipo:
{result.type}

Éxito:
{result.success}

Mensaje:
{result.message}

Datos:
{json.dumps(
    result.data,
    ensure_ascii=False,
    indent=2,
)}
"""

        return results_text