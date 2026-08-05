from core.registry import Registry
from core.orchestrator import Orchestrator
from agents.loader import load_agents
from core.result_processor import ResultProcessor


def main():
    """
    Punto de entrada de Lacerta.
    """

    # Crear el registro de agentes
    registry = Registry()

    load_agents(registry)

    processor = ResultProcessor()

    # Crear el orquestador
    zeus = Orchestrator(registry,processor)

    print("=== Lacerta iniciado ===")

    print(registry)

    for agent in registry.get_all():
        print(agent)

    while True:

        request = input("\n> ")

        if request.lower() in ("exit", "quit"):
            print("Cerrando Lacerta...")
            break

        response = zeus.handle(request)

        print(response)


if __name__ == "__main__":
    main()