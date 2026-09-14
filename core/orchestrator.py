from core.registry import Registry
from core.request import AgentRequest
from core.result_processor import ResultProcessor
from services.ai_service import AIService
from core.result import AgentResult
from concurrent.futures import ThreadPoolExecutor
from services.cronos_service import CronosService
from services.memory_manager import MemoryManager
from services.Aegis import AegisService


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
    ):

        self._registry = registry
        self._result_processor = result_processor
        self._ai_service = ai_service
        self._memory_service = memory_service
        self._memory_manager = memory_manager
        self._cronos_service = cronos_service
        self._aegis_service = aegis_service
        self._session_id = session_id

    def handle(self, text: str) -> str:

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

    # =====================================
    # Guardar petición del usuario
    # =====================================

        self._memory_service.save_message(
            self._session_id,
            "user",
            text
        )

    # =====================================
    # Interpretar petición
    # =====================================

        internal_mode = "lacerta" in text.lower()

        interpretation = self._ai_service.interpret(
            text,
            history_for_interpretation,
            request_history,
            internal_mode=internal_mode
)

        context_request_id = None

        context = interpretation.raw_json.get("context", {})

        if context.get("used"):
            context_request_id = context.get("request_id")

        request_id = self._memory_service.save_request(
            self._session_id,
            text,
            context_request_id
        )

        self._memory_service.save_interpretation(
            request_id,
            interpretation
        )

        request = interpretation.request


        print("\n--- AGENT REQUEST ---")

        print("Intent:", request.intent)
        print("Action:", request.action)
        print("Parameters:", request.parameters)
        print("Context:", request.context)

        if request.requests:
            print("Peticiones múltiples:")

            for i, sub_request in enumerate(request.requests, 1):
                print(f"  [{i}]")
                print("    Intent:", sub_request.get("intent"))
                print("    Action:", sub_request.get("action"))
                print("    Parameters:", sub_request.get("parameters", {}))

        print("--- END REQUEST ---\n")

        # =====================================
        # Determinar peticiones
        # =====================================

        requests_to_execute = []

        if request.requests:
            for sub_request in request.requests:
                requests_to_execute.append(
                    AgentRequest(
                        intent=sub_request.get("intent"),
                        action=sub_request.get("action"),
                        parameters=sub_request.get("parameters", {}),
                        context=sub_request.get("context", {}),
                    )
                )

        else:
            requests_to_execute.append(request)

        # =====================================
        # Resolver referencias temporales
        # =====================================

        requests_to_execute = [
            self._cronos_service.resolve(req)
            for req in requests_to_execute
        ]   

        # =====================================
        # Ejecutar agentes
        # =====================================

        results = []

        with ThreadPoolExecutor(
            max_workers=min(len(requests_to_execute),5)
        ) as executor:

            futures = [
            executor.submit(
            self._execute_request,
            sub_request
        )
        for sub_request in requests_to_execute
    ]

        for future in futures:
            result = future.result()

            print("DEBUG RESULT:")
            print("Success:", result.success if result else None)
            print("Message:", result.message if result else None)
            print("Data:", result.data if result else None)

            if result is not None:
                results.append(result)
        history = self._memory_service.get_messages(self._session_id)[-20:]

        # =====================================
        # Conversación
        # =====================================

        if not results and any(r.intent == "conversation" for r in requests_to_execute):
            response = self._ai_service.generate_response(text, request, [], history)

            self._memory_service.save_message(self._session_id, "assistant", response)

            return response

        # =====================================
        # Procesar resultados
        # =====================================

        response = self._result_processor.process(text, request, results, history)

        self._memory_service.save_message(self._session_id, "assistant", response)

        return response

    def _execute_request(self, request: AgentRequest) -> AgentResult | None:

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
                print(f"Ejecutando agente: {agent.name}")

                return self._aegis_service.execute_agent(
                    agent,
                    request
    )

        print(
            "No se encontró agente para:",
            request.intent,
            request.action
        )

        return None

    def __repr__(self) -> str:
        return f"<Orchestrator(agents={len(self._registry)})>"
