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
    "context": {{}},
    "requests":[]
}}

Intenciones disponibles:

- conversation
- weather
- system
- news

Acciones disponibles:

conversation:
- chat

weather:
- current
- forecast

system:
- open_application
- close_application


news:

- search
  - query
  - date
  - category

categories:

- general
- technology
- sports
- finance
- science

Ejemplos:

Si el usuario realiza UNA sola peticion:

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
¿Qué noticias hay hoy sobre NVIDIA?

Respuesta:
{{
"intent": "news",
"action": "search",
"parameters": {{
"query": "NVIDIA",
"date": "today",
"category": "technology"
}},
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

Usuario:
¿Va a llover hoy en Valdemoro?

Respuesta:
{{
    "intent": "weather",
    "action": "current",
    "parameters": {{
        "location": "Valdemoro",
        "date": "today"
    }},
    "context": {{}}
}}

Usuario:
¿Va a llover hoy?

Respuesta:
{{
    "intent": "weather",
    "action": "current",
    "parameters": {{
        "location": null,
        "date": "today"
    }},
    "context": {{}}
}}

Si el usuario realiza VARIAS petieicones diferentes, No debes meterlas dentro de context. Debes utilizar "requests".

Usuario: 
Dime el tiempo en Valdemoro y las noticias de Argentina. 

Respuesta: 
{{ 
    "intent": "weather", 
"action": "current", 
"parameters": {{ 
    "location": "Valdemoro", 
"date": "today" }}, 
"context": {{}}, 
"requests": [ 
{{ 
    "intent": "weather", 
"action": "current", 
"parameters": {{ 
    "location": "Valdemoro", 
"date": "today" 
}},
 "context": {{}} 
}}, 
{{ 
"intent": "news", 
"action": "search", 
"parameters": {{ 
"query": "Argentina",
"date": "today",
"category": "general" 
}}, 
"context": {{}} 
}} 
] 

}}

IMPORTANTE:

Cuando haya varias peticiones: 
- "intent" debe contener la primera petición.
- "action" debe contener la primera acción. 
- "parameters" debe contener los parámetros de la primera petición. 
- "context" debe permanecer vacío salvo que exista contexto real.
- "requests" debe contener TODAS las peticiones. 
- No utilices "context" para almacenar otras peticiones.

Una conversación normal es una única petición. 
Ejemplo: 

Usuario: 
Hola Zeus

Respuesta: 
{{ "intent": "conversation", 
"action": "chat", 
"parameters": {{}}, 
"context": {{}}, 
"requests": [] }} 
Si existe una petición de conversación junto con otras peticiones, también debe aparecer dentro de "requests".


Utiliza: 
- today 
- tomorrow 
- yesterday 
Si el usuario proporciona una fecha concreta, conserva la fecha indicada. 
Ejemplo:
 Usuario:
 Dime las noticias de NVIDIA de 2022. 
 Respuesta: 
 {{ "intent": "news", 
 "action": "search", 
 "parameters": {{ 
    "query": "NVIDIA", 
    "date": "2022", 
    "category": "technology" 
    }},
      "context": {{}}, 
      "requests": [] 
      }}

================================================== 
REGLAS IMPORTANTES
================================================== 

1. Devuelve únicamente JSON válido. 

2. No inventes parámetros. 

3. Si no se especifica una categoría de noticias, utiliza "general". 

4. Si no se especifica fecha para noticias, utiliza "today". 

5. Si el usuario pide el tiempo "ahora" o "actual", utiliza weather + current. 

6. Si el usuario pregunta por el tiempo de otro día, utiliza weather + forecast. 

7. Si hay varias peticiones independientes, utiliza "requests". 

8. NO coloques peticiones adicionales dentro de "context". 

9. La lista "requests" debe contener objetos con esta estructura:
 {{ 
    "intent": "...", 
    "action": "...",
    "parameters": {{}},
    "context": {{}} 
     }}

 10. Si solamente existe una petición, deja "requests" como [].


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
        "think": False,
        "stream": False,
        "options": {
    "num_predict": 180
}
    }
)

        response.raise_for_status()

        data = response.json()

        print("Tiempo total:", data.get("total_duration", 0) / 1_000_000_000)
        print("Carga modelo:", data.get("load_duration", 0) / 1_000_000_000)
        print("Evaluación prompt:", data.get("prompt_eval_duration", 0) / 1_000_000_000)
        print("Generación:", data.get("eval_duration", 0) / 1_000_000_000)
        print("Tokens generados:", data.get("eval_count", 0))

        content = data["message"]["content"].strip()

        if content.startswith("```json"):
            content = content[7:]

        elif content.startswith("```"):
            content = content[3:]

        if content.endswith("```"): 
            content = content[:-3] 
            content = content.strip()

        parsed = json.loads(content)

        return AgentRequest(
            intent=parsed["intent"],
            action=parsed["action"],
            parameters=parsed.get("parameters", {}),
            context=parsed.get("context", {}),
            requests=parsed.get("requests", [])
        )
    def generate_response(
    self,
    text: str,
    request: AgentRequest,
    results: list[AgentResult]
        ) -> str:

        results_text = ""

        for result in results:

            results_text += f"""
        Agente: {result.agent_name}
        Tipo: {result.type}
        Mensaje: {result.message}
        Datos: {json.dumps(result.data, ensure_ascii=False)}
            """

        prompt = f"""
Eres Zeus, el orquestador de Lacerta.

Tu función es convertir los resultados obtenidos
por los agentes en una respuesta natural para el usuario.

El agente ya ha ejecutado la acción.
NO ejecutes ninguna acción.
NO inventes información.
NO expliques el proceso interno.

Debes responder ÚNICAMENTE a la petición
original del usuario.

IMPORTANTE:

- Utiliza únicamente los datos proporcionados por los agentes. 
- Si hay varios resultados, combina la información. 
- Responde a TODAS las peticiones del usuario. 
- No ignores ninguna petición. 
- No inventes datos. 
- No inventes noticias. 
- Si un agente no obtuvo resultados, dilo claramente. 
- Puedes utilizar las URLs proporcionadas por los agentes. 
- No ocultes las URLs. 
- Responde en español. 
- Sé natural y claro. 
- No repitas información innecesariamente.

Petición original del usuario:

{text}

Interpretación de Zeus:

Intent: {request.intent}
Action: {request.action}

Parameters:
{json.dumps(request.parameters, ensure_ascii=False, indent=2)}

Context:
{json.dumps(request.context, ensure_ascii=False, indent =2)}

Multiple requests:
{json.dumps(request.requests, ensure_ascii=False, indent=2)}

Resultados de los agentes:

{results_text}

Genera únicamente la respuesta que debería recibir el usuario.
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
            "stream": False,
            "think": False,
            "options": {
                "num_predict": 180
            }
        }
    )

        response.raise_for_status()

        data = response.json()

        print(
        "Tiempo total respuesta:",
        data.get("total_duration", 0) / 1_000_000_000
    )

        print(
        "Carga modelo respuesta:",
        data.get("load_duration", 0) / 1_000_000_000
    )

        print(
        "Evaluación prompt respuesta:",
        data.get("prompt_eval_duration", 0) / 1_000_000_000
    )

        print(
        "Generación respuesta:",
        data.get("eval_duration", 0) / 1_000_000_000
    )

        print(
        "Tokens generados respuesta:",
        data.get("eval_count", 0)
    )

        return data["message"]["content"].strip()