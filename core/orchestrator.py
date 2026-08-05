from core.registry import Registry
from core.result_processor import ResultProcessor


class Orchestrator:
    """
    Orquestador principal de Lacerta.

    Su única responsabilidad es coordinar los agentes disponibles.
    No contiene lógica específica de ningún agente ni ejecuta tareas
    por sí mismo.
    """

    def __init__(
        self,
        registry: Registry,
        result_processor: ResultProcessor
    ):

        self._registry = registry
        self._result_processor = result_processor


    def handle(self, request: str) -> str:
        """
        Procesa una petición del usuario.
        """

        results = []

        for agent in self._registry.get_all():

            if not agent.enabled:
                continue

            if agent.can_handle(request):

                result = agent.execute(request)
                results.append(result)


        if not results:
            return "No hay ningún agente disponible para procesar esta petición."


        response = results[0].data.get("response")

        return self._result_processor.process(results)


    def __repr__(self) -> str:
        return f"<Orchestrator(agents={len(self._registry)})>"