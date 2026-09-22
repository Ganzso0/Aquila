from core.execution.registry import Registry
from core.models.request import AgentRequest
from core.execution.result_processor import ResultProcessor
from core.ai.ai_service import AIService
from core.models.result import AgentResult
from concurrent.futures import ThreadPoolExecutor
from services.internal.Cronos.cronos_service import CronosService
from services.internal.memory.memory_manager import MemoryManager
from supervision.Aegis.Aegis import AegisService
from core.execution.interpretationvalidator import InterpretationValidator
from cognition.Hecate.hecate import HecateService
from services.internal.condition_evaluator import ConditionEvaluator
from services.internal.plan_validator import PlanValidator
from services.internal.execution_trace import ExecutionTrace


class Orchestrator:
    """
    Orquestador principal de Lacerta.

    Su responsabilidad es interpretar y coordinar
    las peticiones entre Zeus y los agentes.
    """

    def __init__(
        self,
        registry: Registry,
        result_processor: ResultProcessor,
        ai_service: AIService,
        memory_service,
        memory_manager: MemoryManager,
        cronos_service: CronosService,
        aegis_service: AegisService,
        session_id: int,
        interpretation_validator: InterpretationValidator,
        hecate_service: HecateService,
        condition_evaluator: ConditionEvaluator,
        plan_validator: PlanValidator
        

    ):

        self._registry = registry
        self._result_processor = result_processor
        self._ai_service = ai_service
        self._memory_service = memory_service
        self._memory_manager = memory_manager
        self._cronos_service = cronos_service
        self._aegis_service = aegis_service
        self._session_id = session_id
        self._interpretation_validator = interpretation_validator
        self._hecate_service = hecate_service
        self._condition_evaluator = condition_evaluator
        self._plan_validator = plan_validator
        

    def handle(self, text: str) -> str:

        trace = ExecutionTrace()

        trace.add(
                "request_received",
                text=text
            )

        # =====================================
        # Recuperar historial anterior
        # =====================================

        history_for_interpretation = (
            self._memory_service
            .get_messages(self._session_id)[-20:]
        )

        request_history = (
            self._memory_service
            .get_request_history(self._session_id)[-20:]
        )

        trace.add(
    "history_loaded",
    messages=len(history_for_interpretation),
    requests=len(request_history)
)

        # =====================================
        # Guardar petición del usuario
        # =====================================

        self._memory_service.save_message(
            self._session_id,
            "user",
            text
        )


        trace.add("message_saved")

        # =====================================
        # Interpretar petición
        # =====================================

        internal_mode = "lacerta" in text.lower()

        trace.add(
        "interpretation_started"
        )

        interpretation = self._ai_service.interpret(
            text,
            history_for_interpretation,
            request_history,
            internal_mode=internal_mode
        )

        trace.add(
        "interpretation_completed",
        planning_required=interpretation.planning_required,
        requests=len(interpretation.requests)
        )

        # =====================================
        # Validar interpretación
        # =====================================

        trace.add(
        "interpretation_validation_started"
        )

        if not self._interpretation_validator.validate(
            interpretation,
            text
        ):
            return "No he entendido bien la petición."

        trace.add(
            "interpretation_validated"
        )

        # =====================================
        # Determinar contexto de la petición
        # =====================================

        context_request_id = None

        for parsed_request in interpretation.requests:

            if parsed_request.context.get("used"):

                context_request_id = (
                    parsed_request.context.get("request_id")
                )

                break

        # =====================================
        # Guardar petición
        # =====================================

        request_id = self._memory_service.save_request(
            self._session_id,
            text,
            context_request_id
        )
        trace.add(
    "request_saved",
    request_id=request_id
)

        interpretation_id = self._memory_service.save_interpretation(
            request_id,
            interpretation
        )

        trace.add(
    "interpretation_saved",
    interpretation_id=interpretation_id
)

        # =====================================
        # Mostrar interpretación
        # =====================================

        print("\n--- INTERPRETACIÓN ---")

        print(
            "Conversation:",
            interpretation.conversation
        )

        print(
            "Planning required:",
            interpretation.planning_required
        )

        print(
            "Número de peticiones:",
            len(interpretation.requests)
        )

        for i, request in enumerate(
            interpretation.requests,
            1
        ):

            print(f"\n  [{i}]")

            print(
                "    Intent:",
                request.intent
            )

            print(
                "    Action:",
                request.action
            )

            print(
                "    Parameters:",
                request.parameters
            )

            print(
                "    Context:",
                request.context
            )

        print("\n--- END INTERPRETACIÓN ---\n")

        # =====================================
        # Determinar peticiones a ejecutar
        # =====================================

        requests_to_execute = list(
            interpretation.requests
        )

        # =====================================
        # Resolver referencias temporales
        # =====================================

        trace.add(
    "temporal_resolution_started",
    requests=len(requests_to_execute)
)

        requests_to_execute = [
            self._cronos_service.resolve(request)
            for request in requests_to_execute
        ]

        trace.add(
    "temporal_resolution_completed",
    requests=len(requests_to_execute)
)

        # =====================================
        # Ejecutar peticiones
        # =====================================

        trace.add(
    "execution_started",
    planning_required=interpretation.planning_required
)
        trace.add(
    "execution_requests_prepared",
    requests=len(requests_to_execute)
)

        if interpretation.planning_required:

            trace.add(
                "planning_started",
                requests=len(requests_to_execute)
            )

            plan = self._hecate_service.plan(
                text,
                [
                    {
                        "intent": request.intent,
                        "action": request.action,
                        "parameters": request.parameters,
                        "context": request.context
                    }
                    for request in requests_to_execute
                ]
            )

            trace.add(
                "planning_completed",
                tasks=len(plan.get("tasks", []))
            )

            print("\n--- PLAN DE HÉCATE ---")
            print(plan)
            print("--- END PLAN ---\n")

            results = self._execute_plan(
                plan,
                trace
            )

        else:

            trace.add(
        "parallel_execution_started",
        requests=len(requests_to_execute)
    )

            # Peticiones independientes → ejecución paralela
            results = self._execute_requests_parallel(
                requests_to_execute,
                trace
            )

            trace.add(
        "parallel_execution_completed",
        results=len(results)
    )

        history = (
            self._memory_service
            .get_messages(self._session_id)[-20:]
        )

        # =====================================
        # Conversación
        # =====================================

        trace.add(
    "execution_completed",
    results=len(results)
)

        if (
            not results
            and interpretation.conversation
        ):

            response = self._ai_service.generate_response(
                text,
                interpretation,
                [],
                history
            )

            self._memory_service.save_dataset_label(
                interpretation_id,
                [],
                response
            )

            self._memory_service.save_message(
                self._session_id,
                "assistant",
                response
            )

            return response

        # =====================================
        # Procesar resultados
        # =====================================

        # Compatibilidad temporal:
        # ResultProcessor todavía trabaja con
        # una AgentRequest individual.

        trace.add(
            "response_generation_started",
            results=len(results)
        )

        response = self._result_processor.process(
            text,
            interpretation,
            results,
            history
        )

        trace.add(
            "response_generation_completed"
        )

        # =====================================
        # Preparar datos para dataset
        # =====================================

        dataset_data = []

        for result in results:

            if not result.success:
                continue

            dataset_data.append({
                "agent": result.agent_name,
                "type": result.type,
                "message": result.message,
                "data": result.data
            })

        # =====================================
        # Guardar dataset label
        # =====================================

        self._memory_service.save_dataset_label(
            interpretation_id,
            dataset_data,
            response
        )

        trace.add(
            "dataset_label_saved",
            interpretation_id=interpretation_id
        )

        # =====================================
        # Guardar respuesta
        # =====================================

        self._memory_service.save_message(
            self._session_id,
            "assistant",
            response
        )

        trace.add("response_saved")

        trace.add(
    "execution_finished",
    results=len(results)
)

        print("\n=== EXECUTION TRACE ===")

        for event in trace.get_events():
            print(event)

        print("=== END EXECUTION TRACE ===\n")

        return response

    def _debug_result(
        self,
        result: AgentResult | None
    ):

        print("DEBUG RESULT:")

        print(
            "Success:",
            result.success if result else None
        )

        print(
            "Message:",
            result.message if result else None
        )

        print(
            "Data:",
            result.data if result else None
        )

    def _execute_plan(
        self,
        plan: dict,
        trace: ExecutionTrace
        ) -> list[AgentResult]:

        # =====================================
        # Validar plan
        # =====================================

        self._plan_validator.validate(plan)

        trace.add(
    "plan_validation_completed",
    tasks=len(plan["tasks"])
)

        print("\nPLAN DE HÉCATE VÁLIDO")

        results = []

        # Resultados asociados a cada tarea
        task_results = {}

        for task in plan["tasks"]:

            task_id = task["id"]

            trace.add(
                "task_started",
                task_id=task_id,
                intent=task["intent"],
                action=task["action"]
            )

            print(
                f"\nEjecutando tarea planificada: "
                f"{task_id}"
            )

            # =====================================
            # Evaluar condición
            # =====================================

            condition = task.get("condition")

            if condition:

                value = self._resolve_condition_source(
                    condition["source"],
                    task_results
                )

                print(
                    "Condition value:",
                    value
                )

                condition_result = (
                    self._condition_evaluator.evaluate(
                        value=value,
                        operator=condition["operator"],
                        expected=condition["value"]
                    )
                )
                trace.add(
                    "condition_evaluated",
                    task_id=task_id,
                    source=condition["source"],
                    operator=condition["operator"],
                    expected=condition["value"],
                    actual=value,
                    result=condition_result
                )

                print(
                    "Condition result:",
                    condition_result
                )

                if not condition_result:

                    trace.add(
                        "task_skipped",
                        task_id=task_id,
                        reason="condition_not_met"
                    )

                    print(
                        f"Tarea {task_id} omitida "
                        f"porque la condición no se cumple."
                    )

                    continue

            # =====================================
            # Crear request
            # =====================================

            request = AgentRequest(
                intent=task["intent"],
                action=task["action"],
                parameters=task.get("inputs", {}),
                context={}
            )

            # =====================================
            # Ejecutar
            # =====================================

            result = self._execute_request(request,trace)

            self._debug_result(result)

            if result is not None:

                results.append(result)

                task_results[task_id] = result
                trace.add(
                    "task_completed",
                    task_id=task_id,
                    success=result.success,
                    agent=result.agent_name
                )

        return results

    def _resolve_condition_source(
        self,
        source: str,
        task_results: dict
    ):
        parts = source.split(".")

        task_id = parts[0]

        if task_id not in task_results:
            raise ValueError(
                f"No existe resultado para la tarea: {task_id}"
            )

        result = task_results[task_id]

        value = result.data

        for part in parts[1:]:

            if not isinstance(value, dict):
                raise ValueError(
                    f"No se puede acceder a '{part}' "
                    f"en la fuente '{source}'"
                )

            if part not in value:
                raise ValueError(
                    f"No existe el campo '{part}' "
                    f"en la fuente '{source}'"
                )

            value = value[part]

        return value

    def _execute_requests_parallel(
        self,
        requests: list[AgentRequest],
        trace: ExecutionTrace
    ) -> list[AgentResult]:

        results = []

        if not requests:
            return results

        with ThreadPoolExecutor(
            max_workers=min(len(requests), 5)
        ) as executor:

            futures = [
                executor.submit(
                    self._execute_request,
                    request,
                    trace
                )
                for request in requests
            ]

            for future in futures:

                result = future.result()

                self._debug_result(result)

                if result is not None:
                    results.append(result)

        return results

    def _execute_request(
        self,
        request: AgentRequest,
        trace: ExecutionTrace
    ) -> AgentResult | None:

        trace.add(
            "request_started",
            intent=request.intent,
            action=request.action,
            parameters=request.parameters
        )

    # conversation no necesita agente
        if request.intent == "conversation":
            print("Conversación detectada. Zeus responderá directamente.")

            return None

    # memory y favorites son gestionados por MemoryManager
        if request.intent in ["memory", "favorites"]:
            print("Ejecutando MemoryManager")

            return self._memory_manager.execute(request)

    # control interno del proyecto

        if request.intent == "lacerta":
                print("Ejecutando Aegis")

                if request.action == "agent_status":

                    agent_id = request.parameters.get("agent")

                    status = self._aegis_service.get_agent_status(agent_id)

                    if status is None:
                        return AgentResult(
                            success=False,
                            agent_name="Aegis",
                            type="error",
                            message=f"No se encontró el agente: {agent_id}"
                        )

                    return AgentResult(
                        success=True,
                        agent_name="Aegis",
                        type="agent_status",
                        message="Estado de los agentes obtenido correctamente.",
                        data=status
                    )

                if request.action == "enable_agent":

                    agent_id = request.parameters.get("agent")

                    success = self._aegis_service.enable_agent(agent_id)

                    return AgentResult(
                        success=success,
                        agent_name="Aegis",
                        type="agent_control",
                        message=(
                            f"Agente {agent_id} activado."
                            if success
                            else f"No se encontró el agente: {agent_id}"
                        )
                    )

                if request.action == "disable_agent":

                    agent_id = request.parameters.get("agent")

                    success = self._aegis_service.disable_agent(agent_id)

                    return AgentResult(
                        success=success,
                        agent_name="Aegis",
                        type="agent_control",
                        message=(
                            f"Agente {agent_id} desactivado."
                            if success
                            else f"No se encontró el agente: {agent_id}"
                        )
                    )

                return AgentResult(
                    success=False,
                    agent_name="Aegis",
                    type="error",
                    message=f"Acción de Lacerta no reconocida: {request.action}"
                )

    # El resto de peticiones se buscan en los agentes
        for agent in self._registry.get_all():

            if not agent.enabled:
                continue

            if agent.can_handle(request):

                trace.add(
                    "agent_started",
                    agent=agent.name,
                    intent=request.intent,
                    action=request.action
                )

                result = self._aegis_service.execute_agent(
                    agent,
                    request
                )

                trace.add(
                    "agent_completed",
                    agent=agent.name,
                    success=result.success if result else None
                )

                trace.add(
                    "request_completed",
                    intent=request.intent,
                    action=request.action,
                    success=result.success if result else None
                )

                return result

        print(
            "No se encontró agente para:",
            request.intent,
            request.action
        )

        return None


    def __repr__(self) -> str:
        return f"<Orchestrator(agents={len(self._registry)})>"
