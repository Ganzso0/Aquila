from core.registry import Registry
from core.orchestrator import Orchestrator
from agents.loader import load_agents
from core.result_processor import ResultProcessor
# from services.voice_service import VoiceService
from services.ai_service import AIService
from memory.memory_service import MemoryService
from services.cronos_service import CronosService
from services.memory_manager import MemoryManager
from services.Aegis import AegisService





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

    # Crear procesador de resultados
    processor = ResultProcessor(ai_service)

    # Crear servicio de memoria
    memory_service = MemoryService()
    memory_manager = MemoryManager(memory_service)

    # Crear servicio temporal
    cronos_service = CronosService()

    # Crear una nueva sesión
    session_id = memory_service.create_session()

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
        session_id
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