from core.execution.registry import Registry
from orchestration.Zeus.orchestrator import Orchestrator
from core.execution.loader import load_agents
from core.execution.result_processor import ResultProcessor
# from services.voice_service import VoiceService
from core.ai.ai_service import AIService
from services.internal.memory.memory_service import MemoryService
from services.internal.Cronos.cronos_service import CronosService
from services.internal.memory.memory_manager import MemoryManager
from supervision.Aegis.Aegis import AegisService
from core.execution.interpretationvalidator import InterpretationValidator
from cognition.Hecate.hecate import HecateService
from services.internal.condition_evaluator import ConditionEvaluator
from services.internal.plan_validator import PlanValidator
from services.internal.execution_trace import ExecutionTrace




def main():
    """
    Punto de entrada de Lacerta.
    """

    # Crear el registro de agentes
    registry = Registry()

    load_agents(registry)

    aegis_service = AegisService(registry)

    # Crear servicio de IA
    ai_service = AIService()

    # Crear servicio de hecate
    hecate_service = HecateService()

    condition_evaluator = ConditionEvaluator()
    plan_validator = PlanValidator()
    execution_trace = ExecutionTrace()


    # Crear procesador de resultados
    processor = ResultProcessor(ai_service)

    # Crear servicio de memoria
    memory_service = MemoryService()
    memory_manager = MemoryManager(memory_service)

    # Crear servicio temporal
    cronos_service = CronosService()

    # Crear una nueva sesión
    session_id = memory_service.create_session()

    #interpretator
    interpretation_validator = InterpretationValidator()

    print(f"=== Lacerta iniciado | Sesión {session_id} ===")

    # Crear el orquestador
    zeus = Orchestrator(
        registry,
        processor,
        ai_service,
        memory_service,
        memory_manager,
        cronos_service,
        aegis_service,
        session_id,
        interpretation_validator,
        hecate_service,
        condition_evaluator,
        execution_trace
    )

    # Crear servicio de voz
    # voice = VoiceService()


    print(registry)

    for agent in registry.get_all():
        print(agent)

    while True:

        print("\n¿Cómo quieres introducir la petición?")
        print("[1] Escribir")
        print("[2] Hablar(cerrar)")
        print("[3] Salir")

        mode = input("> ")

        if mode == "1":

            request = input("Tú: ")

        elif mode == "2":

            # request = voice.listen()
            print("cerrando")
            # if not request:
            #     print("No he entendido la petición.")
            #     continue
            break

        elif mode == "3":

            print("Cerrando Lacerta...")
            break

        else:

            print("Opción no válida.")
            continue

        print("> ", request)

        if request.lower() in ["exit", "salir", "terminar"]:
            print("Cerrando Lacerta...")
            break

        # =====================================
        # Zeus procesa la petición
        # =====================================

        response = zeus.handle(request)
        

        # =====================================
        # Mostrar respuesta
        # =====================================

        print("\nZeus:")
        print(response)

        # =====================================
        # Hablar respuesta
        # =====================================

        # voice.speak(response)


if __name__ == "__main__":
    main()