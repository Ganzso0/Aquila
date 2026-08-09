from core.registry import Registry
from core.request import AgentRequest
from core.result_processor import ResultProcessor
from services.ai_service import AIService


class Orchestrator:
    """
    Orquestador principal de Lacerta.

    Su responsabilidad es interpretar y coordinar
    las peticiones entre Zeus y los agentes.
    """

    def __init__(
        self,
        registry: Registry,
        result_processor: ResultProcessor,
        ai_service: AIService
    ):

        self._registry = registry
        self._result_processor = result_processor
        self._ai_service = ai_service

    def handle(self, text: str) -> str:

        request = self._ai_service.interpret(text)

        print("\n--- AGENT REQUEST ---")

        print("Intent:", request.intent)
        print("Action:", request.action)
        print("Parameters:", request.parameters)
        print("Context:", request.context)

        if request.requests:

            print("Peticiones múltiples:")

            for i, sub_request in enumerate(
                request.requests,
                1
            ):

                print(f"  [{i}]")
                print(
                    "    Intent:",
                    sub_request.get("intent")
                )
                print(
                    "    Action:",
                    sub_request.get("action")
                )
                print(
                    "    Parameters:",
                    sub_request.get(
                        "parameters",
                        {}
                    )
                )

        print("--- END REQUEST ---\n")

        # =====================================
        # Determinar peticiones
        # =====================================

        requests_to_execute = []

        if request.requests:

            for sub_request in request.requests:

                requests_to_execute.append(
                    AgentRequest(
                        intent=sub_request.get("intent"),
                        action=sub_request.get("action"),
                        parameters=sub_request.get(
                            "parameters",
                            {}
                        ),
                        context=sub_request.get(
                            "context",
                            {}
                        )
                    )
                )

        else:

            requests_to_execute.append(request)

        # =====================================
        # Ejecutar agentes
        # =====================================

        results = []

        for sub_request in requests_to_execute:

            # conversation no necesita agente
            if sub_request.intent == "conversation":

                print(
                    "Conversación detectada. "
                    "Zeus responderá directamente."
                )

                continue

            handled = False

            for agent in self._registry.get_all():

                if not agent.enabled:
                    continue

                if agent.can_handle(sub_request):

                    print(
                        f"Ejecutando agente: {agent.name}"
                    )

                    result = agent.execute(
                        sub_request
                    )

                    results.append(result)

                    handled = True

                    break

            if not handled:

                print(
                    "No se encontró agente para:",
                    sub_request.intent,
                    sub_request.action
                )

        # =====================================
        # Conversación
        # =====================================

        if (
            not results
            and any(
                r.intent == "conversation"
                for r in requests_to_execute
            )
        ):

            return self._ai_service.generate_response(
                text,
                request,
                []
            )

        # =====================================
        # Procesar resultados
        # =====================================

        return self._result_processor.process(
            text,
            request,
            results
        )

    def __repr__(self) -> str:
        return (
            f"<Orchestrator(agents={len(self._registry)})>"
        )