from core.registry import Registry


class Orchestrator:
    """
    Orquestador principal de Lacerta.

    Su única responsabilidad es coordinar los agentes disponibles.
    No contiene lógica específica de ningún agente ni ejecuta tareas
    por sí mismo.
    """

    def __init__(self, registry: Registry):
        """
        Inicializa el orquestador con un registro de agentes.
        """

        self._registry = registry

    def handle(self, request: str) -> str:
        """
        Procesa una petición del usuario.

        Busca un agente capaz de responderla y delega en él
        la ejecución.
        """

        for agent in self._registry.get_all():

            if not agent.enabled:
                continue

            if agent.can_handle(request):
                return agent.execute(request)

        return "No hay ningún agente disponible para procesar esta petición."

    def __repr__(self) -> str:
        return f"<Orchestrator(agents={len(self._registry)})>"

# 1. Obtener todos los agentes

# 2. Recorrerlos

# 3. Ignorar los deshabilitados

# 4. Preguntar si pueden encargarse

# 5. Si alguno puede

# ejecutar()

# devolver respuesta

# 6. Si nadie puede

#  devolver mensaje de error