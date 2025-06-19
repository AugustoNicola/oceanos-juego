from copy import copy, deepcopy
from enum import Enum, auto
from .acción import Acción
from .evento import Evento
from juego.carta import Carta
from juego.partida import PartidaDeOcéanos, SIRENAS_INF
from jugador.RandyBot.randy import RandyBot
from jugador.CLI.cli import JugadorCLI
from jugador.base import JugadorBase
from jugador.PuntosBot.puntosbot_mk1 import PuntosBotMk1
from jugador.PuntosBot.puntosbot_mk2 import PuntosBotMk2

class AdministradorDeJuego():
	class Verbosidad(Enum):
		NADA = auto()
		JUGADOR = auto()
		OMNISCIENTE = auto()
	
	def __init__(self, clasesDeJugadores, verbosidad=Verbosidad.NADA):
		if not verbosidad in AdministradorDeJuego.Verbosidad:
			raise Exception("Usar el enum AdministradorDeJuego.Verbosidad")
		
		self._clasesDeJugadores = clasesDeJugadores
		self._jugadores: list[JugadorBase] = [None] * len(clasesDeJugadores)
		self._juego = None
		self._verbosidad = verbosidad
		self._eventos = []
		
		self._rondasTerminadas = 0
		self._rondasTerminadasSinFinPorSirenas = 0
		
		self._cantidadDeCartasPorJugadorPorTipo = [{tipo: 0 for tipo in Carta.Tipo} for _ in range(len(self._jugadores))]
		self._partidasGanadasPorJugador = [0 for _ in range(len(self._jugadores))]
		self._puntosPorJugadorPorRonda = [ [] for _ in range(len(self._jugadores)) ]
		
		self._dúosJugadosPorJugadorPorTipo = [{
			Carta.Tipo.PEZ: 0,
			Carta.Tipo.BARCO: 0,
			Carta.Tipo.CANGREJO: 0,
			Carta.Tipo.NADADOR: 0
		} for _ in range(len(self._jugadores))]
		
		self._dúosEnManoPorJugadorPorTipo = [{
			Carta.Tipo.PEZ: 0,
			Carta.Tipo.BARCO: 0,
			Carta.Tipo.CANGREJO: 0,
			Carta.Tipo.NADADOR: 0
		} for _ in range(len(self._jugadores))]
		
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
		} for _ in range(len(self._jugadores))]
	
	def jugarPartida(self):
		self._juego = PartidaDeOcéanos(cantidadDeJugadores=len(self._jugadores))
		for j in range(len(self._clasesDeJugadores)):
			self._jugadores[j] = (self._clasesDeJugadores[j])()
			self._jugadores[j].configurarParaJuego(self._juego, j, self._eventos)
		
		while not self._juego.haTerminado():
			self._eventos.clear()
			
			self._juego.iniciarRonda()
			if self._verbosidad != AdministradorDeJuego.Verbosidad.NADA:
				print("~~~~~~~~~~~~~~~~~~~~~ Inicia Ronda ~~~~~~~~~~~~~~~~~~~~~~")
				print(f"Jugador inicial: {self._juego.deQuiénEsTurno}")
				print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
			
			for j in range(len(self._jugadores)):
				self._jugadores[j].configurarInicioDeRonda(self._juego.topeDelDescarte)

			while self._juego.rondaEnCurso():
				if self._verbosidad != AdministradorDeJuego.Verbosidad.NADA:
					print(f"~~~~~~~~~~~~~~~~~~~ Turno del jugador {self._juego.deQuiénEsTurno} ~~~~~~~~~~~~~~~~~~~~")
					print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
					if self._verbosidad == AdministradorDeJuego.Verbosidad.OMNISCIENTE:
						print(f"El descarte 0 es {(self._juego._descarte[0])}")
						print(f"El descarte 1 es {(self._juego._descarte[1])}")
					elif self._verbosidad == AdministradorDeJuego.Verbosidad.JUGADOR:
						print(f"El tope del descarte 0 es {(self._juego.topeDelDescarte[0])}")
						print(f"El tope del descarte 1 es {(self._juego.topeDelDescarte[1])}")
				
				self._jugadores[self._juego.deQuiénEsTurno].configurarInicioDeTurno()
				
				self._faseDeRobo()
				self._faseDeDúos()
				self._faseDeFin()
			
			self._finDeRonda()
		
		self._partidasGanadasPorJugador[self._juego.jugadorGanador] += 1
		if self._verbosidad != AdministradorDeJuego.Verbosidad.NADA:
			print("!!!!!!!!!!!!!!!!!!! Partida Terminada !!!!!!!!!!!!!!!!!!!")
			print(f"Ganador: {self._juego.jugadorGanador}")
			print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		return self._juego.jugadorGanador
	
	def _faseDeRobo(self):
		acciónDeRobo = self._jugadores[self._juego.deQuiénEsTurno].decidirAcciónDeRobo()
		
		if acciónDeRobo == Acción.Robo.DEL_MAZO:
			# Robar del mazo
			opcionesDeRobo = self._juego.verCartasParaRobarDelMazo()
			(indiceDeCartaARobar, indiceDePilaDondeDescartar) = self._jugadores[self._juego.deQuiénEsTurno].decidirCómoRobarDelMazo(opcionesDeRobo)
			cartaRobada = self._juego.robarDelMazo(indiceDeCartaARobar, indiceDePilaDondeDescartar)
			
			self._eventos.append(Evento(self._juego.deQuiénEsTurno, Acción.Robo.DEL_MAZO,
				{
					"cartaDescartada": copy(self._juego.topeDelDescarte[indiceDePilaDondeDescartar]) if len(opcionesDeRobo) > 1 else None,
					"pilaDondeDescartó": indiceDePilaDondeDescartar if len(opcionesDeRobo) > 1 else None
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
		noSeQuierenJugarMásDúos = False
		
		while not noSeQuierenJugarMásDúos and not self._juego.haTerminado():
			(acciónDeDúos, cartasAJugar, parametrosDelDúo) = self._jugadores[self._juego.deQuiénEsTurno].decidirAcciónDeDúos()
			if acciónDeDúos == Acción.Dúos.JUGAR_PECES:
				# Jugar dúo de peces
				self._eventos.append(Evento(self._juego.deQuiénEsTurno, acciónDeDúos,
					{
						"cartasJugadas": deepcopy(sorted(cartasAJugar.elements()))
					}
				))
				
				cartaRobada = self._juego.jugarDúoDePeces(cartasAJugar)
				if self._verbosidad == AdministradorDeJuego.Verbosidad.OMNISCIENTE:
					print(f"Juega un dúo de {list(cartasAJugar.elements())[0]} y {list(cartasAJugar.elements())[1]} y roba una {cartaRobada} del mazo")
				elif self._verbosidad == AdministradorDeJuego.Verbosidad.JUGADOR:
					print(f"Juega un dúo de {list(cartasAJugar.elements())[0]} y {list(cartasAJugar.elements())[1]} y roba una carta del mazo")
				
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
				noSeQuierenJugarMásDúos = True
				
			elif acciónDeDúos == Acción.Dúos.JUGAR_CANGREJOS:
				# Jugar dúo de cangrejos
				pilaDeDescarteARobar = parametrosDelDúo[0]
				indiceDeCartaARobar = self._jugadores[self._juego.deQuiénEsTurno].decidirQuéRobarConDúoDeCangrejos(deepcopy(self._juego._descarte[pilaDeDescarteARobar]))
				
				self._eventos.append(Evento(self._juego.deQuiénEsTurno, acciónDeDúos,
					{
						"cartasJugadas": deepcopy(sorted(cartasAJugar.elements())),
						"pilaDondeRobó": pilaDeDescarteARobar
					}
				))
				
				cartaRobada = self._juego.jugarDúoDeCangrejos(cartasAJugar, pilaDeDescarteARobar, indiceDeCartaARobar)
				if self._verbosidad == AdministradorDeJuego.Verbosidad.OMNISCIENTE:
					print(f"Juega un dúo de {list(cartasAJugar.elements())[0]} y {list(cartasAJugar.elements())[1]} para robar una {cartaRobada} de la pila {pilaDeDescarteARobar}")
				elif self._verbosidad == AdministradorDeJuego.Verbosidad.JUGADOR:
					print(f"Juega un dúo de {list(cartasAJugar.elements())[0]} y {list(cartasAJugar.elements())[1]} para robar una carta de la pila {pilaDeDescarteARobar}")
				
			elif acciónDeDúos == Acción.Dúos.JUGAR_NADADOR_Y_TIBURÓN:
				# Jugar dúo de nadador y tiburón
				jugadorARobar = parametrosDelDúo[0]
				cartaRobada = self._juego.jugarDúoDeNadadorYTiburón(cartasAJugar, jugadorARobar)
				
				self._eventos.append(Evento(self._juego.deQuiénEsTurno, acciónDeDúos,
					{
						"cartasJugadas": deepcopy(sorted(cartasAJugar.elements())),
						"jugadorRobado": jugadorARobar,
						"cartaRobada": cartaRobada # ! SOLO VER SI FUISTE EL JUGADOR ROBADO!!!
					}
				))
				if self._verbosidad == AdministradorDeJuego.Verbosidad.OMNISCIENTE:
					print(f"Juega un dúo de {list(cartasAJugar.elements())[0]} y {list(cartasAJugar.elements())[1]} para robarle al jugador {jugadorARobar}, y roba una {cartaRobada}")
				elif self._verbosidad == AdministradorDeJuego.Verbosidad.JUGADOR:
					print(f"Juega un dúo de {list(cartasAJugar.elements())[0]} y {list(cartasAJugar.elements())[1]} para robarle al jugador {jugadorARobar}")
				
			elif acciónDeDúos == Acción.Dúos.NO_JUGAR:
				# No jugar dúos
				noSeQuierenJugarMásDúos = True
				
			else:
				#! ERROR
				raise Exception("Error")

	def _faseDeFin(self):
		if not self._juego.haTerminado() and self._juego.rondaEnCurso():
			acciónDeFinDeTurno = self._jugadores[self._juego.deQuiénEsTurno].decidirAcciónDeFinDeTurno()
			self._eventos.append(Evento(self._juego.deQuiénEsTurno, acciónDeFinDeTurno, None))
			
			if acciónDeFinDeTurno == Acción.FinDeTurno.PASAR_TURNO:
				# Pasar el turno normalmente				
				self._juego.pasarTurno()
				if self._verbosidad != AdministradorDeJuego.Verbosidad.NADA:
					print("Pasa de turno")
			elif acciónDeFinDeTurno == Acción.FinDeTurno.DECIR_BASTA:
				# Decir basta y terminar la ronda
				self._juego.decirBasta()
				if self._verbosidad != AdministradorDeJuego.Verbosidad.NADA:
					print("¡¡¡Basta!!!")
			elif acciónDeFinDeTurno == Acción.FinDeTurno.DECIR_ÚLTIMA_CHANCE:
				# Decir última chance y pasar el turno
				self._juego.decirÚltimaChance()
				if self._verbosidad != AdministradorDeJuego.Verbosidad.NADA:
					print("¡¡¡Última Chance!!!")
			else:
				#! ERROR
				raise Exception("Error")
	
	def _finDeRonda(self):
		self._rondasTerminadas += 1
		if max(self._juego.puntajes) == SIRENAS_INF:
			self._motivosFinDeRonda["4_SIRENAS"] += 1
			self._motivosFinDeRondaPorJugador[self._juego.jugadorGanador]["4_SIRENAS"] += 1
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
			for j in range(len(self._jugadores)):
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
				self._motivosFinDeRondaPorJugador[self._juego.jugadorQueDijoÚltimaChance]["ÚLTIMA_CHANCE_GANADA"] += 1
			else:
				self._motivosFinDeRondaPorJugador[self._juego.jugadorQueDijoÚltimaChance]["ÚLTIMA_CHANCE_PERDIDA"] += 1
			for j in range(len(self._jugadores)):
				if self._juego.últimaChanceGanada():
					if j == self._juego.jugadorQueDijoÚltimaChance:
						self._puntosPorJugadorPorRonda[j].append(self._juego._estadosDeJugadores[j].puntajeDeRonda() + self._juego._estadosDeJugadores[j]._bonificacionPorColor())
					else:
						self._puntosPorJugadorPorRonda[j].append(self._juego._estadosDeJugadores[j]._bonificacionPorColor())
				else:
					if j == self._juego.jugadorQueDijoÚltimaChance:
						self._puntosPorJugadorPorRonda[j].append(self._juego._estadosDeJugadores[j]._bonificacionPorColor())
					else:
						self._puntosPorJugadorPorRonda[j].append(self._juego._estadosDeJugadores[j].puntajeDeRonda())
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
			self._motivosFinDeRondaPorJugador[(self._juego.deQuiénEsTurno - 1) % self._juego.cantidadDeJugadores]["BASTA"] += 1
			for j in range(len(self._jugadores)):
				self._puntosPorJugadorPorRonda[j].append(self._juego._estadosDeJugadores[j].puntajeDeRonda())
			if self._verbosidad != AdministradorDeJuego.Verbosidad.NADA:
				print("*************** Ronda terminada por basta ***************")
				for j in range(self._juego.cantidadDeJugadores):
					print(f"Jugador {j}: +{self._juego._estadosDeJugadores[j].puntajeDeRonda()} ({self._juego.puntajes[j]}/{self._juego.puntajeParaGanar})")					
				print("*********************************************************")
		
		if self._verbosidad != self.Verbosidad.NADA:
			for j in range(len(self._jugadores)):
				print(f"Mano del jugador {j}:\n{self._juego._estadosDeJugadores[j].mano}")
				print(f"zona de dúos del jugador {j}:\n{self._juego._estadosDeJugadores[j].zonaDeDúos}\n")
		
		self._calcularEstadísticasDeRonda()
		
		quiénArranca = self._juego._deQuiénEsTurno
		manos = [deepcopy(self._juego._estadosDeJugadores[j].mano) for j in range(len(self._jugadores))]
		puntajesDeRonda = [ int(self._juego._estadosDeJugadores[j].puntajeDeRonda()) for j in range(len(self._jugadores))]
		for j in range(len(self._jugadores)):
			self._juego._deQuiénEsTurno = j
			self._jugadores[j].configurarFinDeRonda(manos, puntajesDeRonda)
		self._juego._deQuiénEsTurno = quiénArranca
		
		self._eventos.clear()
	
	def _calcularEstadísticasDeRonda(self):
		for j in range(len(self._jugadores)):
			# Cálculos auxiliares...
			cantidadDeCartasEnManoDeTipo = {tipo: 0 for tipo in Carta.Tipo}
			cantidadDeCartasEnZonaDeDúosDeTipo = {tipo: 0 for tipo in Carta.Tipo}
			cantidadDeDúosEnJuegoDeTipo = {
				Carta.Tipo.PEZ: 0,
				Carta.Tipo.BARCO: 0,
				Carta.Tipo.CANGREJO: 0,
				Carta.Tipo.NADADOR: 0    # noo maldito enum que no me deja poner nombres declarativos!
			}
			
			for claveDeCarta in self._juego._estadosDeJugadores[j].mano:
				cantidadDeCartasEnManoDeTipo[claveDeCarta.tipo] += self._juego._estadosDeJugadores[j].mano[claveDeCarta]
			
			for claveDeDúo in self._juego._estadosDeJugadores[j].zonaDeDúos:
				cantidadDeDúosEnJuegoDeTipo[claveDeDúo[0].tipo] += self._juego._estadosDeJugadores[j].zonaDeDúos[claveDeDúo]
				cantidadDeCartasEnZonaDeDúosDeTipo[claveDeDúo[0].tipo] += self._juego._estadosDeJugadores[j].zonaDeDúos[claveDeDúo]
				cantidadDeCartasEnZonaDeDúosDeTipo[claveDeDúo[1].tipo] += self._juego._estadosDeJugadores[j].zonaDeDúos[claveDeDúo]
			
			
			# Calcular dúos en juego del jugador en esta ronda
			for tipoDúo in [Carta.Tipo.PEZ, Carta.Tipo.BARCO, Carta.Tipo.CANGREJO, Carta.Tipo.NADADOR]:
				self._dúosJugadosPorJugadorPorTipo[j][tipoDúo] += cantidadDeDúosEnJuegoDeTipo[tipoDúo]
			
			# Calcular dúos en mano del jugador en esta ronda
			self._dúosEnManoPorJugadorPorTipo[j][Carta.Tipo.PEZ] += cantidadDeCartasEnManoDeTipo[Carta.Tipo.PEZ] // 2
			self._dúosEnManoPorJugadorPorTipo[j][Carta.Tipo.BARCO] += cantidadDeCartasEnManoDeTipo[Carta.Tipo.BARCO] // 2
			self._dúosEnManoPorJugadorPorTipo[j][Carta.Tipo.CANGREJO] += cantidadDeCartasEnManoDeTipo[Carta.Tipo.CANGREJO] // 2
			self._dúosEnManoPorJugadorPorTipo[j][Carta.Tipo.NADADOR] += min(cantidadDeCartasEnManoDeTipo[Carta.Tipo.NADADOR], cantidadDeCartasEnManoDeTipo[Carta.Tipo.TIBURÓN])
			
			# Calcular cartas poseídas de cada tipo en esta ronda
			for tipo in Carta.Tipo:
				self._cantidadDeCartasPorJugadorPorTipo[j][tipo] += cantidadDeCartasEnManoDeTipo[tipo] + cantidadDeCartasEnZonaDeDúosDeTipo[tipo]
	
if __name__ == '__main__':
	administrador = AdministradorDeJuego([PuntosBotMk2, JugadorCLI], verbosidad=AdministradorDeJuego.Verbosidad.JUGADOR)
	ganador = administrador.jugarPartida()
	print(f"Ganador: {ganador}")
