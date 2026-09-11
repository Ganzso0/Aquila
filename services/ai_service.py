import json
import requests
from core.result import AgentResult
from core.request import AgentRequest
from core.interpretation_result import InterpretationResult



class AIService:
    def __init__(self, model: str = "qwen3:14b"):

        self.model = model
        self.url = "http://localhost:11434/api/chat"

    def interpret(self, text: str, history: list[dict] | None = None, request_history: list[dict] | None = None) -> InterpretationResult:


        history = history or []

        history_text = ""

        for message in history:
            role = "Usuario" if message["role"] == "user" else "Zeus"
            history_text += f"{role}: {message['content']}\n"


        request_history = request_history or []

        request_history_text = ""

        for request in request_history:
            request_history_text += (
            f"[request_id={request['request_id']}] "
            f"Usuario: {request['content']}\n"
            )


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
- favorites
- memory
- music
- astronomy

Acciones disponibles:

conversation:
- chat

weather:
- current
- forecast

system:
- open_application
- close_application

memory

- save
- get
- list
- delete

favorites:
- save
- get
- list
- delete

news:

- search
  - query
  - date
  - category

-categories:
    - general
    - technology
    - sports
    - finance
    - science

music:
- play
- pause
- next
- previous
- current
- volume
- search

astronomy:
    -object:
        - object
        - location
        - date
        - time

    -sky:
        - location
        - date
        - time


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

Usuario:

Guarda en memoria que mi color favorito es amarillo.

Respuesta:

{{
    "intent": "memory",
    "action": "save",
    "parameters": {{
        "type": "preference",
        "key": "favorite_color",
        "value": "amarillo"
}},
    "context": {{}},
    "requests": []
}}

Usuario:

"¿Cuál es mi color favorito?"

Respuesta:

{{
    "intent": "memory",
    "action": "get",
    "parameters": {{
        "type": "preference",
        "key": "favorite_color"
    }},
    "context": {{}},
    "requests": []
}}

Usuario:

¿Qué cosas tienes guardadas en mi memoria?

Respuesta:

{{
"intent": "memory",
"action": "list",
"parameters": {{}},
"context": {{}},
"requests": []
}}

Usuario:

Borra de memoria mi color favorito.

Respuesta:

{{
"intent": "memory",
"action": "delete",
"parameters": {{
"type": "preference",
"key": "favorite_color"
}},
"context": {{}},
"requests": []
}}

Usuario:

Quiero comprarme el Sky-Watcher 200P, guárdalo en favoritos.

Respuesta:

{{
"intent": "favorites",
"action": "save",
"parameters": {{
"category": "telescope",
"summary": "Sky-Watcher 200P como posible próximo telescopio",
"prompt": "Quiero comprarme el Sky-Watcher 200P, guárdalo en favoritos."
}},
"context": {{}},
"requests": []
}}

Usuario:

Guarda Monster Hunter World en favoritos.

Respuesta:

{{
"intent": "favorites",
"action": "save",
"parameters": {{
"category": "game",
"summary": "Monster Hunter World",
"prompt": "Guarda Monster Hunter World en favoritos."
}},
"context": {{}},
"requests": []
}}

Usuario:

¿Qué tengo guardado en favoritos?

Respuesta:

{{
"intent": "favorites",
"action": "list",
"parameters": {{}},
"context": {{}},
"requests": []
}}

Usuario:

¿Qué tengo guardado en favoritos de telescopios?

Respuesta:

{{
"intent": "favorites",
"action": "list",
"parameters": {{
"category": "telescope"
}},
"context": {{}},
"requests": []
}}

Usuario:

Enséñame el favorito número 2.

Respuesta:

{{
"intent": "favorites",
"action": "get",
"parameters": {{
"id": 2
}},
"context": {{}},
"requests": []
}}

Usuario:

Borra el favorito número 2.

Respuesta:

{{
"intent": "favorites",
"action": "delete",
"parameters": {{
"id": 2
}},
"context": {{}},
"requests": []
}}

Usuario:

Guarda en favoritos que mi color favorito es amarillo.

Respuesta:

{{
"intent": "favorites",
"action": "save",
"parameters": {{
"category": "preference",
"summary": "Color favorito: amarillo",
"prompt": "Guarda en favoritos que mi color favorito es amarillo."
}},
"context": {{}},
"requests": []
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


Usuario:
Pon música

Respuesta:
{{
    "intent": "music",
    "action": "play",
    "parameters": {{}},
    "context": {{}},
    "requests": []
}}

Usuario:
Reproduce música

Respuesta:
{{
    "intent": "music",
    "action": "play",
    "parameters": {{}},
    "context": {{}},
    "requests": []
}}

Usuario:
Pausa la música

Respuesta:
{{
    "intent": "music",
    "action": "pause",
    "parameters": {{}},
    "context": {{}},
    "requests": []
}}

Usuario:
Para la música

Respuesta:
{{
    "intent": "music",
    "action": "pause",
    "parameters": {{}},
    "context": {{}},
    "requests": []
}}

Usuario:
Detén la música

Respuesta:
{{
    "intent": "music",
    "action": "pause",
    "parameters": {{}},
    "context": {{}},
    "requests": []
}}

Usuario:
Siguiente canción

Respuesta:
{{
    "intent": "music",
    "action": "next",
    "parameters": {{}},
    "context": {{}},
    "requests": []
}}

Usuario:
Canción anterior

Respuesta:
{{
    "intent": "music",
    "action": "previous",
    "parameters": {{}},
    "context": {{}},
    "requests": []
}}

Usuario:
Pon el volumen al 50%

Respuesta:
{{
    "intent": "music",
    "action": "volume",
    "parameters": {{
        "volume": 50
    }},
    "context": {{}},
    "requests": []
}}

Usuario:
Pon el volumen al máximo

Respuesta:
{{
    "intent": "music",
    "action": "volume",
    "parameters": {{
        "volume": 100
    }},
    "context": {{}},
    "requests": []
}}

Usuario:
Pon el volumen al mínimo

Respuesta:
{{
    "intent": "music",
    "action": "volume",
    "parameters": {{
        "volume": 0
    }},
    "context": {{}},
    "requests": []
}}

Usuario:
Sube un poco el volumen

Respuesta:
{{
    "intent": "music",
    "action": "volume",
    "parameters": {{
        "change": 10
    }},
    "context": {{}},
    "requests": []
}}

Usuario:
Baja un poco el volumen

Respuesta:
{{
    "intent": "music",
    "action": "volume",
    "parameters": {{
        "change": -10
    }},
    "context": {{}},
    "requests": []
}}

Usuario:
Reduce el volumen

Respuesta:
{{
    "intent": "music",
    "action": "volume",
    "parameters": {{
        "change": -10
    }},
    "context": {{}},
    "requests": []
}}

Usuario:
Sube el volumen

Respuesta:
{{
    "intent": "music",
    "action": "volume",
    "parameters": {{
        "change": 10
    }},
    "context": {{}},
    "requests": []
}}

Usuario:
Pon NUEVAYOL de Bad Bunny

Respuesta:
{{
  "intent": "music",
  "action": "play",
  "parameters": {{
    "song": "NUEVAYOL",
    "artist": "Bad Bunny"
  }}
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

Usuario:
¿Dónde está Júpiter ahora?

Respuesta:
{{
    "intent": "astronomy",
    "action": "object",
    "parameters": {{
        "object": "jupiter",
        "location": null,
        "date": "today",
        "time": "now"
    }},
    "context": {{}},
    "requests": []
}}

Usuario:
¿Dónde estará Saturno mañana a las 23:00?

Respuesta:
{{
    "intent": "astronomy",
    "action": "object",
    "parameters": {{
        "object": "saturn",
        "location": null,
        "date": "tomorrow",
        "time": "23:00:00"
}},
    "context": {{}},
    "requests": []
}}

Usuario:
¿Dónde está Marte dentro de 2 horas?

Respuesta:
{{
    "intent": "astronomy",
    "action": "object",
    "parameters": {{
        "object": "mars",
        "location": null,
        "date": "today",
        "time": "in_2_hours"
    }},
    "context": {{}},
    "requests": []
}}

Usuario:
¿Dónde está Júpiter ahora en Madrid?

Respuesta:
{{
    "intent": "astronomy",
    "action": "object",
    "parameters": {{
        "object": "jupiter",
        "location": "Madrid",
        "date": "today",
        "time": "now"
    }},
    "context": {{}},
    "requests": []
}}

Usuario:
¿Qué puedo ver en el cielo esta noche?

Respuesta:
{{
    "intent": "astronomy",
    "action": "sky",
    "parameters": {{
        "location": null,
        "date": "today",
        "time": "tonight"
    }},
    "context": {{}},
    "requests": []
}}

================================================== 
REGLAS IMPORTANTES
================================================== 

1. Devuelve únicamente JSON válido. 

2. No inventes parámetros ni valores.
   Solo utiliza valores por defecto cuando se indiquen
   explícitamente en estas instrucciones.

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
10. Para music + volume:

    - Si el usuario indica un porcentaje concreto, utiliza "volume".
    - Si el usuario pide subir o bajar el volumen, utiliza "change".
    - "change" representa el cambio en puntos porcentuales.
    - "sube un poco" = 10.
    - "baja un poco" = -10.
    - Nunca dejes "parameters" vacío para music + volume.
    - Si el usuario especifica una canción Y un artista,
      debes incluir ambos parámetros:
      song y artist.

11. Si el usuario pide explícitamente guardar una información en memoria,
    utiliza memory + save.

12. Si el usuario pide explícitamente guardar algo en favoritos,
    utiliza favorites + save.

13. Si el usuario pregunta por una información que debe recuperarse
    de la memoria, utiliza memory + get.

14. Si el usuario pregunta qué información hay guardada en memoria,
    utiliza memory + list.

15. Si el usuario pide eliminar una información de la memoria,
    utiliza memory + delete.

16. Si el usuario solicita consultar un favorito concreto,
    utiliza favorites + get.

17. Si el usuario solicita listar sus favoritos,
    utiliza favorites + list.

18. La memoria puede utilizarse automáticamente para conservar información
    personal, preferencias, intereses o datos relevantes que puedan ser
    útiles en futuras conversaciones.

    Si el usuario solicita explícitamente guardar una información en memoria,
    DEBES utilizar memory + save.

    Si el usuario no solicita explícitamente guardar la información,
    PUEDES utilizar memory + save cuando consideres que esa información
    es relevante y útil para futuras conversaciones.

    Los favoritos NUNCA deben guardarse automáticamente.
    Solo utiliza favorites + save cuando el usuario solicite explícitamente
    guardar algo en favoritos.

18.5. La memoria y los favoritos tienen comportamientos diferentes:

    - memory:
      Puede utilizarse de forma explícita o automática.

    - favorites:
      Solo puede utilizarse cuando el usuario lo solicite explícitamente.

19. Considera especialmente relevante para la memoria:

    - gustos y preferencias del usuario.
    - hobbies e intereses.
    - actividades que practica habitualmente.
    - comidas o tipos de comida que le gustan.
    - juegos, películas, música, libros o actividades que le interesan.
    - proyectos personales.
    - preferencias relacionadas con tecnología, compras o entretenimiento.
    - información sobre sus objetivos o planes a largo plazo.

20. "memory" y "favorites" son sistemas independientes.

21. Si el usuario utiliza expresiones como "guárdalo en favoritos",
    "añádelo a favoritos", "quiero guardarlo como favorito" o equivalentes,
    utiliza favorites + save.

22. Si el usuario utiliza expresiones como "guárdalo en memoria",
    "recuerda esto", "acuérdate de esto" o equivalentes,
    utiliza memory + save.

23. Si el usuario pide explícitamente guardar algo en favoritos,
    no utilices memory + save para esa petición.

24. Si el usuario utiliza "guárdalo" sin especificar si se refiere
    a memoria o favoritos, utiliza memory + save.

25. Para memory + save, los parámetros deben ser:
    "type", "key" y "value".

26. Para favorites + save, los parámetros deben ser:
    "category", "summary" y "prompt".

27. Nunca utilices los parámetros "type", "key" o "value"
    para una petición favorites + save.

28. Nunca utilices los parámetros "category", "summary" o "prompt"
    para una petición memory + save.
29. Para consultas astronómicas utiliza intent "astronomy".

30. Para consultar la posición de un objeto astronómico utiliza:
    intent = "astronomy"
    action = "object"

31. Los objetos astronómicos deben utilizar nombres simples y normalizados
    como:
    - sun
    - moon
    - mercury
    - venus
    - mars
    - jupiter
    - saturn
    - uranus
    - neptune

32. Para astronomy + object, los parámetros disponibles son:
    - object
    - location
    - date
    - time

33. Si el usuario no especifica una ubicación, utiliza:
    "location": null

34. Si el usuario no especifica una fecha pero hace referencia al momento actual,
    utiliza:
    "date": "today"

35. Si el usuario utiliza "ahora" o "en este momento", utiliza:
    "time": "now"

36. Si el usuario utiliza una expresión temporal relativa,
    conserva dicha expresión para que Cronos la resuelva.

    Ejemplos:
    "dentro de 2 horas" → "in_2_hours"
    "hace 2 horas" → "2_hours_ago"

37. Zeus NO debe calcular ni resolver fechas u horas.
    Debe conservar las expresiones temporales semánticas para que
    Cronos las convierta posteriormente en una fecha y hora concretas.

38. Zeus NO debe calcular la posición de los objetos astronómicos.
    Su única función es identificar el objeto, ubicación, fecha y hora
    solicitados.


Historial de la conversación:

{history_text if history_text else "(No hay historial previo.)"}

Historial de peticiones:

{request_history_text if request_history_text else "(No hay peticiones anteriores.)"}

IMPORTANTE SOBRE EL HISTORIAL:

- El historial pertenece a la misma conversación.
- Puedes utilizarlo para resolver referencias ambiguas.
- Si el usuario omite información que ya fue indicada anteriormente,
  recupera esa información del historial.
- No inventes información que no aparezca ni en la petición actual
  ni en el historial.

Ejemplo:

Historial de peticiones:

[request_id=28] Usuario: ¿Qué tiempo hará mañana en Valdemoro?

Petición actual:

¿Y hoy?

Interpretación correcta:

{{
    "intent": "weather",
    "action": "current",
    "parameters": {{
        "location": "Valdemoro",
        "date": "today"
    }},
    "context": {{
        "used": true,
        "request_id": 28
    }},
    "requests": []
}}

IMPORTANTE SOBRE EL CONTEXTO ENTRE PETICIONES:

El historial de peticiones contiene el request_id de cada petición anterior.

Si la petición actual depende de información de una petición anterior,
debes indicarlo dentro de "context".

Si utilizas una petición anterior como contexto, utiliza:

"context": {{
    "used": true,
    "request_id": ID_DE_LA_PETICION
}}

Si la petición actual NO depende de ninguna petición anterior, utiliza:

"context": {{
    "used": false,
    "request_id": null
}}

Solo debes utilizar contexto cuando sea realmente necesario
para interpretar la petición actual.

No utilices "context" para almacenar otras peticiones.
Para varias peticiones independientes utiliza "requests".

Petición del usuario:
{text}
"""

        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "think": False,
                "stream": False,
                "options": {"num_predict": 500},
            },
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

        request = AgentRequest(
            intent=parsed["intent"],
            action=parsed["action"],
            parameters=parsed.get("parameters", {}),
            context=parsed.get("context", {}),
            requests=parsed.get("requests", []),
        )

        return InterpretationResult(
            request=request,
            raw_json=parsed,
            model=self.model,
            total_duration=data.get("total_duration", 0),
            load_duration=data.get("load_duration", 0),
            prompt_eval_duration=data.get("prompt_eval_duration", 0),
            eval_duration=data.get("eval_duration", 0),
            eval_count=data.get("eval_count", 0),
        )

    def generate_response(
        self,
        text: str,
        request: AgentRequest,
        results: list[AgentResult],
        history: list[dict],
    ) -> str:

        history_text = ""

        for message in history:
            role = "Usuario" if message["role"] == "user" else "Zeus"

            history_text += f"{role}: {message['content']}\n"

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
- Sé conciso y directo.
- No añadas explicaciones que el usuario no haya pedido.
- Para noticias, muestra únicamente el titular, la fuente y la URL.
- No resumas ni expliques las noticias salvo que el usuario lo solicite.
- Para peticiones sencillas, responde brevemente.
- Si hay varias peticiones, responde a todas sin extenderte innecesariamente.

Historial de la conversación:

El siguiente texto contiene mensajes anteriores de esta misma sesión.
Utilízalo para mantener la continuidad de la conversación y recordar
información que el usuario ya haya proporcionado.

{history_text}

Petición original del usuario:

{text}

Interpretación de Zeus:

Intent: {request.intent}
Action: {request.action}

Parameters:
{json.dumps(request.parameters, ensure_ascii=False, indent=2)}

Context:
{json.dumps(request.context, ensure_ascii=False, indent=2)}

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
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "think": False,
                "options": {"num_predict": 500},
            },
        )

        response.raise_for_status()

        data = response.json()

        print("Tiempo total respuesta:", data.get("total_duration", 0) / 1_000_000_000)

        print("Carga modelo respuesta:", data.get("load_duration", 0) / 1_000_000_000)

        print(
            "Evaluación prompt respuesta:",
            data.get("prompt_eval_duration", 0) / 1_000_000_000,
        )

        print("Generación respuesta:", data.get("eval_duration", 0) / 1_000_000_000)

        print("Tokens generados respuesta:", data.get("eval_count", 0))

        return data["message"]["content"].strip()
