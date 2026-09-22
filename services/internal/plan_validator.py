class PlanValidator:

    VALID_OPERATORS = {
        "equals",
        "not_equals",
        "greater_than",
        "greater_or_equal",
        "less_than",
        "less_or_equal",
        "contains",
        "not_contains",
        "exists",
        "not_exists",
    }

    def validate(self, plan: dict) -> None:

        if not isinstance(plan, dict):
            raise ValueError(
                "El plan debe ser un diccionario."
            )

        if "tasks" not in plan:
            raise ValueError(
                "El plan no contiene 'tasks'."
            )

        tasks = plan["tasks"]

        if not isinstance(tasks, list):
            raise ValueError(
                "'tasks' debe ser una lista."
            )

        if not tasks:
            raise ValueError(
                "El plan no contiene ninguna tarea."
            )

        task_ids = set()

        # =================================
        # Validar tareas
        # =================================

        for task in tasks:

            if not isinstance(task, dict):
                raise ValueError(
                    "Cada tarea debe ser un objeto."
                )

            required_fields = {
                "id",
                "intent",
                "action",
                "inputs",
                "depends_on",
                "outputs",
            }

            missing = required_fields - task.keys()

            if missing:
                raise ValueError(
                    f"La tarea no contiene los campos: {missing}"
                )

            task_id = task["id"]

            if task_id in task_ids:
                raise ValueError(
                    f"ID de tarea duplicado: {task_id}"
                )

            task_ids.add(task_id)

            depends_on = task["depends_on"]

            if not isinstance(depends_on, list):
                raise ValueError(
                    f"'depends_on' debe ser una lista "
                    f"en {task_id}."
                )

            if task_id in depends_on:
                raise ValueError(
                    f"La tarea {task_id} depende de sí misma."
                )

        # =================================
        # Validar dependencias
        # =================================

        task_positions = {
            task["id"]: index
            for index, task in enumerate(tasks)
        }

        for task in tasks:

            task_id = task["id"]

            for dependency in task["depends_on"]:

                if dependency not in task_ids:
                    raise ValueError(
                        f"La tarea {task_id} depende de "
                        f"una tarea inexistente: {dependency}"
                    )

                if (
                    task_positions[dependency]
                    >= task_positions[task_id]
                ):
                    raise ValueError(
                        f"La dependencia {dependency} debe aparecer "
                        f"antes que {task_id}."
                    )

        # =================================
        # Validar condiciones
        # =================================

        for task in tasks:

            task_id = task["id"]

            condition = task.get("condition")

            if condition is None:
                continue

            if not isinstance(condition, dict):
                raise ValueError(
                    f"'condition' debe ser un objeto "
                    f"en {task_id}."
                )

            required_fields = {
                "source",
                "operator",
                "value",
            }

            missing = required_fields - condition.keys()

            if missing:
                raise ValueError(
                    f"La condición de {task_id} "
                    f"no contiene: {missing}"
                )

            if condition["operator"] not in self.VALID_OPERATORS:
                raise ValueError(
                    f"Operador no válido en {task_id}: "
                    f"{condition['operator']}"
                )

        # =================================
        # Validar input_mapping
        # =================================

        for task in tasks:

            task_id = task["id"]

            input_mapping = task.get("input_mapping")

            if input_mapping is None:
                continue

            if not isinstance(input_mapping, dict):
                raise ValueError(
                    f"'input_mapping' debe ser un objeto "
                    f"en {task_id}."
                )