from random import choice
from collections import Counter as Multiset
from administrador.acción import Acción
from administrador.evento import Evento
from juego.carta import Carta
from juego.partida import PartidaDeOcéanos
from ..base import JugadorBase
from jugador.registro import registrarComo

@registrarComo("randybot")
class RandyBot(JugadorBase):
	def __init__(self):
		super().__init__()
	
	def configurarParaJuego(self, juego: PartidaDeOcéanos, númeroDeJugador: int, listaDeEventos: list[Evento]) -> None:
		super().configurarParaJuego(juego, númeroDeJugador, listaDeEventos)
	
	def decidirAcciónDeRobo(self) -> Acción.Robo:
		accionesPosibles = [Acción.Robo.DEL_MAZO]
		if self._juego.cantidadDeCartasEnDescarte[0] > 0:
			accionesPosibles.append(Acción.Robo.DEL_DESCARTE_0)
		if self._juego.cantidadDeCartasEnDescarte[1] > 0:
			accionesPosibles.append(Acción.Robo.DEL_DESCARTE_1)
		return choice(accionesPosibles)
	
	def decidirCómoRobarDelMazo(self, opcionesDeRobo: list[Carta]) -> tuple[int, int|None]:
		if len(opcionesDeRobo) == 1:
			return (0, None)
		else:
			indiceDeCartaARobar = choice([0,1])
			indiceDePilaDondeDescartar = None
			
			if self._juego.cantidadDeCartasEnDescarte[0] > 0 and self._juego.cantidadDeCartasEnDescarte[1] == 0:
				indiceDePilaDondeDescartar = 1
			elif self._juego.cantidadDeCartasEnDescarte[1] > 0 and self._juego.cantidadDeCartasEnDescarte[0] == 0:
				indiceDePilaDondeDescartar = 0
			else:
				indiceDePilaDondeDescartar = choice([0,1])
			return (indiceDeCartaARobar, indiceDePilaDondeDescartar)
	
	def decidirAcciónDeDúos(self) -> tuple[Acción.Dúos, Multiset[Carta]|None, tuple[any]|None]:
		
		accionesPosibles = [Acción.Dúos.NO_JUGAR]
		
		
		posibleDúoDePeces = self._buscarDúoParaJugar(Carta.Tipo.PEZ)
		if posibleDúoDePeces != None:
			accionesPosibles.append(Acción.Dúos.JUGAR_PECES)
		
		posibleDúoDeBarcos = self._buscarDúoParaJugar(Carta.Tipo.BARCO)
		if posibleDúoDeBarcos != None:
			accionesPosibles.append(Acción.Dúos.JUGAR_BARCOS)
			
		posibleDúoDeCangrejos = self._buscarDúoParaJugar(Carta.Tipo.CANGREJO)
		if posibleDúoDeCangrejos != None and (self._juego.cantidadDeCartasEnDescarte[0] > 0 or self._juego.cantidadDeCartasEnDescarte[1] > 0):
			accionesPosibles.append(Acción.Dúos.JUGAR_CANGREJOS)
		
		posibleDúoDeNadadorYTiburón = self._buscarDúoParaJugar(Carta.Tipo.NADADOR)
		if posibleDúoDeNadadorYTiburón != None and not self._juego.últimaChanceEnCurso():
			accionesPosibles.append(Acción.Dúos.JUGAR_NADADOR_Y_TIBURÓN)
		
		acciónElegida = choice(accionesPosibles)
		if acciónElegida == Acción.Dúos.JUGAR_PECES:
			return (acciónElegida, posibleDúoDePeces, None)
		
		elif acciónElegida == Acción.Dúos.JUGAR_BARCOS:
			return (acciónElegida, posibleDúoDeBarcos, None)
		
		elif acciónElegida == Acción.Dúos.JUGAR_CANGREJOS:
			pilasPosibles = []
			if (self._juego.cantidadDeCartasEnDescarte[0] > 0):
				pilasPosibles.append(0)
			if (self._juego.cantidadDeCartasEnDescarte[1] > 0):
				pilasPosibles.append(1)
			pilaElegida = choice(pilasPosibles)
			
			return (acciónElegida, posibleDúoDeCangrejos, (pilaElegida,))
		
		elif acciónElegida == Acción.Dúos.JUGAR_NADADOR_Y_TIBURÓN:
			jugadorARobar = list(range(self._juego.cantidadDeJugadores))
			del jugadorARobar[self._númeroDeJugador]
			return (acciónElegida, posibleDúoDeNadadorYTiburón, (jugadorARobar))
		
		elif acciónElegida == Acción.Dúos.NO_JUGAR:
			return (Acción.Dúos.NO_JUGAR, None, None)
	
	def decidirQuéRobarConDúoDeCangrejos(self, descarteElegido: list[Carta]) -> int:
		return choice(list(range(len(descarteElegido))))
	
	def decidirAcciónDeFinDeTurno(self) -> Acción.FinDeTurno:
		accionesDeFinDeTurnoPosibles = [Acción.FinDeTurno.PASAR_TURNO]
		
		if self._juego.puntajeDeRonda >= 7 and (not self._juego.últimaChanceEnCurso()):
			accionesDeFinDeTurnoPosibles.append(Acción.FinDeTurno.DECIR_BASTA)
			accionesDeFinDeTurnoPosibles.append(Acción.FinDeTurno.DECIR_ÚLTIMA_CHANCE)
		
		return choice(accionesDeFinDeTurnoPosibles)
	
	def configurarInicioDeRonda(self, cartasInicialesDelDescarte: tuple[Carta, Carta]) -> None:
		pass
	
	def configurarFinDeRonda(self, manos: list[Multiset[Carta]], puntajesDeRonda: list[int]) -> None:
		pass
	
	def configurarInicioDeTurno(self) -> None:
		pass
	