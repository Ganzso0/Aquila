
from core.registry import Registry
from core.result import AgentResult


class AegisService:
    """
    Servicio de supervisión y seguridad interna de Lacerta.

    Aegis supervisa el estado del sistema, protege las ejecuciones
    y gestiona el ciclo de vida de los agentes.
    """

    MAX_CONSECUTIVE_FAILURES = 3

    def __init__(self, registry: Registry):
        self._registry = registry
        self._agent_stats = {}

        self._initialize_agent_stats()

    def _initialize_agent_stats(self):
        """
        Inicializa las estadísticas de todos los agentes registrados.
        """

        for agent in self._registry.get_all():

            self._agent_stats[agent.id] = {
                "executions": 0,
                "successes": 0,
                "failures": 0,
                "consecutive_failures": 0,
                "last_error": None,
            }

    def __repr__(self):
        return f"<AegisService(agents={len(self._registry)})>"

    def register_success(self, agent_id: str):
        """
        Registra una ejecución exitosa.
        """

        stats = self._agent_stats[agent_id]

        stats["executions"] += 1
        stats["successes"] += 1
        stats["consecutive_failures"] = 0

    def register_failure(self, agent_id: str, error: Exception):
        """
        Registra una ejecución fallida.
        """

        stats = self._agent_stats[agent_id]

        stats["executions"] += 1
        stats["failures"] += 1
        stats["consecutive_failures"] += 1
        stats["last_error"] = str(error)

        if stats["consecutive_failures"] >= self.MAX_CONSECUTIVE_FAILURES:
            self.disable_agent(agent_id)

    def execute_agent(self, agent, request):
        """
        Ejecuta un agente de forma segura y registra el resultado.
        """

        try:
            result = agent.execute(request)

            self.register_success(agent.id)

            return result

        except Exception as error:

            self.register_failure(
                agent.id,
                error
            )

            return AgentResult(
                success=False,
                agent_name=agent.name,
                type="error",
                message=f"El agente {agent.name} ha fallado: {error}"
            )

    def get_agent_status(self, agent_id: str | None = None):
        """
        Devuelve el estado de uno o todos los agentes.

        Si se especifica agent_id, devuelve únicamente ese agente.
        Si no se especifica, devuelve el estado de todos los agentes.
        """

        if agent_id is not None:

            agent = self._registry.get(agent_id)

            if agent is None:
                return None

            return {
                "id": agent.id,
                "name": agent.name,
                "enabled": agent.enabled,
                "stats": self._agent_stats[agent.id],
            }

        return {
            agent.id: {
                "id": agent.id,
                "name": agent.name,
                "enabled": agent.enabled,
                "stats": self._agent_stats[agent.id],
            }
            for agent in self._registry.get_all()
        }

    def enable_agent(self, agent_id: str):
        """
        Activa un agente y reinicia sus fallos consecutivos.
        """

        agent = self._registry.get(agent_id)

        if agent is None:
            return False

        agent.enabled = True
        self._agent_stats[agent_id]["consecutive_failures"] = 0

        return True

    def disable_agent(self, agent_id: str):
        """
        Desactiva un agente.
        """

        agent = self._registry.get(agent_id)

        if agent is None:
            return False

        agent.enabled = False

        return True

