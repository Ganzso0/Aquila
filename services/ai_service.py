import json
import requests
from core.result import AgentResult
from core.request import AgentRequest


class AIService:

    def __init__(self, model: str = "qwen3:14b"):

        self.model = model
        self.url = "http://localhost:11434/api/chat"

    def interpret(self, text: str) -> AgentRequest:

        prompt = f"""
Eres Zeus, el orquestador de Lacerta.

Tu única función en esta etapa es interpretar la petición
del usuario y convertirla en un AgentRequest.

NO ejecutes ninguna acción.
NO expliques tu razonamiento.
NO escribas texto fuera del JSON.

Debes devolver SIEMPRE un JSON válido con exactamente esta estructura:

{{
    "intent": "...",
    "action": "...",
    "parameters": {{}},
    "context": {{}}
}}

Intenciones disponibles:

- conversation
- weather
- system

Acciones disponibles:

conversation:
- chat

weather:
- current
- forecast

system:
- open_application
- close_application

Ejemplos:

Usuario:
Hola, ¿qué tal?

Respuesta:
{{
    "intent": "conversation",
    "action": "chat",
    "parameters": {{}},
    "context": {{}}
}}

Usuario:
Abre Steam

Respuesta:
{{
    "intent": "system",
    "action": "open_application",
    "parameters": {{
        "application": "Steam"
    }},
    "context": {{}}
}}

Usuario:
¿Qué tiempo hará mañana en Barcelona?

Respuesta:
{{
    "intent": "weather",
    "action": "forecast",
    "parameters": {{
        "location": "Barcelona",
        "date": "tomorrow"
    }},
    "context": {{}}
}}

Petición del usuario:
{text}
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
        "stream": False
    }
)

        response.raise_for_status()

        data = response.json()

        print("Tiempo total:", data.get("total_duration", 0) / 1_000_000_000)
        print("Carga modelo:", data.get("load_duration", 0) / 1_000_000_000)
        print("Evaluación prompt:", data.get("prompt_eval_duration", 0) / 1_000_000_000)
        print("Generación:", data.get("eval_duration", 0) / 1_000_000_000)
        print("Tokens generados:", data.get("eval_count", 0))

        content = data["message"]["content"]

        parsed = json.loads(content)

        return AgentRequest(
            intent=parsed["intent"],
            action=parsed["action"],
            parameters=parsed.get("parameters", {}),
            context=parsed.get("context", {})
        )
    def generate_response(self, result: AgentResult) -> str:

        prompt = f"""
Eres Zeus, el orquestador de Lacerta.

Tu función es convertir el resultado de un agente
en una respuesta natural para el usuario.

El agente ya ha ejecutado la acción.
NO ejecutes ninguna acción.
NO inventes información.
NO expliques el proceso interno.
Responde únicamente con el mensaje que debería recibir el usuario.

Resultado del agente:

Agente: {result.agent_name}
Tipo: {result.type}
Mensaje: {result.message}
Datos: {json.dumps(result.data, ensure_ascii=False)}

Responde en español de forma natural, breve y clara.
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
            "stream": False
        }
    )

        response.raise_for_status()

        data = response.json()

        print("Tiempo total respuesta:", data.get("total_duration", 0) / 1_000_000_000)
        print("Carga modelo respuesta:", data.get("load_duration", 0) / 1_000_000_000)
        print("Evaluación prompt respuesta:", data.get("prompt_eval_duration", 0) / 1_000_000_000)
        print("Generación respuesta:", data.get("eval_duration", 0) / 1_000_000_000)
        print("Tokens generados respuesta:", data.get("eval_count", 0))

        return data["message"]["content"].strip()