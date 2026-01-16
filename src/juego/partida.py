from random import shuffle, choice
from collections import Counter as Multiset
from enum import Enum, auto
from copy import copy, deepcopy
from .carta import Carta
from .excepciones import JuegoException, JuegoInvalidoException
from .estado_del_jugador import EstadoDeJugador

SIRENAS_INF = 999

def cartasDelJuego():
	return list([
		Carta(Carta.Tipo.CANGREJO, Carta.Color.AZUL),
		Carta(Carta.Tipo.CANGREJO, Carta.Color.AZUL),
		Carta(Carta.Tipo.CANGREJO, Carta.Color.CELESTE),
		Carta(Carta.Tipo.CANGREJO, Carta.Color.CELESTE),
		Carta(Carta.Tipo.CANGREJO, Carta.Color.NEGRO),
		Carta(Carta.Tipo.CANGREJO, Carta.Color.AMARILLO),
		Carta(Carta.Tipo.CANGREJO, Carta.Color.AMARILLO),
		Carta(Carta.Tipo.CANGREJO, Carta.Color.VERDE),
		Carta(Carta.Tipo.CANGREJO, Carta.Color.GRIS),
		
		Carta(Carta.Tipo.BARCO, Carta.Color.AZUL),
		Carta(Carta.Tipo.BARCO, Carta.Color.AZUL),
		Carta(Carta.Tipo.BARCO, Carta.Color.CELESTE),
		Carta(Carta.Tipo.BARCO, Carta.Color.CELESTE),
		Carta(Carta.Tipo.BARCO, Carta.Color.NEGRO),
		Carta(Carta.Tipo.BARCO, Carta.Color.NEGRO),
		Carta(Carta.Tipo.BARCO, Carta.Color.AMARILLO),
		Carta(Carta.Tipo.BARCO, Carta.Color.AMARILLO),
		
		Carta(Carta.Tipo.PEZ, Carta.Color.AZUL),
		Carta(Carta.Tipo.PEZ, Carta.Color.AZUL),
		Carta(Carta.Tipo.PEZ, Carta.Color.CELESTE),
		Carta(Carta.Tipo.PEZ, Carta.Color.NEGRO),
		Carta(Carta.Tipo.PEZ, Carta.Color.NEGRO),
		Carta(Carta.Tipo.PEZ, Carta.Color.AMARILLO),
		Carta(Carta.Tipo.PEZ, Carta.Color.VERDE),
		
		Carta(Carta.Tipo.NADADOR, Carta.Color.AZUL),
		Carta(Carta.Tipo.NADADOR, Carta.Color.CELESTE),
		Carta(Carta.Tipo.NADADOR, Carta.Color.NEGRO),
		Carta(Carta.Tipo.NADADOR, Carta.Color.AMARILLO),
		Carta(Carta.Tipo.NADADOR, Carta.Color.NARANJA_CLARO),
		
		Carta(Carta.Tipo.TIBURÓN, Carta.Color.AZUL),
		Carta(Carta.Tipo.TIBURÓN, Carta.Color.CELESTE),
		Carta(Carta.Tipo.TIBURÓN, Carta.Color.NEGRO),
		Carta(Carta.Tipo.TIBURÓN, Carta.Color.VERDE),
		Carta(Carta.Tipo.TIBURÓN, Carta.Color.VIOLETA),
		
		Carta(Carta.Tipo.CONCHA, Carta.Color.AZUL),
		Carta(Carta.Tipo.CONCHA, Carta.Color.CELESTE),
		Carta(Carta.Tipo.CONCHA, Carta.Color.NEGRO),
		Carta(Carta.Tipo.CONCHA, Carta.Color.AMARILLO),
		Carta(Carta.Tipo.CONCHA, Carta.Color.VERDE),
		Carta(Carta.Tipo.CONCHA, Carta.Color.GRIS),
		
		Carta(Carta.Tipo.PULPO, Carta.Color.CELESTE),
		Carta(Carta.Tipo.PULPO, Carta.Color.AMARILLO),
		Carta(Carta.Tipo.PULPO, Carta.Color.VERDE),
		Carta(Carta.Tipo.PULPO, Carta.Color.VIOLETA),
		Carta(Carta.Tipo.PULPO, Carta.Color.GRIS),
		
		Carta(Carta.Tipo.PINGUINO, Carta.Color.VIOLETA),
		Carta(Carta.Tipo.PINGUINO, Carta.Color.NARANJA_CLARO),
		Carta(Carta.Tipo.PINGUINO, Carta.Color.ROSA),
		
		Carta(Carta.Tipo.ANCLA, Carta.Color.ROSA),
		Carta(Carta.Tipo.ANCLA, Carta.Color.NARANJA),
		
		Carta(Carta.Tipo.COLONIA, Carta.Color.VERDE),
		Carta(Carta.Tipo.FARO, Carta.Color.VIOLETA),
		Carta(Carta.Tipo.CARDUMEN, Carta.Color.GRIS),
		Carta(Carta.Tipo.CAPITÁN, Carta.Color.NARANJA_CLARO),
		
		Carta(Carta.Tipo.SIRENA, Carta.Color.BLANCO),
		Carta(Carta.Tipo.SIRENA, Carta.Color.BLANCO),
		Carta(Carta.Tipo.SIRENA, Carta.Color.BLANCO),
		Carta(Carta.Tipo.SIRENA, Carta.Color.BLANCO)
	])

class PartidaDeOcéanos():
	class Estado(Enum):
		PARTIDA_NO_INICIADA = auto()
		FASE_ROBO = auto()
		FASE_ROBO_DEL_MAZO = auto()
		FASE_DÚOS = auto()
		RONDA_TERMINADA = auto()
		PARTIDA_TERMINADA = auto()
	
	# ============================ ESTADO PÚBLICO ============================
	@property
	def topeDelDescarte(self):
		return (
			(copy(self._descarte[0][-1]) if len(self._descarte[0]) > 0 else None),
			(copy(self._descarte[1][-1]) if len(self._descarte[1]) > 0 else None)
		)
	
	@property
	def cantidadDeCartasEnDescarte(self):
		return (
			len(self._descarte[0]),
			len(self._descarte[1])
		)
	
	def cantidadDeCartasEnManoDelJugador(self, jugador):
		if not (0 <= jugador and jugador < self._cantidadDeJugadores):
			raise JuegoException("El jugador seleccionado es inválido")
		return self._estadosDeJugadores[jugador].mano.total()
	
	@property
	def cantidadDeCartasEnMazo(self):
		return len(self._mazo)
	
	def zonaDeDúosDelJugador(self, jugador):
		if not (0 <= jugador and jugador < self._cantidadDeJugadores):
			raise JuegoException("El jugador seleccionado es inválido")
		return deepcopy(self._estadosDeJugadores[jugador].zonaDeDúos)
	
	@property
	def zonaDeDúos(self):
		return self.zonaDeDúosDelJugador(self._deQuiénEsTurno)
	
	@property
	def mano(self):
		return deepcopy(self._estadosDeJugadores[self._deQuiénEsTurno].mano)
	
	@property
	def puntajeDeRonda(self):
		return self._estadosDeJugadores[self._deQuiénEsTurno].puntajeDeRonda()
	
	def rondaEnCurso(self):
		return self._estadoActual in [
			self.Estado.FASE_ROBO,
			self.Estado.FASE_ROBO_DEL_MAZO,
			self.Estado.FASE_DÚOS
		]
	
	def haTerminado(self):
		return self._estadoActual == self.Estado.PARTIDA_TERMINADA
	
	def hayQueRobar(self):
		return self._estadoActual == self.Estado.FASE_ROBO
	
	def seHaRobadoEsteTurno(self):
		return self._estadoActual == self.Estado.FASE_DÚOS
	
	def hayQueTomarDecisionesDeRoboDelMazo(self):
		return self._estadoActual == self.Estado.FASE_ROBO_DEL_MAZO
	
	def últimaChanceEnCurso(self):
		return self._últimaChancePorJugador != None
	
	def últimaChanceGanada(self):
		return bool(self._últimaChanceGanada) if self._últimaChanceGanada != None else None
	
	def rondaAnulada(self):
		return bool(self._rondaAnulada)
	
	@property
	def cantidadDeJugadores(self):
		return int(self._cantidadDeJugadores)
	
	@property
	def deQuiénEsTurno(self):
		return int(self._deQuiénEsTurno)
	
	@property
	def puntajes(self):
		return list(self._puntajes.copy())
	
	@property
	def puntajeParaGanar(self):
		return self._obtenerPuntajeParaGanarParaCantidadDeJugadores(self._cantidadDeJugadores)
	
	@property
	def jugadorGanador(self):
		return int(self._jugadorGanador) if self._jugadorGanador != None else None
	
	@property
	def jugadorQueDijoÚltimaChance(self):
		return int(self._últimaChancePorJugador) if self._últimaChancePorJugador != None else None
	
	
	# ============================ FLUJO DE PARTIDA ============================
	def __init__(self, cantidadDeJugadores=2):
		if(not (2 <= cantidadDeJugadores and cantidadDeJugadores <= 4)):
			raise JuegoInvalidoException("La cantidad de jugadores es inválida")
		
		self._cantidadDeJugadores = cantidadDeJugadores 
		self._deQuiénEsTurno = 0
		self._puntajes = [0] * cantidadDeJugadores
		self._jugadorGanador = None
		self._últimaChancePorJugador = None
		self._últimaChanceGanada = None
		self._descarte = None
		self._estadosDeJugadores = None
		self._mazo = None
		self._estadoActual = self.Estado.PARTIDA_NO_INICIADA
		self._rondaAnulada = None
	
	def iniciarRonda(self):
		if self.rondaEnCurso():
			raise JuegoException("Ya hay una ronda en curso!")
		
		self._estadosDeJugadores = [EstadoDeJugador() for _ in range(self._cantidadDeJugadores)]
		self._mazo = list(cartasDelJuego())
		shuffle(self._mazo)
		self._descarte = ([self._mazo.pop(0)], [self._mazo.pop(0)])
		self._estadoActual = self.Estado.FASE_ROBO
		self._últimaChancePorJugador = None
		self._últimaChanceGanada = None
		self._rondaAnulada = False
	
	# ============================== FASE DE ROBO ==============================
	def robarDelDescarte(self, indicePilaDeDescarte):
		self._assertSePuedeElegirAcciónDeRobo()
		self._assertÍndicePilaDeDescarteVálidoParaRobar(indicePilaDeDescarte)
		
		cartaRobada = self._descarte[indicePilaDeDescarte].pop()
		self._estadosDeJugadores[self._deQuiénEsTurno].mano[cartaRobada] += 1
		self._estadoActual = self.Estado.FASE_DÚOS
		
		self._calcularSiHayGanadorPorSirenas()
		
		return cartaRobada
	
	def verCartasParaRobarDelMazo(self):
		self._assertSePuedeElegirAcciónDeRobo()
		if len(self._mazo) == 0:
			raise JuegoException("No se puede robar de un mazo vacío")
		
		self._estadoActual = self.Estado.FASE_ROBO_DEL_MAZO
		
		if len(self._mazo) == 1:
			return [self._mazo[-1]]
		return [self._mazo[-1], self._mazo[-2]]
	
	def robarDelMazo(self, indiceDeCartaARobar, indiceDePilaDondeDescartar):
		self._assertSePuedeRobarDelMazo()
		
		self._assertObjetivoDeRoboDelMazoYDescarteVálido(indiceDePilaDondeDescartar, indiceDeCartaARobar)
		
		cartasRobadasDelMazo = [self._mazo.pop()]
		if len(self._mazo) > 0:
			cartasRobadasDelMazo.append(self._mazo.pop())
			self._descarte[indiceDePilaDondeDescartar].append(cartasRobadasDelMazo[1 - indiceDeCartaARobar])
		cartaRobada = cartasRobadasDelMazo[indiceDeCartaARobar]
		self._estadosDeJugadores[self._deQuiénEsTurno].mano[cartaRobada] += 1
		
		self._estadoActual = self.Estado.FASE_DÚOS
		
		self._calcularSiHayGanadorPorSirenas()
		
		return cartaRobada
	
	# ============================== FASE DE DÚOS ===============================
	def jugarDúoDePeces(self, cartasAJugar):
		self._assertSePuedeJugarDúo(cartasAJugar)
		self._assertDúoEsDeTipo(cartasAJugar, Carta.Tipo.PEZ)
		
		self._moverDúoAZonaDeDúo(cartasAJugar)
		
		cartaRobada = None
		if len(self._mazo) > 0:
			cartaRobada = self._mazo.pop()
			self._estadosDeJugadores[self._deQuiénEsTurno].mano[cartaRobada] += 1
			self._calcularSiHayGanadorPorSirenas()
		
		return cartaRobada
	
	def jugarDúoDeBarcos(self, cartasAJugar):
		self._assertSePuedeJugarDúo(cartasAJugar)
		self._assertDúoEsDeTipo(cartasAJugar, Carta.Tipo.BARCO)
		
		self._moverDúoAZonaDeDúo(cartasAJugar)
		
		if len(self._mazo) == 0:
			# ronda anulada por mazo vacío
			
			self._estadoActual = self.Estado.RONDA_TERMINADA
			self._rondaAnulada = True
			
			self._deQuiénEsTurno = (self._deQuiénEsTurno + 1) % self._cantidadDeJugadores
			return
		
		self._estadoActual = self.Estado.FASE_ROBO
	
	def jugarDúoDeCangrejos(self, cartasAJugar, pilaDeDescarteARobar, indiceDeCartaARobar):
		self._assertSePuedeJugarDúo(cartasAJugar)
		self._assertDúoEsDeTipo(cartasAJugar, Carta.Tipo.CANGREJO)
		
		self._assertObjetivoDeDúoDeCangrejosVálido(pilaDeDescarteARobar, indiceDeCartaARobar)
		
		self._moverDúoAZonaDeDúo(cartasAJugar)
		if len(self._descarte[0]) == 0 and len(self._descarte[1]) == 0:
			return None
		
		cartaRobada = self._descarte[pilaDeDescarteARobar][indiceDeCartaARobar]
		self._estadosDeJugadores[self._deQuiénEsTurno].mano[cartaRobada] += 1
		del self._descarte[pilaDeDescarteARobar][indiceDeCartaARobar]
		
		self._calcularSiHayGanadorPorSirenas()
		
		return cartaRobada
	
	def jugarDúoDeNadadorYTiburón(self, cartasAJugar, jugadorARobar):
		self._assertSePuedeJugarDúo(cartasAJugar)
		self._assertDúoEsDeTipo(cartasAJugar, Carta.Tipo.TIBURÓN)
		self._assertObjetivoDeDúoDeNadadorYTiburónVálido(jugadorARobar)
		
		self._moverDúoAZonaDeDúo(cartasAJugar)
		
		cartaRobada = None
		if self._estadosDeJugadores[jugadorARobar].mano.total() > 0:
			cartaRobada = choice(list(self._estadosDeJugadores[jugadorARobar].mano.elements()))
			
			self._estadosDeJugadores[self._deQuiénEsTurno].mano[cartaRobada] += 1
			
			self._estadosDeJugadores[jugadorARobar].mano[cartaRobada] -= 1
			if self._estadosDeJugadores[jugadorARobar].mano[cartaRobada] == 0:
				del self._estadosDeJugadores[jugadorARobar].mano[cartaRobada]
			
			self._calcularSiHayGanadorPorSirenas()
		
		return cartaRobada
	
	# =============================== FASE DE FIN ================================
	def pasarTurno(self):
		self._assertSePuedeTerminarElTurno()
		
		if len(self._mazo) == 0:
			# ronda anulada por mazo vacío
			
			self._estadoActual = self.Estado.RONDA_TERMINADA
			self._rondaAnulada = True
			
			self._deQuiénEsTurno = (self._deQuiénEsTurno + 1) % self._cantidadDeJugadores
			return
		
		self._deQuiénEsTurno = (self._deQuiénEsTurno + 1) % self._cantidadDeJugadores
		
		if self._últimaChancePorJugador == self._deQuiénEsTurno:
			#calcular fin de ronda por apuesta de última chance
			if self._estadosDeJugadores[self._últimaChancePorJugador].puntajeDeRonda() == max([self._estadosDeJugadores[j].puntajeDeRonda() for j in range(self._cantidadDeJugadores)]):
				# apuesta ganada
				self._últimaChanceGanada = True
				for jugador in range(self._cantidadDeJugadores):
					self._puntajes[jugador] += self._estadosDeJugadores[jugador]._bonificacionPorColor()
				self._puntajes[self._últimaChancePorJugador] += self._estadosDeJugadores[self._últimaChancePorJugador].puntajeDeRonda()
			else: 
				# apuesta perdida
				self._últimaChanceGanada = False
				for jugador in range(self._cantidadDeJugadores):
					if jugador != self._últimaChancePorJugador:
						self._puntajes[jugador] += self._estadosDeJugadores[jugador].puntajeDeRonda()
				self._puntajes[self._últimaChancePorJugador] += self._estadosDeJugadores[self._últimaChancePorJugador]._bonificacionPorColor()
			
			
			self._estadoActual = self.Estado.RONDA_TERMINADA
			
			self._deQuiénEsTurno = (self._deQuiénEsTurno + 1) % self._cantidadDeJugadores
			self._calcularSiHayGanador()
		
		else:
			
			self._estadoActual = self.Estado.FASE_ROBO
	
	def decirBasta(self):
		self._assertSePuedeTerminarElTurno()
		self._assertSePuedeTerminarLaRonda()
		
		for jugador in range(self._cantidadDeJugadores):
			self._puntajes[jugador] += self._estadosDeJugadores[jugador].puntajeDeRonda()
		
		self._estadoActual = self.Estado.RONDA_TERMINADA
		
		self._deQuiénEsTurno = (self._deQuiénEsTurno + 1) % self._cantidadDeJugadores
		self._calcularSiHayGanador()
	
	def decirÚltimaChance(self):
		self._assertSePuedeTerminarElTurno()
		self._assertSePuedeTerminarLaRonda()
		
		if len(self._mazo) == 0:
			# ronda anulada por mazo vacío
			
			self._estadoActual = self.Estado.RONDA_TERMINADA
			self._rondaAnulada = True
			
			self._deQuiénEsTurno = (self._deQuiénEsTurno + 1) % self._cantidadDeJugadores
			return
		
		
		self._estadoActual = self.Estado.FASE_ROBO
		
		self._últimaChancePorJugador = self._deQuiénEsTurno
		self._deQuiénEsTurno = (self._deQuiénEsTurno + 1) % self._cantidadDeJugadores
	
	# =========================== AUXILIARES DE CÁLCULO ===========================
	def _calcularSiHayGanador(self):
		puntajeMáximoAlcanzado = max(self._puntajes)
		if puntajeMáximoAlcanzado >= self.puntajeParaGanar:
			
			self._estadoActual = self.Estado.PARTIDA_TERMINADA
			
			
			# calcular ganador
			for orden in range(self._cantidadDeJugadores):
				jugadorEnOrden = (self._deQuiénEsTurno - 1 - orden) % self._cantidadDeJugadores
				if self._puntajes[jugadorEnOrden] == puntajeMáximoAlcanzado:
					self._jugadorGanador = jugadorEnOrden
					break;
	
	def _calcularSiHayGanadorPorSirenas(self):
		for j in range(self._cantidadDeJugadores):
			if self._estadosDeJugadores[j].mano[Carta(Carta.Tipo.SIRENA, Carta.Color.BLANCO)] == 4:
				
				self._estadoActual = self.Estado.PARTIDA_TERMINADA
				
				self._jugadorGanador = j
				self._puntajes[j] = SIRENAS_INF
		
	# ============================= AUXILIARES VARIOS ==============================
	def _moverDúoAZonaDeDúo(self, cartasAJugar):
		for clave in cartasAJugar:
			self._estadosDeJugadores[self._deQuiénEsTurno].mano[clave] -= cartasAJugar[clave]
			if self._estadosDeJugadores[self._deQuiénEsTurno].mano[clave] == 0:
				del self._estadosDeJugadores[self._deQuiénEsTurno].mano[clave]
		
		self._estadosDeJugadores[self._deQuiénEsTurno].zonaDeDúos[
			tuple(sorted((list(cartasAJugar.elements())[0], list(cartasAJugar.elements())[1])))
		] += 1
	
	def _obtenerPuntajeParaGanarParaCantidadDeJugadores(self, cantidadDeJugadores):
		if cantidadDeJugadores == 2:
			return 40
		elif cantidadDeJugadores == 3:
			return 35
		elif cantidadDeJugadores == 4:
			return 30
		else:
			raise JuegoException("La cantidad de jugadores no es válida")
	
	def _jugadorMostróSuManoPorÚltimaChance(self, jugador):
		if not self.últimaChanceEnCurso():
			return False
		else:
			for orden in range(self._últimaChancePorJugador + 1, self._últimaChancePorJugador + 1 + self._cantidadDeJugadores):
				jugadorEnOrden = orden % self._cantidadDeJugadores
				if jugadorEnOrden == self._deQuiénEsTurno:
					return False
				if jugadorEnOrden == jugador:
					return True
	
	# ========================== AUXILIARES DE ASERCIONES ==========================
	def _assertSePuedeElegirAcciónDeRobo(self):
		if not self.rondaEnCurso():
			raise JuegoException("No hay una ronda en curso")
		if self.hayQueTomarDecisionesDeRoboDelMazo():
			raise JuegoException("No se ha concretado el robo del mazo (¡falta elegir!)")
		if self.seHaRobadoEsteTurno():
			raise JuegoException("Ya se ha robado en este turno")
	
	def _assertSePuedeRobarDelMazo(self):
		if not self.rondaEnCurso():
			raise JuegoException("No hay una ronda en curso")
		if not self.hayQueTomarDecisionesDeRoboDelMazo():
			raise JuegoException("Debe confirmarse que se va a robar del mazo")
		if self.seHaRobadoEsteTurno():
			raise JuegoException("Ya se ha robado en este turno")
	
	def _assertObjetivoDeRoboDelMazoYDescarteVálido(self, indiceDePilaDondeDescartar, indiceDeCartaARobar):
		if not len(self._mazo) > 1:
			if not (0 <= indiceDeCartaARobar and indiceDeCartaARobar < len(self._mazo)):
				raise JuegoException("No se puede elegir una carta para robar fuera del rango")
			return
		if not (0 <= indiceDePilaDondeDescartar and indiceDePilaDondeDescartar <= 1):
			raise JuegoException("Pila de descarte no existente")
		elif len(self._descarte[indiceDePilaDondeDescartar]) > 0 and len(self._descarte[1 - indiceDePilaDondeDescartar]) == 0:
			raise JuegoException("No se puede descartar en una pila no vacía mientras la otra se encuentre vacía")
		elif not (0 <= indiceDeCartaARobar and indiceDeCartaARobar < 2):
			raise JuegoException("No se puede elegir una carta para robar fuera del rango")
	
	def _assertÍndicePilaDeDescarteVálidoParaRobar(self, indicePilaDeDescarte):
		if not (0 <= indicePilaDeDescarte and indicePilaDeDescarte < len(self._descarte)):
			raise JuegoException("Pila de descarte no existente")
		if len(self._descarte[indicePilaDeDescarte]) == 0:
			raise JuegoException("No se puede robar de una pila de descarte vacía")
	
	def _assertSePuedeJugarDúo(self, cartasAJugar):
		if not self.rondaEnCurso():
			raise JuegoException("No hay una ronda en curso")
		if self.hayQueTomarDecisionesDeRoboDelMazo():
			raise JuegoException("No se ha concretado el robo del mazo (¡falta elegir!)")
		if not self.seHaRobadoEsteTurno():
			raise JuegoException("No se puede jugar dúos sin antes haber robado")
		
		if cartasAJugar.total() != 2:
			raise JuegoException("Se necesitan dos cartas para jugar un dúo")
		
		for carta in cartasAJugar.elements():
			if not carta.esDúo():
				raise JuegoException("Se necesitan cartas dúo para jugar un dúo")
		
		tipos = [list(cartasAJugar.elements())[0].tipo, list(cartasAJugar.elements())[1].tipo] if (list(cartasAJugar.elements())[0].tipo.value < list(cartasAJugar.elements())[1].tipo.value) else [list(cartasAJugar.elements())[1].tipo, list(cartasAJugar.elements())[0].tipo]
		
		if not ((
				tipos[0] == Carta.Tipo.NADADOR and
				tipos[1] == Carta.Tipo.TIBURÓN
			) or (
				tipos[0] != Carta.Tipo.NADADOR and
				tipos[1] == tipos[0]
		)):
			raise JuegoException("Se necesitan cartas del mismo tipo dúo para jugar un dúo")
		
		if not (cartasAJugar <= self._estadosDeJugadores[self._deQuiénEsTurno].mano):
			raise JuegoException("Las cartas seleccionadas no están en la mano")
	
	def _assertDúoEsDeTipo(self, cartasAJugar, tipoObjetivo):
		if tipoObjetivo in [Carta.Tipo.NADADOR, Carta.Tipo.TIBURÓN]:
			tipos = [list(cartasAJugar.elements())[0].tipo, list(cartasAJugar.elements())[1].tipo] if (list(cartasAJugar.elements())[0].tipo.value < list(cartasAJugar.elements())[1].tipo.value) else [list(cartasAJugar.elements())[1].tipo, list(cartasAJugar.elements())[0].tipo]
			if tipos[0] != Carta.Tipo.NADADOR or tipos[1] != Carta.Tipo.TIBURÓN:
				raise JuegoException("Ese tipo de dúo no es válido para esta acción")
		else:
			if next(iter(cartasAJugar)).tipo !=  tipoObjetivo:
				raise JuegoException("Ese tipo de dúo no es válido para esta acción")
	
	def _assertObjetivoDeDúoDeCangrejosVálido(self, pilaDeDescarteARobar, indiceDeCartaARobar):
		if (len(self._descarte[0]) != 0 or len(self._descarte[1]) != 0) and (
			(not (0 <= pilaDeDescarteARobar and pilaDeDescarteARobar <= 1) )
			or (
				not (0 <= indiceDeCartaARobar and indiceDeCartaARobar < len(self._descarte[pilaDeDescarteARobar]))
			)
		):
			raise JuegoException("La selección de robo con el dúo de cangrejos es inválida")
	
	def _assertObjetivoDeDúoDeNadadorYTiburónVálido(self, jugadorARobar):
		if not (
			0 <= jugadorARobar and jugadorARobar < self._cantidadDeJugadores and jugadorARobar != self._deQuiénEsTurno
			and not self._jugadorMostróSuManoPorÚltimaChance(jugadorARobar)
		):
			raise JuegoException("La selección de jugador a robar con el dúo de nadador y tiburón es inválida")
	
	def _assertSePuedeTerminarElTurno(self):
		if not self.rondaEnCurso():
			raise JuegoException("No hay una ronda en curso")
		if self.hayQueTomarDecisionesDeRoboDelMazo():
			raise JuegoException("No se ha concretado el robo del mazo (¡falta elegir!)")
		if not self.seHaRobadoEsteTurno():
			raise JuegoException("No se puede terminar el turno sin antes haber robado")
	
	def _assertSePuedeTerminarLaRonda(self):
		if not (self._estadosDeJugadores[self._deQuiénEsTurno].puntajeDeRonda() >= 7):
			raise JuegoException("No se puede terminar la ronda si no se tienen al menos siete puntos")
		if self.últimaChanceEnCurso():
			raise JuegoException("Ya se está jugando una ronda de última chance")
	
