from core.registry import Registry
from core.orchestrator import Orchestrator
from agents.loader import load_agents
from core.result_processor import ResultProcessor
from services.voice_service import VoiceService
from services.ai_service import AIService


def main():
    """
    Punto de entrada de Lacerta.
    """

    # Crear el registro de agentes
    registry = Registry()

    load_agents(registry)

    # Crear servicio de IA
    ai_service = AIService()

    # Crear procesador de resultados
    processor = ResultProcessor(ai_service)

    # Crear el orquestador
    zeus = Orchestrator(
        registry,
        processor,
        ai_service
    )

    voice = VoiceService()

    print("=== Lacerta iniciado ===")

    print(registry)

    for agent in registry.get_all():
        print(agent)

    while True:

        print("\n¿Cómo quieres introducir la petición?")
        print("[1] Escribir")
        print("[2] Hablar")
        print("[3] Salir")

        mode = input("> ")

        if mode == "1":
            request = input("Tú: ")

        elif mode == "2":
            request = voice.listen()

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

        response = zeus.handle(request)

        print(response)


if __name__ == "__main__":
    main()