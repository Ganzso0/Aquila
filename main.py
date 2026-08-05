from core.registry import Registry
from core.orchestrator import Orchestrator


def main():
    """
    Punto de entrada de Lacerta.
    """

    # Crear el registro de agentes
    registry = Registry()

    # Crear el orquestador
    zeus = Orchestrator(registry)

    print("=== Lacerta iniciado ===")

    while True:

        request = input("\n> ")

        if request.lower() in ("exit", "quit"):
            print("Cerrando Lacerta...")
            break

        response = zeus.handle(request)

        print(response)


if __name__ == "__main__":
    main()