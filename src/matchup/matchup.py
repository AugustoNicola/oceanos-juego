import matplotlib.pyplot as plt
import numpy as np
from juego.carta import Carta, apodosCartas
from jugador.RandyBot.randy import RandyBot
from jugador.PuntosBot.puntosbot_mk1 import PuntosBotMk1
from jugador.PuntosBot.puntosbot_mk2 import PuntosBotMk2
from jugador.SirenaTeam.sirena_enjoyer import SirenaEnjoyer
from jugador.SirenaTeam.sirena_hater import SirenaHater
from administrador.administrador_de_juego import AdministradorDeJuego

#* vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
#* vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
#* vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
#* vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
#* vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
_jugadoresDelMatchup = [
	PuntosBotMk2,
	PuntosBotMk1
]
_nombres = [
	"MK2",
	"MK1"
]
_cantidadDePartidasAJugar = 600
#* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

class Matchup():
	def __init__(self, jugadoresDelMatchup, nombres):
		self.jugadoresDelMatchup = jugadoresDelMatchup
		self.nombres = nombres
		self.administrador = AdministradorDeJuego(
			jugadoresDelMatchup,
			verbosidad=AdministradorDeJuego.Verbosidad.NADA
		)
		
	def simular(self, cantidadDePartidasAJugar):
		# =================================================== ¡¡¡¡¡MATCHUP!!!!! ===================================================
		cantidadJugadores = len(self.jugadoresDelMatchup)
		
		for decimo in range(1, 11):
			for _ in range(cantidadDePartidasAJugar // 10):
				self.administrador.jugarPartida()
			print(f"{decimo * 10}% de las {cantidadDePartidasAJugar} partidas disputadas{'...' if decimo < 10 else '!'}")
		
		# ======================================================== GANADOR ========================================================
		ganador = np.argmax(self.administrador._partidasGanadasPorJugador)
		print("EL GANADOR ES...")
		print("v" * 119)
		print("v" * 119)
		print("v" * 119)
		print("v" * 119)
		print("v" * 119)
		print((">" * ((117 - len(self.nombres[ganador])) // 2)) + " " + self.nombres[ganador] + " " + ("<" * ((117 - len(self.nombres[ganador])) // 2 + int(len(self.nombres[ganador]) % 2 == 0 ))))
		print("^" * 119)
		print("^" * 119)
		print("^" * 119)
		print("^" * 119)
		print("^" * 119)
		
		
		# =============================================== Preprocesamiento de datos ===============================================
		for j in range(cantidadJugadores):
			for e in self.administrador._dúosJugadosPorJugadorPorTipo[j]:
				self.administrador._dúosJugadosPorJugadorPorTipo[j][e] = self.administrador._dúosJugadosPorJugadorPorTipo[j][e] / self.administrador._rondasTerminadas
			
			for e in self.administrador._dúosEnManoPorJugadorPorTipo[j]:
				self.administrador._dúosEnManoPorJugadorPorTipo[j][e] = self.administrador._dúosEnManoPorJugadorPorTipo[j][e] / self.administrador._rondasTerminadas
			
			for e in self.administrador._cantidadDeCartasPorJugadorPorTipo[j]:
				self.administrador._cantidadDeCartasPorJugadorPorTipo[j][e] = self.administrador._cantidadDeCartasPorJugadorPorTipo[j][e] / self.administrador._rondasTerminadas
	
	def _graficar(self):
		cantidadJugadores = len(self.jugadoresDelMatchup)
		
		# =================================================== Preparación Gráficos ===================================================
		fig, ((ax_motivosFinDeRonda, ax_partidasGanadas, ax_puntosPorJugador), (ax_motivosFinDeRondaJugadorCero, ax_motivosFinDeRondaJugadorUno, ax_dúosPorRonda), (ax_motivosFinDeRondaJugadorDos, ax_motivosFinDeRondaJugadorTres, ax_cartasPorTipo)) = plt.subplots(3, 3)
		fig.suptitle('Estadísticas del Matchup')
		fig.tight_layout()
		
		colors = ['red', 'mediumseagreen', 'cornflowerblue', 'purple']
		colors2 = ['orange', 'lime', 'darkturquoise', 'violet']
		labelsMotivosFinDeRonda = ["Mazo vacío", "Basta", "Cuatro sirenas", "Última chance"]
		coloresMotivosFinDeRonda = ["lightsteelblue", "tan", "lightgrey", "deeppink"]
		labelsMotivosFinDeRondaPorJugador = ["Basta", "Última chance ganada", "Última chance perdida", "Cuatro sirenas"]
		coloresMotivosFinDeRondaPorJugador = ["tan", "seagreen", "orangered", "lightgrey"]
		labelsPartidasGanadas = self.nombres
		labelsDúos = ['Peces', 'Barcos', 'Cangrejos', 'Ndrs&Tbns']
		labelsTiposCartas = [ apodosCartas[t] for t in Carta.Tipo ]
		width = None
		preOff = None
		if cantidadJugadores == 2:
			width = 0.25
			preOff = 0.125
		elif cantidadJugadores == 3:
			width = 0.25
			preOff = 0.05
		elif cantidadJugadores == 4:
			width = 0.20
			preOff = 0.025
		
		# =================================================== Motivos Fin de Ronda ===================================================
		my_pie, texts, pct_txts = ax_motivosFinDeRonda.pie(self.administrador._motivosFinDeRonda.values(), labels=labelsMotivosFinDeRonda, autopct='%1.1f%%', colors=coloresMotivosFinDeRonda)
		ax_motivosFinDeRonda.title.set_text("Motivos Fin de Ronda")
		
		# ================================================= Distribución de Victorias ================================================
		ax_partidasGanadas.pie(self.administrador._partidasGanadasPorJugador, labels=labelsPartidasGanadas, autopct='%1.1f%%', colors=colors)
		ax_partidasGanadas.title.set_text("Distribución de Victorias")
		
		# ============================================== Distribución de Puntos por Ronda ============================================
		for j in range(cantidadJugadores):
			counts, bins = np.histogram(self.administrador._puntosPorJugadorPorRonda[j], bins=np.arange(20))
			ax_puntosPorJugador.stairs(counts, bins, color=colors[j])
		ax_puntosPorJugador.title.set_text("Distribución de Puntos por Ronda")
		
		# ============================================ Motivos Fin de Ronda (Por Jugador) ============================================
		ax_motivosFinDeRondaJugadorCero.pie(self.administrador._motivosFinDeRondaPorJugador[0].values(), labels=labelsMotivosFinDeRondaPorJugador, autopct='%1.1f%%', colors=coloresMotivosFinDeRondaPorJugador)
		ax_motivosFinDeRondaJugadorCero.title.set_text(f"Motivos Fin de Ronda ({self.nombres[0]})")
		
		
		if max(self.administrador._motivosFinDeRondaPorJugador[1].values()) > 0:
			ax_motivosFinDeRondaJugadorUno.pie(self.administrador._motivosFinDeRondaPorJugador[1].values(), labels=labelsMotivosFinDeRondaPorJugador, autopct='%1.1f%%', colors=coloresMotivosFinDeRondaPorJugador)
			ax_motivosFinDeRondaJugadorUno.title.set_text(f"Motivos Fin de Ronda ({self.nombres[1]})")
		else:
			ax_motivosFinDeRondaJugadorUno.text(0.5, 0.5, "No disponible", ha="center", va="center", transform=ax_motivosFinDeRondaJugadorUno.transAxes)
			ax_motivosFinDeRondaJugadorUno.set_xticks([])
			ax_motivosFinDeRondaJugadorUno.set_yticks([])
			ax_motivosFinDeRondaJugadorUno.spines['top'].set_visible(False)
			ax_motivosFinDeRondaJugadorUno.spines['right'].set_visible(False)
			ax_motivosFinDeRondaJugadorUno.spines['bottom'].set_visible(False)
			ax_motivosFinDeRondaJugadorUno.spines['left'].set_visible(False)
			ax_motivosFinDeRondaJugadorUno.title.set_text(f"Motivos Fin de Ronda ({self.nombres[1]})")
		
		
		if cantidadJugadores >= 3 and max(self.administrador._motivosFinDeRondaPorJugador[2].values()) > 0:
			ax_motivosFinDeRondaJugadorDos.pie(self.administrador._motivosFinDeRondaPorJugador[2].values(), labels=labelsMotivosFinDeRondaPorJugador, autopct='%1.1f%%', colors=coloresMotivosFinDeRondaPorJugador)
			ax_motivosFinDeRondaJugadorDos.title.set_text(f"Motivos Fin de Ronda ({self.nombres[2]})")
		else:
			ax_motivosFinDeRondaJugadorDos.text(0.5, 0.5, "No disponible", ha="center", va="center", transform=ax_motivosFinDeRondaJugadorDos.transAxes)
			ax_motivosFinDeRondaJugadorDos.set_xticks([])
			ax_motivosFinDeRondaJugadorDos.set_yticks([])
			ax_motivosFinDeRondaJugadorDos.spines['top'].set_visible(False)
			ax_motivosFinDeRondaJugadorDos.spines['right'].set_visible(False)
			ax_motivosFinDeRondaJugadorDos.spines['bottom'].set_visible(False)
			ax_motivosFinDeRondaJugadorDos.spines['left'].set_visible(False)
			ax_motivosFinDeRondaJugadorDos.title.set_text(f"Motivos Fin de Ronda (Jugador 2)")
		
		if cantidadJugadores == 4 and max(self.administrador._motivosFinDeRondaPorJugador[3].values()) > 0:
			ax_motivosFinDeRondaJugadorTres.pie(self.administrador._motivosFinDeRondaPorJugador[3].values(), labels=labelsMotivosFinDeRondaPorJugador, autopct='%1.1f%%', colors=coloresMotivosFinDeRondaPorJugador)
			ax_motivosFinDeRondaJugadorTres.title.set_text(f"Motivos Fin de Ronda ({self.nombres[3]})")
		else:
			ax_motivosFinDeRondaJugadorTres.text(0.5, 0.5, "No disponible", ha="center", va="center", transform=ax_motivosFinDeRondaJugadorTres.transAxes)
			ax_motivosFinDeRondaJugadorTres.set_xticks([])
			ax_motivosFinDeRondaJugadorTres.set_yticks([])
			ax_motivosFinDeRondaJugadorTres.spines['top'].set_visible(False)
			ax_motivosFinDeRondaJugadorTres.spines['right'].set_visible(False)
			ax_motivosFinDeRondaJugadorTres.spines['bottom'].set_visible(False)
			ax_motivosFinDeRondaJugadorTres.spines['left'].set_visible(False)
			ax_motivosFinDeRondaJugadorTres.title.set_text(f"Motivos Fin de Ronda (Jugador 3)")
		
		# ============================================ Promedio de Dúos Jugados por Ronda ============================================
		x = np.arange(len(labelsDúos))
		
		for j in range(cantidadJugadores):
			multiplier = j
			attribute = f"Jugador {j}"
			measurement = self.administrador._dúosJugadosPorJugadorPorTipo[j].values()
			#print(attribute)
			#print(measurement)
			offset = width * multiplier
			rects = ax_dúosPorRonda.bar(x + offset, measurement, width, label=attribute, color=colors[j])
			ax_dúosPorRonda.bar_label(rects, label_type="center", fmt="{:.2f}")
		for j in range(cantidadJugadores):
			multiplier = j
			attribute = f"Jugador {j}"
			measurement = self.administrador._dúosEnManoPorJugadorPorTipo[j].values()
			#print(attribute)
			#print(measurement)
			offset = width * multiplier
			#print(list(self.administrador._dúosJugadosPorJugadorPorTipo[j].values()))
			rects = ax_dúosPorRonda.bar(x + offset, measurement, width, label=attribute, bottom=list(self.administrador._dúosJugadosPorJugadorPorTipo[j].values()), color=colors2[j], hatch='//')
			ax_dúosPorRonda.bar_label(rects, label_type="center", fmt="{:.2f}")
		ax_dúosPorRonda.set_title('Promedio de Dúos Jugados por Ronda')
		ax_dúosPorRonda.set_xticks(x + width - preOff, labelsDúos)
		
		# =============================================== Promedio de Cartas por Ronda ===============================================
		x = np.arange(len(labelsTiposCartas))
		
		for j in range(cantidadJugadores):
			multiplier = j
			attribute = f"Jugador {j}"
			measurement = self.administrador._cantidadDeCartasPorJugadorPorTipo[j].values()
			#print(attribute)
			#print(measurement)
			offset = width * multiplier
			rects = ax_cartasPorTipo.bar(x + offset, measurement, width, label=attribute, color=colors[j])
			#ax_cartasPorTipo.bar_label(rects, label_type="center")
		
		ax_cartasPorTipo.set_title('Promedio de Cartas por Ronda')
		ax_cartasPorTipo.set_xticks(x + width - preOff, labelsTiposCartas)
		#ax_cartasPorTipo.legend(loc='upper left', ncols=3)
		
		# ===================================================== Mostrar Gráficos =====================================================
		return fig
	
	def mostrarGráficos(self):
		fig = self._graficar()
		plt.show()
	
	def guardarGráficos(self, nombreDelArchivo):
		fig = self._graficar()
		fig.set_size_inches(18, 10)
		fig.set_dpi(600)
		plt.savefig(nombreDelArchivo + '.jpg', format='jpg')

if __name__ == '__main__':
	simulador = Matchup(_jugadoresDelMatchup, _nombres)
	simulador.simular(_cantidadDePartidasAJugar)
	simulador.mostrarGráficos()