from copy import deepcopy

class Evento:
	def __init__(self, jugador, acción, parámetros):
		self._jugador = jugador
		self._acción = acción
		self._parámetros = parámetros
	
	@property
	def jugador(self):
		return int(self._jugador)
	
	@property
	def acción(self):
		return deepcopy(self._acción)
	
	@property
	def parámetros(self):
		return deepcopy(self._parámetros)
	
	def __str__(self):
		return f"({self._jugador}, {self._acción}, {self._parámetros})"
	
	def __repr__(self):
		return f"({self._jugador}, {self._acción}, {self._parámetros})"
	
	def aDiccionario(self):
		return {
			"jugador": self._jugador,
			"acción": self._acción.value,
			"parámetros": self._parámetros
		}