from core.registry import Registry
from agents.hermes import Hermes
from agents.poseidon import Poseidon
from agents.hefesto import Hefesto
from agents.hipnos import Hipnos
from agents.orfeo import Orfeo


def load_agents(registry: Registry) -> None:
    """
    Carga y registra todos los agentes disponibles en Lacerta.
    """

    registry.register(Hermes())
    registry.register(Poseidon())
    registry.register(Hefesto())
    registry.register(Hipnos())
    registry.register(Orfeo())