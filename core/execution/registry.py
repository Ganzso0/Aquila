from agents.base_agent import BaseAgent


class Registry:
    """
    Registro de agentes de Lacerta.

    Se encarga de almacenar, registrar y recuperar
    los agentes disponibles en el sistema.
    """

    def __init__(self):
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        """
        Registra un nuevo agente.
        """

        if agent.id in self._agents:
            raise ValueError(f"El agente '{agent.id}' ya está registrado.")

        self._agents[agent.id] = agent

    def unregister(self, agent_id: str) -> None:
        """
        Elimina un agente del registro.
        """

        self._agents.pop(agent_id, None)

    def get(self, agent_id: str) -> BaseAgent | None:
        """
        Devuelve un agente por su ID.
        """

        return self._agents.get(agent_id)

    def get_all(self) -> list[BaseAgent]:
        """
        Devuelve todos los agentes registrados.
        """

        return list(self._agents.values())

    def __len__(self) -> int:
        """
        Devuelve el número de agentes registrados.
        """

        return len(self._agents)

    def __repr__(self) -> str:
        return f"<Registry(agents={len(self)})>"