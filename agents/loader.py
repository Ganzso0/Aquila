from core.registry import Registry
from agents.hermes import Hermes
from agents.poseidon import Poseidon


def load_agents(registry: Registry) -> None:
    """
    Carga y registra todos los agentes disponibles en Lacerta.
    """

    registry.register(Hermes())
    registry.register(Poseidon())