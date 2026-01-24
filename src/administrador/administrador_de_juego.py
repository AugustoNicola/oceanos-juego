import sys
from random import shuffle
from copy import copy, deepcopy
from enum import Enum, auto
from .acción import Acción
from .evento import Evento
from .excepcion_esperando import ExcepciónEsperando
from juego.carta import Carta
from juego.partida import PartidaDeOcéanos, SIRENAS_INF
import jugador

class AdministradorDeJuego():
	class Verbosidad(Enum):
		NADA = auto()
		JUGADOR = auto()
		OMNISCIENTE = auto()
	
	class Fases(Enum):
		INICIO_RONDA = auto()
		ROBO = auto()
		DUOS = auto()
		FIN = auto()
	
	def __init__(self, nombresDeJugadores, verbosidad=Verbosidad.NADA, partidaActiva=False, randomizarOrden=False):
		if not verbosidad in AdministradorDeJuego.Verbosidad:
			raise Exception("Usar el enum AdministradorDeJuego.Verbosidad")
		
		self._cantidadDeJugadores = len(nombresDeJugadores)
		
		# clases de los jugadores nombrados al crear el administrador. Nunca cambia de orden.
		self._clasesDeJugadores = [jugador.registro.JUGADORES[nombreClase] for nombreClase in nombresDeJugadores]
		
		# instancias de jugadores, adaptados al orden de la partida actual. Va cambiando de orden.
		self._jugadores: list[jugador.base.JugadorBase] = [None] * len(nombresDeJugadores)
		
		# Este arreglo almacena la biyección entre el orden en que los jugadores fueron ingresados al sistema
		#   (en self._jugadores), y el orden real en los asientos de la partida actual
		# self._ordenPartidaJugadores[i] = j significa que el asiento j-ésimo lo está ocupando el jugador i-ésimo
		#    ej, self._ordenPartidaJugadores[0] = 2 significa que self._clasesDeJugadores[2]
		#    empieza jugando esta partida
		# Siempre se comienza en el mismo orden en el que se inscribieron los jugadores al administrador
		self._ordenPartidaJugadores = list(range(self._cantidadDeJugadores))
		self._próximoOrdenPartidaJugadores = list(range(self._cantidadDeJugadores))
		self._randomizarOrden = randomizarOrden
		
		self._juego = None
		self._verbosidad = verbosidad
		self._eventos = []
		
		self._partidaActiva = partidaActiva
		self._permisoParaSeguir = False
		self._continuarEn = None
		
		self._noSeQuierenJugarMásDúos = False
		
		self._rondasTerminadas = 0
		self._rondasTerminadasSinFinPorSirenas = 0
		
		# Estos arreglos de estadísticas están indexados por el orden de clase jugador (el que no cambia nunca)
		self._cantidadDeCartasPorJugadorPorTipo = [{tipo: 0 for tipo in Carta.Tipo} for _ in range(self._cantidadDeJugadores)]
		self._partidasGanadasPorJugador = [0 for _ in range(self._cantidadDeJugadores)]
		self._puntosPorJugadorPorRonda = [ [] for _ in range(self._cantidadDeJugadores) ]
		
		self._dúosJugadosPorJugadorPorTipo = [{
			Carta.Tipo.PEZ: 0,
			Carta.Tipo.BARCO: 0,
			Carta.Tipo.CANGREJO: 0,
			Carta.Tipo.NADADOR: 0
		} for _ in range(self._cantidadDeJugadores)]
		
		self._dúosEnManoPorJugadorPorTipo = [{
			Carta.Tipo.PEZ: 0,
			Carta.Tipo.BARCO: 0,
			Carta.Tipo.CANGREJO: 0,
			Carta.Tipo.NADADOR: 0
		} for _ in range(self._cantidadDeJugadores)]
		
		self._motivosFinDeRonda = {
			"0_CARTAS": 0,
			"BASTA": 0,
			"4_SIRENAS": 0,
			"ÚLTIMA_CHANCE": 0
		}
		
		self._motivosFinDeRondaPorJugador = [{
			"BASTA": 0,
			"ÚLTIMA_CHANCE_GANADA": 0,
			"ÚLTIMA_CHANCE_PERDIDA": 0,
			"4_SIRENAS": 0,
		} for _ in range(self._cantidadDeJugadores)]
	
	def jugarPartida(self):
		self._inicializarPartida()
		
		while not self._juego.haTerminado():
			self._inicializarRonda()

			while self._juego.rondaEnCurso():
				self._faseInicioTurno()
				self._faseDeRobo()
				self._faseDeDúos()
				self._faseDeFin()
			
			self._finDeRonda()
		
		self._finDePartida()
		return self._juego.jugadorGanador
	
	def continuar(self):
		self._permisoParaSeguir = True
		buscandoPuntoDeContinuar = self._continuarEn != None
		
		try:
			if not buscandoPuntoDeContinuar:
				self._inicializarPartida()
			
			while not self._juego.haTerminado():
				if not buscandoPuntoDeContinuar or self._continuarEn == self.Fases.INICIO_RONDA:
					buscandoPuntoDeContinuar = False
					self._inicializarRonda()
					

				while self._juego.rondaEnCurso():
					if not buscandoPuntoDeContinuar:
						self._faseInicioTurno()
					if not buscandoPuntoDeContinuar or self._continuarEn == self.Fases.ROBO:
						buscandoPuntoDeContinuar = False
						self._faseDeRobo()
					if not buscandoPuntoDeContinuar or self._continuarEn == self.Fases.DUOS:
						buscandoPuntoDeContinuar = False
						self._faseDeDúos()
					if not buscandoPuntoDeContinuar or self._continuarEn == self.Fases.FIN:
						buscandoPuntoDeContinuar = False
						self._faseDeFin()
				
				self._finDeRonda()
			
			self._finDePartida()
		except ExcepciónEsperando as e:
			print(f"Esperando en {e}")
			return None
			
		return self._juego.jugadorGanador
	
	def obtenerEstadoPartida(self):
		return {
			"mazo": self._juego._mazo,
			"descarte": self._juego._descarte,
			"estadosDeJugadores": [self.obtenerEstadoJugador(númeroJugador) for númeroJugador in range(self._cantidadDeJugadores)],
			"puntajes": self._juego.puntajes,
			"puntajesRonda": [self._juego._estadosDeJugadores[j].puntajeDeRonda() for j in range(self._cantidadDeJugadores)],
			"deQuienEsTurno": self._juego.deQuiénEsTurno,
			"últimaChanceEnCurso": self._juego.últimaChanceEnCurso(),
			"fase": self._juego._estadoActual.name
		}
	def obtenerEstadoJugador(self, númeroJugador):
		return {
			"mano": [carta.aDiccionario() for carta, cantidad in self._juego._estadosDeJugadores[númeroJugador].mano.items() for _ in range(cantidad) ],
			"duos": [(dúo[0].aDiccionario(), dúo[1].aDiccionario()) for dúo, cantidad in self._juego._estadosDeJugadores[númeroJugador].zonaDeDúos.items() for _ in range(cantidad) ]
		}
	
	def _inicializarPartida(self):
		# Cambiamos el orden de los jugadores en esta partida
		if self._randomizarOrden:
			self._ordenPartidaJugadores = self._próximoOrdenPartidaJugadores.copy()
			shuffle(self._próximoOrdenPartidaJugadores)
		
		self._juego = PartidaDeOcéanos(cantidadDeJugadores=self._cantidadDeJugadores)
		for j in range(len(self._clasesDeJugadores)):
			self._jugadores[j] = (self._clasesDeJugadores[self._claseJugadorEnPosición(j)])()
			self._jugadores[j].configurarParaJuego(self._juego, j, self._eventos)
		if self._verbosidad != AdministradorDeJuego.Verbosidad.NADA:
			print("~~~~~~~~~~~~~~~~~~~~ Orden Partida ~~~~~~~~~~~~~~~~~~~~~~")
			for j in range(self._cantidadDeJugadores):
				print((self._clasesDeJugadores[self._claseJugadorEnPosición(j)].__name__))
			print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	
	def _inicializarRonda(self):
		if self._partidaActiva and not self._permisoParaSeguir:
			self._continuarEn = self.Fases.INICIO_RONDA
			raise ExcepciónEsperando("INICIO_RONDA")
		self._permisoParaSeguir = False
		
		self._eventos.clear()
				
		self._juego.iniciarRonda()
		if self._verbosidad != AdministradorDeJuego.Verbosidad.NADA:
			print("~~~~~~~~~~~~~~~~~~~~~ Inicia Ronda ~~~~~~~~~~~~~~~~~~~~~~")
			print(f"Jugador inicial: {self._juego.deQuiénEsTurno}")
			print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
				
		for j in range(self._cantidadDeJugadores):
			self._jugadores[j].configurarInicioDeRonda(self._juego.topeDelDescarte)
	
	def _faseInicioTurno(self):
		if self._verbosidad != AdministradorDeJuego.Verbosidad.NADA:
			print(f"~~~~~~~~~~~~~~~~~~~~ Turno del jugador {self._juego.deQuiénEsTurno} ~~~~~~~~~~~~~~~~~~~~")
			print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
			if self._verbosidad == AdministradorDeJuego.Verbosidad.OMNISCIENTE:
				print(f"El descarte 0 es {(self._juego._descarte[0])}")
				print(f"El descarte 1 es {(self._juego._descarte[1])}")
			elif self._verbosidad == AdministradorDeJuego.Verbosidad.JUGADOR:
				print(f"El tope del descarte 0 es {(self._juego.topeDelDescarte[0])}")
				print(f"El tope del descarte 1 es {(self._juego.topeDelDescarte[1])}")
		
		self._jugadores[self._juego.deQuiénEsTurno].configurarInicioDeTurno()
	
	def _faseDeRobo(self):
		if self._partidaActiva and not self._permisoParaSeguir:
			self._continuarEn = self.Fases.ROBO
			raise ExcepciónEsperando("ROBO")
		self._permisoParaSeguir = False
		
		acciónDeRobo = self._jugadores[self._juego.deQuiénEsTurno].decidirAcciónDeRobo()
		
		if acciónDeRobo == Acción.Robo.DEL_MAZO:
			# Robar del mazo
			opcionesDeRobo = self._juego.verCartasParaRobarDelMazo()
			(indiceDeCartaARobar, indiceDePilaDondeDescartar) = self._jugadores[self._juego.deQuiénEsTurno].decidirCómoRobarDelMazo(opcionesDeRobo)
			cartaRobada = self._juego.robarDelMazo(indiceDeCartaARobar, indiceDePilaDondeDescartar)
			
			self._eventos.append(Evento(self._juego.deQuiénEsTurno, Acción.Robo.DEL_MAZO,
				{
					"cartaDescartada": copy(self._juego.topeDelDescarte[indiceDePilaDondeDescartar]) if len(opcionesDeRobo) > 1 else None,
					"pilaDondeDescartó": indiceDePilaDondeDescartar if len(opcionesDeRobo) > 1 else None,
					"_cartaRobada": cartaRobada # ! SOLO VER SI FUISTE EL JUGADOR QUE ROBÓ!!!
				}
			))
			if self._verbosidad == AdministradorDeJuego.Verbosidad.OMNISCIENTE:
				if len(opcionesDeRobo) > 1:
					print(f"Roba del mazo una {cartaRobada}, descarta una {self._juego.topeDelDescarte[indiceDePilaDondeDescartar]} en la pila {indiceDePilaDondeDescartar}")
				else:
					print(f"Roba del mazo una {cartaRobada}, la última carta del mazo")
			elif self._verbosidad == AdministradorDeJuego.Verbosidad.JUGADOR:
				if len(opcionesDeRobo) > 1:
					print(f"Roba del mazo, descarta una {self._juego.topeDelDescarte[indiceDePilaDondeDescartar]} en la pila {indiceDePilaDondeDescartar}")
				else:
					print(f"Roba la última carta del mazo")
			
		elif acciónDeRobo == Acción.Robo.DEL_DESCARTE_0:
			cartaRobada = self._juego.robarDelDescarte(0)
			
			self._eventos.append(Evento(self._juego.deQuiénEsTurno, Acción.Robo.DEL_DESCARTE_0,
				{
					"cartaRobada": copy(cartaRobada)
				}
			))
			if self._verbosidad != AdministradorDeJuego.Verbosidad.NADA:
				print(f"Roba del descarte 0 una {cartaRobada}")
		elif acciónDeRobo == Acción.Robo.DEL_DESCARTE_1:
			cartaRobada = self._juego.robarDelDescarte(1)
			
			self._eventos.append(Evento(self._juego.deQuiénEsTurno, Acción.Robo.DEL_DESCARTE_1,
				{
					"cartaRobada": copy(cartaRobada)
				}
			))
			if self._verbosidad != AdministradorDeJuego.Verbosidad.NADA:
				print(f"Roba del descarte 1 una {cartaRobada}")
		else:
			#! ERROR
			raise Exception("Error")

	def _faseDeDúos(self):
		self._noSeQuierenJugarMásDúos = False
		
		while not self._noSeQuierenJugarMásDúos and not self._juego.haTerminado():
			if self._partidaActiva and not self._permisoParaSeguir:
				self._continuarEn = self.Fases.DUOS
				raise ExcepciónEsperando("DUOS")
			self._permisoParaSeguir = False
			
			(acciónDeDúos, cartasAJugar, parametrosDelDúo) = self._jugadores[self._juego.deQuiénEsTurno].decidirAcciónDeDúos()
			if acciónDeDúos == Acción.Dúos.JUGAR_PECES:
				# Jugar dúo de peces
				cartaRobada = self._juego.jugarDúoDePeces(cartasAJugar)
				if self._verbosidad == AdministradorDeJuego.Verbosidad.OMNISCIENTE:
					print(f"Juega un dúo de {list(cartasAJugar.elements())[0]} y {list(cartasAJugar.elements())[1]} y roba una {cartaRobada} del mazo")
				elif self._verbosidad == AdministradorDeJuego.Verbosidad.JUGADOR:
					print(f"Juega un dúo de {list(cartasAJugar.elements())[0]} y {list(cartasAJugar.elements())[1]} y roba una carta del mazo")
				self._eventos.append(Evento(self._juego.deQuiénEsTurno, acciónDeDúos,
					{
						"cartasJugadas": deepcopy(sorted(cartasAJugar.elements())),
						"_cartaRobada": cartaRobada # ! SOLO VER SI FUISTE EL JUGADOR QUE JUGÓ EL DÚO!!!
					}
				))
				
			elif acciónDeDúos == Acción.Dúos.JUGAR_BARCOS:
				# Jugar dúo de barcos
				self._eventos.append(Evento(self._juego.deQuiénEsTurno, acciónDeDúos,
					{
						"cartasJugadas": deepcopy(sorted(cartasAJugar.elements()))
					}
				))
				
				if self._verbosidad != AdministradorDeJuego.Verbosidad.NADA:
					print(f"Juega un dúo de {list(cartasAJugar.elements())[0]} y {list(cartasAJugar.elements())[1]}; consigue otro turno")
				self._juego.jugarDúoDeBarcos(cartasAJugar)
				if self._juego.rondaEnCurso():
					self._faseDeRobo()
					self._faseDeDúos()
				self._noSeQuierenJugarMásDúos = True
				
			elif acciónDeDúos == Acción.Dúos.JUGAR_CANGREJOS:
				# Jugar dúo de cangrejos
				pilaDeDescarteARobar = parametrosDelDúo[0]
				indiceDeCartaARobar = self._jugadores[self._juego.deQuiénEsTurno].decidirQuéRobarConDúoDeCangrejos(deepcopy(self._juego._descarte[pilaDeDescarteARobar]))
				
				cartaRobada = self._juego.jugarDúoDeCangrejos(cartasAJugar, pilaDeDescarteARobar, indiceDeCartaARobar)
				if self._verbosidad == AdministradorDeJuego.Verbosidad.OMNISCIENTE:
					print(f"Juega un dúo de {list(cartasAJugar.elements())[0]} y {list(cartasAJugar.elements())[1]} para robar una {cartaRobada} de la pila {pilaDeDescarteARobar}")
				elif self._verbosidad == AdministradorDeJuego.Verbosidad.JUGADOR:
					print(f"Juega un dúo de {list(cartasAJugar.elements())[0]} y {list(cartasAJugar.elements())[1]} para robar una carta de la pila {pilaDeDescarteARobar}")
				
				self._eventos.append(Evento(self._juego.deQuiénEsTurno, acciónDeDúos,
					{
						"cartasJugadas": deepcopy(sorted(cartasAJugar.elements())),
						"pilaDondeRobó": pilaDeDescarteARobar,
						"_cartaRobada": cartaRobada # ! SOLO VER SI FUISTE EL JUGADOR QUE JUGÓ EL DÚO!!!
					}
				))
				
			elif acciónDeDúos == Acción.Dúos.JUGAR_NADADOR_Y_TIBURÓN:
				# Jugar dúo de nadador y tiburón
				jugadorARobar = parametrosDelDúo[0]
				cartaRobada = self._juego.jugarDúoDeNadadorYTiburón(cartasAJugar, jugadorARobar)
				
				self._eventos.append(Evento(self._juego.deQuiénEsTurno, acciónDeDúos,
					{
						"cartasJugadas": deepcopy(sorted(cartasAJugar.elements())),
						"jugadorRobado": jugadorARobar,
						"_cartaRobada": cartaRobada # ! SOLO VER SI FUISTE EL JUGADOR ROBADO!!!
					}
				))
				if self._verbosidad == AdministradorDeJuego.Verbosidad.OMNISCIENTE:
					print(f"Juega un dúo de {list(cartasAJugar.elements())[0]} y {list(cartasAJugar.elements())[1]} para robarle al jugador {jugadorARobar}, y roba una {cartaRobada}")
				elif self._verbosidad == AdministradorDeJuego.Verbosidad.JUGADOR:
					print(f"Juega un dúo de {list(cartasAJugar.elements())[0]} y {list(cartasAJugar.elements())[1]} para robarle al jugador {jugadorARobar}")
				
			elif acciónDeDúos == Acción.Dúos.NO_JUGAR:
				# No jugar dúos
				self._noSeQuierenJugarMásDúos = True
				self._permisoParaSeguir = True
			else:
				#! ERROR
				raise Exception("Error")

	def _faseDeFin(self):
		if not self._juego.haTerminado() and self._juego.rondaEnCurso():
			
			if self._partidaActiva and not self._permisoParaSeguir:
				self._continuarEn = self.Fases.FIN
				raise ExcepciónEsperando("FIN")
			self._permisoParaSeguir = False
			
			acciónDeFinDeTurno = self._jugadores[self._juego.deQuiénEsTurno].decidirAcciónDeFinDeTurno()
			
			self._eventos.append(Evento(self._juego.deQuiénEsTurno, acciónDeFinDeTurno, {
				"puntajesRonda": [ int(self._juego._estadosDeJugadores[j].puntajeDeRonda()) for j in range(self._cantidadDeJugadores)]
			}))
			
			cuerpoEventoFin = {}
			jugadorEventoFin = self._juego.deQuiénEsTurno
			
			if acciónDeFinDeTurno == Acción.FinDeTurno.PASAR_TURNO:
				# Pasar el turno normalmente				
				self._juego.pasarTurno()
				if self._verbosidad != AdministradorDeJuego.Verbosidad.NADA:
					print("Pasa de turno")
				if self._juego.rondaEnCurso():
					# turno terminado normalmente, la ronda continúa
					cuerpoEventoFin = {
						"estadoRonda": "EN_CURSO"
					}
				elif self._juego.rondaAnulada():
					# ronda anulada por mazo vacío
					cuerpoEventoFin = {
						"estadoRonda": "ANULADA_MAZO_VACÍO"
					}
					pass
				elif self._juego.últimaChanceGanada() != None:
					# ronda terminada por última chance
					
					puntajesRonda = [0 for _ in range(self._cantidadDeJugadores)]
					
					for j in range(self._cantidadDeJugadores):
						if self._juego.últimaChanceGanada():
							if j == self._juego.jugadorQueDijoÚltimaChance:
								puntajesRonda[j] = self._juego._estadosDeJugadores[j].puntajeDeRonda() + self._juego._estadosDeJugadores[j]._bonificacionPorColor()
							else:
								puntajesRonda[j] = self._juego._estadosDeJugadores[j]._bonificacionPorColor()
						else:
							if j == self._juego.jugadorQueDijoÚltimaChance:
								puntajesRonda[j] = self._juego._estadosDeJugadores[j]._bonificacionPorColor()
							else:
								puntajesRonda[j] = self._juego._estadosDeJugadores[j].puntajeDeRonda()
					
					cuerpoEventoFin = {
						"estadoRonda": "ÚLTIMA_CHANCE_GANADA" if self._juego.últimaChanceGanada() else "ÚLTIMA_CHANCE_PERDIDA",
						"puntajesRonda":  puntajesRonda
					}
				
			elif acciónDeFinDeTurno == Acción.FinDeTurno.DECIR_BASTA:
				# Decir basta y terminar la ronda
				self._juego.decirBasta()
				if self._verbosidad != AdministradorDeJuego.Verbosidad.NADA:
					print("¡¡¡Basta!!!")
				cuerpoEventoFin = {
					"puntajesRonda": [ int(self._juego._estadosDeJugadores[j].puntajeDeRonda()) for j in range(self._cantidadDeJugadores)]
				}
			elif acciónDeFinDeTurno == Acción.FinDeTurno.DECIR_ÚLTIMA_CHANCE:
				# Decir última chance y pasar el turno
				self._juego.decirÚltimaChance()
				if self._verbosidad != AdministradorDeJuego.Verbosidad.NADA:
					print("¡¡¡Última Chance!!!")
			else:
				#! ERROR
				raise Exception("Error")
		
			self._eventos.append(Evento(jugadorEventoFin, acciónDeFinDeTurno, cuerpoEventoFin))
	
	def _finDeRonda(self):		
		self._rondasTerminadas += 1
		if max(self._juego.puntajes) == SIRENAS_INF:
			self._motivosFinDeRonda["4_SIRENAS"] += 1
			self._motivosFinDeRondaPorJugador[self._claseJugadorEnPosición(self._juego.jugadorGanador)]["4_SIRENAS"] += 1
			if self._verbosidad != AdministradorDeJuego.Verbosidad.NADA:
				print("################### CUATRO SIRENAS ###################")
				print(f"Ganador: {self._juego.jugadorGanador}")
				for j in range(self._juego.cantidadDeJugadores):
					if self._juego.puntajes[j] == SIRENAS_INF:
						print(f"Jugador {j}: +INF (INF/{self._juego.puntajeParaGanar})")
					else:
						print(f"Jugador {j}: +0 ({self._juego.puntajes[j]}/{self._juego.puntajeParaGanar})")
				print("######################################################")
		elif self._juego.rondaAnulada():
			self._rondasTerminadasSinFinPorSirenas += 1
			self._motivosFinDeRonda["0_CARTAS"] += 1
			for j in range(self._cantidadDeJugadores):
				self._puntosPorJugadorPorRonda[j].append(0)
			if self._verbosidad != AdministradorDeJuego.Verbosidad.NADA:
				print("********* Ronda anulada por cero cartas en mazo *********")
				for j in range(self._juego.cantidadDeJugadores):
					print(f"Jugador {j}: +0 ({self._juego.puntajes[j]}/{self._juego.puntajeParaGanar})")
				print("*********************************************************")
		elif self._juego.últimaChanceEnCurso():
			self._rondasTerminadasSinFinPorSirenas += 1
			self._motivosFinDeRonda["ÚLTIMA_CHANCE"] += 1
			if self._juego.últimaChanceGanada():
				self._motivosFinDeRondaPorJugador[self._claseJugadorEnPosición(self._juego.jugadorQueDijoÚltimaChance)]["ÚLTIMA_CHANCE_GANADA"] += 1
			else:
				self._motivosFinDeRondaPorJugador[self._claseJugadorEnPosición(self._juego.jugadorQueDijoÚltimaChance)]["ÚLTIMA_CHANCE_PERDIDA"] += 1
			for j in range(self._cantidadDeJugadores):
				índiceClaseJugador = self._claseJugadorEnPosición(j)
				
				if self._juego.últimaChanceGanada():
					if j == self._juego.jugadorQueDijoÚltimaChance:
						self._puntosPorJugadorPorRonda[índiceClaseJugador].append(self._juego._estadosDeJugadores[j].puntajeDeRonda() + self._juego._estadosDeJugadores[j]._bonificacionPorColor())
					else:
						self._puntosPorJugadorPorRonda[índiceClaseJugador].append(self._juego._estadosDeJugadores[j]._bonificacionPorColor())
				else:
					if j == self._juego.jugadorQueDijoÚltimaChance:
						self._puntosPorJugadorPorRonda[índiceClaseJugador].append(self._juego._estadosDeJugadores[j]._bonificacionPorColor())
					else:
						self._puntosPorJugadorPorRonda[índiceClaseJugador].append(self._juego._estadosDeJugadores[j].puntajeDeRonda())
			if self._verbosidad != AdministradorDeJuego.Verbosidad.NADA:
				print("*********** Ronda terminada por última chance ***********")
				if self._juego.últimaChanceGanada():
					print("¡Apuesta ganada!")
					for j in range(self._juego.cantidadDeJugadores):
						if j == self._juego.jugadorQueDijoÚltimaChance:
							print(f"Jugador {j}: +{self._juego._estadosDeJugadores[j].puntajeDeRonda() + self._juego._estadosDeJugadores[j]._bonificacionPorColor()} ({self._juego.puntajes[j]}/{self._juego.puntajeParaGanar})")
						else:
							print(f"Jugador {j}: +{self._juego._estadosDeJugadores[j]._bonificacionPorColor()} ({self._juego.puntajes[j]}/{self._juego.puntajeParaGanar})")
				else:
					print("Apuesta perdida...")
					for j in range(self._juego.cantidadDeJugadores):
						if j == self._juego.jugadorQueDijoÚltimaChance:
							print(f"Jugador {j}: +{self._juego._estadosDeJugadores[j]._bonificacionPorColor()} ({self._juego.puntajes[j]}/{self._juego.puntajeParaGanar})")
						else:
							print(f"Jugador {j}: +{self._juego._estadosDeJugadores[j].puntajeDeRonda()} ({self._juego.puntajes[j]}/{self._juego.puntajeParaGanar})")
				print("*********************************************************")
		else:
			self._rondasTerminadasSinFinPorSirenas += 1
			self._motivosFinDeRonda["BASTA"] += 1
			self._motivosFinDeRondaPorJugador[self._claseJugadorEnPosición((self._juego.deQuiénEsTurno - 1) % self._juego.cantidadDeJugadores)]["BASTA"] += 1
			for j in range(self._cantidadDeJugadores):
				índiceClaseJugador = self._claseJugadorEnPosición(j)
				self._puntosPorJugadorPorRonda[índiceClaseJugador].append(self._juego._estadosDeJugadores[j].puntajeDeRonda())
			if self._verbosidad != AdministradorDeJuego.Verbosidad.NADA:
				print("*************** Ronda terminada por basta ***************")
				for j in range(self._juego.cantidadDeJugadores):
					print(f"Jugador {j}: +{self._juego._estadosDeJugadores[j].puntajeDeRonda()} ({self._juego.puntajes[j]}/{self._juego.puntajeParaGanar})")					
				print("*********************************************************")
		
		if self._verbosidad != self.Verbosidad.NADA:
			for j in range(self._cantidadDeJugadores):
				print(f"Mano del jugador {j}:\n{self._juego._estadosDeJugadores[j].mano}")
				print(f"zona de dúos del jugador {j}:\n{self._juego._estadosDeJugadores[j].zonaDeDúos}\n")
		
		self._calcularEstadísticasDeRonda()
		
		quiénArranca = self._juego._deQuiénEsTurno
		manos = [deepcopy(self._juego._estadosDeJugadores[j].mano) for j in range(self._cantidadDeJugadores)]
		puntajesDeRonda = [ int(self._juego._estadosDeJugadores[j].puntajeDeRonda()) for j in range(self._cantidadDeJugadores)]
		for j in range(self._cantidadDeJugadores):
			self._juego._deQuiénEsTurno = j
			self._jugadores[j].configurarFinDeRonda(manos, puntajesDeRonda)
		self._juego._deQuiénEsTurno = quiénArranca
	
	def _finDePartida(self):
		self._partidasGanadasPorJugador[self._claseJugadorEnPosición(self._juego.jugadorGanador)] += 1
		if self._verbosidad != AdministradorDeJuego.Verbosidad.NADA:
			print("!!!!!!!!!!!!!!!!!!! Partida Terminada !!!!!!!!!!!!!!!!!!!")
			print(f"Ganador: {self._juego.jugadorGanador}")
			print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
	
	def _claseJugadorEnPosición(self, índicePosiciónBuscada: int) -> int:
		# Dado un índice de self._jugadores (orden de ESTA partida),
		#   obtener cuál es el correspondiente índice en self._clasesDeJugadores
		return self._ordenPartidaJugadores[índicePosiciónBuscada]
	
	def _posiciónDeClaseJugador(self, índiceClaseJugadorBuscado: int) -> int:
		# Dado un índice de self._clasesDeJugadores (ordenes estáticos introducidos al sistema),
		#   obtener cuál es el correspondiente índice en self._jugadores de ESTA partida
		return next((
			índicePartida for índicePartida, índiceClase in enumerate(self._ordenPartidaJugadores)
			if índiceClase == índiceClaseJugadorBuscado
		), None)
	
	def _calcularEstadísticasDeRonda(self):
		for posición in range(self._cantidadDeJugadores):
			índiceClaseJugador = self._claseJugadorEnPosición(posición)
			
			# Cálculos auxiliares...
			cantidadDeCartasEnManoDeTipo = {tipo: 0 for tipo in Carta.Tipo}
			cantidadDeCartasEnZonaDeDúosDeTipo = {tipo: 0 for tipo in Carta.Tipo}
			cantidadDeDúosEnJuegoDeTipo = {
				Carta.Tipo.PEZ: 0,
				Carta.Tipo.BARCO: 0,
				Carta.Tipo.CANGREJO: 0,
				Carta.Tipo.NADADOR: 0    # noo maldito enum que no me deja poner nombres declarativos!
			}
			
			for claveDeCarta in self._juego._estadosDeJugadores[posición].mano:
				cantidadDeCartasEnManoDeTipo[claveDeCarta.tipo] += self._juego._estadosDeJugadores[posición].mano[claveDeCarta]
			
			for claveDeDúo in self._juego._estadosDeJugadores[posición].zonaDeDúos:
				cantidadDeDúosEnJuegoDeTipo[claveDeDúo[0].tipo] += self._juego._estadosDeJugadores[posición].zonaDeDúos[claveDeDúo]
				cantidadDeCartasEnZonaDeDúosDeTipo[claveDeDúo[0].tipo] += self._juego._estadosDeJugadores[posición].zonaDeDúos[claveDeDúo]
				cantidadDeCartasEnZonaDeDúosDeTipo[claveDeDúo[1].tipo] += self._juego._estadosDeJugadores[posición].zonaDeDúos[claveDeDúo]
			
			
			# Calcular dúos en juego del jugador en esta ronda
			for tipoDúo in [Carta.Tipo.PEZ, Carta.Tipo.BARCO, Carta.Tipo.CANGREJO, Carta.Tipo.NADADOR]:
				self._dúosJugadosPorJugadorPorTipo[índiceClaseJugador][tipoDúo] += cantidadDeDúosEnJuegoDeTipo[tipoDúo]
			
			# Calcular dúos en mano del jugador en esta ronda
			self._dúosEnManoPorJugadorPorTipo[índiceClaseJugador][Carta.Tipo.PEZ] += cantidadDeCartasEnManoDeTipo[Carta.Tipo.PEZ] // 2
			self._dúosEnManoPorJugadorPorTipo[índiceClaseJugador][Carta.Tipo.BARCO] += cantidadDeCartasEnManoDeTipo[Carta.Tipo.BARCO] // 2
			self._dúosEnManoPorJugadorPorTipo[índiceClaseJugador][Carta.Tipo.CANGREJO] += cantidadDeCartasEnManoDeTipo[Carta.Tipo.CANGREJO] // 2
			self._dúosEnManoPorJugadorPorTipo[índiceClaseJugador][Carta.Tipo.NADADOR] += min(cantidadDeCartasEnManoDeTipo[Carta.Tipo.NADADOR], cantidadDeCartasEnManoDeTipo[Carta.Tipo.TIBURÓN])
			
			# Calcular cartas poseídas de cada tipo en esta ronda
			for tipo in Carta.Tipo:
				self._cantidadDeCartasPorJugadorPorTipo[índiceClaseJugador][tipo] += cantidadDeCartasEnManoDeTipo[tipo] + cantidadDeCartasEnZonaDeDúosDeTipo[tipo]
	
if __name__ == '__main__':
	administrador = AdministradorDeJuego(sys.argv[1:], verbosidad=AdministradorDeJuego.Verbosidad.OMNISCIENTE)
	ganador = administrador.jugarPartida()
	print(f"Ganador: {ganador}")
