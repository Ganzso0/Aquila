class AgentRequest:
    """
    Petición estructurada generada por Zeus.
    """

    def __init__(
        self,
        intent: str | None = None,
        action: str | None = None,
        parameters: dict | None = None,
        context: dict | None = None,
        requests: list | None = None
    ):
        self.intent = intent
        self.action = action
        self.parameters = parameters or {}
        self.context = context or {}
        self.requests = requests or []

    def is_multiple(self) -> bool:
        return len(self.requests) > 0

    def __repr__(self) -> str:
        return (
            f"<AgentRequest("
            f"intent={self.intent}, "
            f"action={self.action}, "
            f"requests={len(self.requests)}"
            f")>"
        )