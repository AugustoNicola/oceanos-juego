from typing import Type
from jugador.base import JugadorBase

JUGADORES: dict[str, Type[JugadorBase]] = {}

def registrarComo(nombreJugador: str):
    def decorator(claseJugador: Type[JugadorBase]):
        if nombreJugador in JUGADORES:
            raise RuntimeError(f"Nombre duplicado: {nombreJugador}")
        JUGADORES[nombreJugador] = claseJugador
        return claseJugador
    return decorator