class AgentResult:
    """
    Resultado devuelto por un agente de Lacerta.

    Contiene la información que el agente devuelve
    al orquestador después de procesar una tarea.
    """

    def __init__(
        self,
        success: bool,
        agent_name: str,
        type: str,
        message: str,
        data: dict | None = None,
        requires_llm: bool = False
    ):
        self.success = success
        self.agent_name = agent_name
        self.type = type
        self.message = message
        self.data = data or {}
        self.requires_llm = requires_llm

    def __repr__(self):
        return (
            f"<AgentResult("
            f"agent='{self.agent_name}', "
            f"success={self.success}, "
            f"requires_llm={self.requires_llm}"
            f")>"
        )