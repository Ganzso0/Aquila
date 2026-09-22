class InterpretationResult:

    def __init__(
        self,
        requests,
        raw_json,
        model,
        total_duration,
        load_duration,
        prompt_eval_duration,
        eval_duration,
        eval_count,
        conversation=False,
        planning_required=False,
    ):
        # Peticiones individuales detectadas por Nous
        self.requests = requests

        # Respuesta estructurada original de Qwen
        self.raw_json = raw_json

        # Propiedades globales de la interpretación
        self.conversation = conversation
        self.planning_required = planning_required

        # Información del modelo
        self.model = model

        # Métricas de procesamiento
        self.total_duration = total_duration
        self.load_duration = load_duration
        self.prompt_eval_duration = prompt_eval_duration
        self.eval_duration = eval_duration
        self.eval_count = eval_count

    def __repr__(self) -> str:
        return (
            f"<InterpretationResult("
            f"model={self.model}, "
            f"requests={len(self.requests)}, "
            f"conversation={self.conversation}, "
            f"planning_required={self.planning_required}, "
            f"tokens={self.eval_count}"
            f")>"
        )

