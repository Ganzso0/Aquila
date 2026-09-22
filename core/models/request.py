class AgentRequest:
    """
    Petición individual estructurada generada por Nous.
    """


    def __init__(
        self,
        intent: str | None = None,
        action: str | None = None,
        parameters: dict | None = None,
        context: dict | None = None,
    ):
        self.intent = intent
        self.action = action
        self.parameters = parameters or {}
        self.context = context or {}

    def __repr__(self) -> str:
        return (
            f"<AgentRequest("
            f"intent={self.intent}, "
            f"action={self.action}"
            f")>"
        )