from random import choice
from collections import Counter as Multiset
from administrador.acción import Acción
from administrador.evento import Evento
from juego.carta import Carta
from juego.partida import PartidaDeOcéanos
from ..base import JugadorBase
from jugador.registro import registrarComo

@registrarComo("sirena_enjoyer")
class SirenaEnjoyer(JugadorBase):
	def __init__(self) -> None:
		super().__init__()
	
	def configurarParaJuego(self, juego: PartidaDeOcéanos, númeroDeJugador: int, listaDeEventos: list[Evento]) -> None:
		super().configurarParaJuego(juego, númeroDeJugador, listaDeEventos)
	
	def decidirAcciónDeRobo(self) -> Acción.Robo:
		if self._juego.cantidadDeCartasEnDescarte[0] > 0 and self._juego.topeDelDescarte[0].tipo == Carta.Tipo.SIRENA:
			return Acción.Robo.DEL_DESCARTE_0
		if self._juego.cantidadDeCartasEnDescarte[1] > 0 and self._juego.topeDelDescarte[1].tipo == Carta.Tipo.SIRENA:
			return Acción.Robo.DEL_DESCARTE_1
		return Acción.Robo.DEL_MAZO
	
	def decidirCómoRobarDelMazo(self, opcionesDeRobo: list[Carta]) -> tuple[int, int|None]:
		if len(opcionesDeRobo) == 1:
			return (0, None)
		else:
			pilaVálida = 0 if self._juego.cantidadDeCartasEnDescarte[0] == 0 else 1
			if opcionesDeRobo[0].tipo == Carta.Tipo.SIRENA:
				return (0, pilaVálida)
			else:
				return (1, pilaVálida)
	
	def decidirAcciónDeDúos(self) -> tuple[Acción.Dúos, Multiset[Carta]|None, tuple[any]|None]:
		return (Acción.Dúos.NO_JUGAR, None, None)
	
	def decidirAcciónDeFinDeTurno(self) -> Acción.FinDeTurno:
		#if self._juego.cantidadDeCartasEnMazo < 2 and self._juego.puntajeDeRonda >= 7:
		#	return Acción.FinDeTurno.DECIR_BASTA
		return Acción.FinDeTurno.PASAR_TURNO
	
	def configurarInicioDeRonda(self, cartasInicialesDelDescarte: tuple[Carta, Carta]) -> None:
		pass
	
	def configurarFinDeRonda(self, manos: list[Multiset[Carta]], puntajesDeRonda: list[int]) -> None:
		pass
	
	def configurarInicioDeTurno(self) -> None:
		pass