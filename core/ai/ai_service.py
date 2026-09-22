import json
import requests
from core.models.result import AgentResult
from core.models.request import AgentRequest
from core.models.interpretation_result import InterpretationResult
from pathlib import Path
from core.models.interpretation_result import InterpretationResult


class AIService:

    def __init__(self, model: str = "granite4:3b"):

        self.model = model
        self.url = "http://localhost:11434/api/chat"
        prompt_path = Path(__file__).parent / "prompt.txt"
        
        with open(prompt_path, "r", encoding="utf-8") as f:
                    self.prompt = f.read()

    def interpret(
    self,
    text: str,
    history: list[dict] | None = None,
    request_history: list[dict] | None = None,
    internal_mode: bool = False
    ) -> InterpretationResult:

        
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

        internal_mode_text = ""

        if internal_mode:
            internal_mode_text = """
            MODO INTERNO LACERTA: ACTIVADO

            La petición pertenece al control interno de Lacerta.

            Debes utilizar obligatoriamente:
            "intent": "lacerta"

            Interpreta la solicitud utilizando únicamente las acciones disponibles
            para el intent "lacerta".

            NO utilices "memory", "conversation", "system" ni ningún otro intent.

            "LACERTA" es únicamente el activador del modo interno y no forma
            parte de la petición que debes interpretar.
            """

        prompt = f"""
            {self.prompt}

            Historial de la conversación:
        ```

        {history_text if history_text else "(No hay historial previo.)"}

        Historial de peticiones:

        {request_history_text if request_history_text else "(No hay peticiones anteriores.)"}

        IMPORTANTE SOBRE EL HISTORIAL:

        * El historial pertenece a la misma conversación.
        * Puedes utilizarlo para resolver referencias ambiguas.
        * Si el usuario omite información que ya fue indicada anteriormente,
        recupera esa información del historial.
        * No inventes información que no aparezca ni en la petición actual
        ni en el historial.

        {internal_mode_text}

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

        print(
            "Tiempo total:",
            data.get("total_duration", 0) / 1_000_000_000
        )
        print(
            "Carga modelo:",
            data.get("load_duration", 0) / 1_000_000_000
        )
        print(
            "Evaluación prompt:",
            data.get("prompt_eval_duration", 0) / 1_000_000_000
        )
        print(
            "Generación:",
            data.get("eval_duration", 0) / 1_000_000_000
        )
        print(
            "Tokens generados:",
            data.get("eval_count", 0)
        )

        content = data["message"]["content"].strip()

        if content.startswith("```json"):
            content = content[7:]

        elif content.startswith("```"):
            content = content[3:]

        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()

        if content.startswith("{{") and content.endswith("}}"):
            content = content[1:-1].strip()

        print("\n--- RAW QWEN RESPONSE ---")
        print(content)
        print("--- END RAW RESPONSE ---\n")

        parsed = json.loads(content)

        conversation = parsed.get("conversation", False)
        planning_required = parsed.get("planning_required", False)

        print("=== INTERPRETACIÓN QWEN ===")
        print("Conversation:", repr(conversation))
        print("Planning required:", repr(planning_required))
        print("Requests:", len(parsed.get("requests", [])))
        print("===========================")

        # --------------------------------------------------
        # Convertir cada request del JSON en un AgentRequest
        # --------------------------------------------------

        parsed_request = []

        for request_data in parsed.get("requests", []):

            request = AgentRequest(
                intent=request_data.get("intent"),
                action=request_data.get("action"),
                parameters=request_data.get("parameters", {}),
                context=request_data.get("context", {}),
            )

            parsed_request.append(request)

        return InterpretationResult(
            requests=parsed_request,
            raw_json=parsed,
            model=self.model,
            total_duration=data.get("total_duration", 0),
            load_duration=data.get("load_duration", 0),
            prompt_eval_duration=data.get("prompt_eval_duration", 0),
            eval_duration=data.get("eval_duration", 0),
            eval_count=data.get("eval_count", 0),
            conversation=conversation,
            planning_required=planning_required,
        )

    def generate_response(
    self,
    text: str,
    interpretation: InterpretationResult,
    results: list[AgentResult],
    history: list[dict],
) -> str:

        history_text = ""

        for message in history:
            role = "Usuario" if message["role"] == "user" else "Logos"

            history_text += (
                f"{role}: {message['content']}\n"
            )

        # =====================================
        # Interpretación completa
        # =====================================

        requests_text = ""

        for i, request in enumerate(
            interpretation.requests,
            1
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
        indent=2
    )}

    Context:
    {json.dumps(
        request.context,
        ensure_ascii=False,
        indent=2
    )}
    """

        # =====================================
        # Resultados
        # =====================================

        results_text = ""

        for result in results:

            results_text += f"""
    Agente: {result.agent_name}
    Tipo: {result.type}
    Mensaje: {result.message}
    Datos: {json.dumps(result.data, ensure_ascii=False)}
    """

        prompt = f"""
    Eres Logos, el componente conversacional de Lacerta.

    Tu función es convertir los resultados obtenidos
    por los agentes en una respuesta natural para el usuario.

    Los agentes ya han ejecutado las acciones.
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

    Interpretación de Nous:

    Conversation:
    {interpretation.conversation}

    Planning required:
    {interpretation.planning_required}

    Requests:

    {requests_text}

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
                    "num_predict": 500
                },
            },
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