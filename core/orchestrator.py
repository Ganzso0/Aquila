from core.registry import Registry
from core.request import AgentRequest
from core.result_processor import ResultProcessor
from services.ai_service import AIService


class Orchestrator:
    """
    Orquestador principal de Lacerta.

    Su única responsabilidad es interpretar y coordinar
    las peticiones entre los agentes disponibles.
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
        """
        Recibe la petición del usuario, la interpreta mediante
        Zeus/AIService y la convierte en un AgentRequest.
        """

        request: AgentRequest = self._ai_service.interpret(text)
         

        print("\n--- AGENT REQUEST ---")
        print("Intent:", request.intent)
        print("Action:", request.action)
        print("Parameters:", request.parameters)
        print("Context:", request.context)
        print("--- END REQUEST ---\n")

        results = []

        for agent in self._registry.get_all():

            if not agent.enabled:
                continue

            if agent.can_handle(request):

                result = agent.execute(request)
                results.append(result)

        if not results:
            return (
                "No hay ningún agente disponible "
                "para procesar esta petición."
            )



        return self._result_processor.process(
    text,
    request,
    results
)

    def __repr__(self) -> str:
        return f"<Orchestrator(agents={len(self._registry)})>"