class ConditionEvaluator:

    def evaluate(
        self,
        value,
        operator: str,
        expected
    ) -> bool:

        if operator in ("equals", "=="):
            return value == expected

        if operator in ("not_equals", "!="):
            return value != expected

        if operator in ("greater_than", ">"):
            return value > expected

        if operator in ("greater_or_equal", ">="):
            return value >= expected

        if operator in ("less_than", "<"):
            return value < expected

        if operator in ("less_or_equal", "<="):
            return value <= expected

        if operator == "contains":
            return expected in value

        if operator == "not_contains":
            return expected not in value

        if operator == "exists":
            return value is not None

        if operator == "not_exists":
            return value is None

        raise ValueError(
            f"Operador no soportado: {operator}"
        )