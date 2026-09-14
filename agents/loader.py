from core.registry import Registry
from agents.hermes import Hermes
from agents.poseidon import Poseidon
from agents.hefesto import Hefesto
from agents.orfeo import Orfeo
from agents.nix import Nix


def load_agents(registry: Registry) -> None:
    """
    Carga y registra todos los agentes disponibles en Lacerta.
    """

    registry.register(Hermes())
    registry.register(Poseidon())
    registry.register(Hefesto())
    registry.register(Orfeo())
    registry.register(Nix())