class InterpretationResult:

    def __init__(
        self,
        request,
        raw_json,
        model,
        total_duration,
        load_duration,
        prompt_eval_duration,
        eval_duration,
        eval_count,
    ):
        self.request = request

        # Respuesta estructurada original de Qwen
        self.raw_json = raw_json

        # Información del modelo
        self.model = model

        # Métricas de procesamiento
        self.total_duration = total_duration
        self.load_duration = load_duration
        self.prompt_eval_duration = prompt_eval_duration
        self.eval_duration = eval_duration
        self.eval_count = eval_count

    def __repr__(self):
        return (
            f"<InterpretationResult("
            f"model={self.model}, "
            f"intent={self.request.intent}, "
            f"action={self.request.action}, "
            f"tokens={self.eval_count}"
            f")>"
        )