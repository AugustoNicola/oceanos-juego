from matchup.matchup import Matchup
from itertools import product
from jugador.PuntosBot.puntosbot_mk1 import PuntosBotMk1
from jugador.PuntosBot.puntosbot_mk2 import PuntosBotMk2
from jugador.RandyBot.randy import RandyBot
from time import time
import os.path

# supongo 2 partidas/seg, tengo 50k partidas en 7hrs
# son 64 casos de prueba, cada uno corre N*2 partidas
# pongo N = 370 y me sobra (debería ser N = 390.625)

CANTIDAD_DE_PARTIDAS_POR_LADO_VS_MK1 = 400
#CANTIDAD_DE_PARTIDAS_POR_LADO_VS_RANDY = 20

## Primer experimento (re-done)
#valores_BONUS_MULTIPLICADOR_OBTENIDO = [1.0, 3.0]
#valores_OBTENER_MULTIPLICADOR = [0.0, 1.0]
#valores_ARRANCAR_COLECCIONABLE =  [1.0, 3.0]
#valores_VALOR_BASE_PRIMER_CARTA_DUO = [1.0, 3.0]
#valores_BONUS_COMPLETAR_DUO = [3.0, 6.0]
#valores_VALOR_BASE_SIRENA = [10.0, 15.0]


## Segundo experimento (nuevo)
valores_BONUS_MULTIPLICADOR_OBTENIDO = [2.0,3.0]
valores_OBTENER_MULTIPLICADOR = [0.0,0.5,1.0]
valores_ARRANCAR_COLECCIONABLE =  [0.5,1.0,1.5,2.0,2.5,3.0]
valores_VALOR_BASE_PRIMER_CARTA_DUO = [1.0]
valores_BONUS_COMPLETAR_DUO = [3.0,4.0,5.0]
valores_VALOR_BASE_SIRENA = [0.0]


combinacionesTotales = (
	len(valores_BONUS_MULTIPLICADOR_OBTENIDO) * 
	len(valores_OBTENER_MULTIPLICADOR) * 
	len(valores_ARRANCAR_COLECCIONABLE) * 
	len(valores_VALOR_BASE_PRIMER_CARTA_DUO) * 
	len(valores_BONUS_COMPLETAR_DUO) * 
	len(valores_VALOR_BASE_SIRENA)
)
índiceCombinacion = 0

mejorWinrate = -1.0
mejorConfiguracion = None


with open("../../../Desktop/Matchups/MK2/winrates.txt", "a") as file:
	file.write(f"========== nuevo experimento ===========\n")

tiempo_inicial_explorador = time()
for configuracion in product(
	valores_BONUS_MULTIPLICADOR_OBTENIDO,
	valores_OBTENER_MULTIPLICADOR,
	valores_ARRANCAR_COLECCIONABLE,
	valores_VALOR_BASE_PRIMER_CARTA_DUO,
	valores_BONUS_COMPLETAR_DUO,
	valores_VALOR_BASE_SIRENA
):
	índiceCombinacion += 1
	if os.path.isfile(f"../../../Desktop/Matchups/MK2/mk2vsmk1/MK2_vs_MK1-BO_MULT_OBT_{configuracion[0]}-OBT_MULT_{configuracion[1]}-ARR_COL_{configuracion[2]}-BA_PRI_DUO_{configuracion[3]}-BO_COMP_DUO_{configuracion[4]}-BA_SNA_{configuracion[5]}.jpg"):
		print(f"skip iteración {índiceCombinacion}...")
		continue

	print(f"Probando combinación {índiceCombinacion}/{combinacionesTotales}...")
	
	tiempo_inicial_configuracion = time()
	
	logréCorrerExperimento1 = False
	logréCorrerExperimento2 = False
	simuladorMK1_1 = None
	simuladorMK1_2 = None
	
	with open("configuracion_mk2.txt", "w") as configfile:
		configfile.write(f"BONUS_MULTIPLICADOR_OBTENIDO = {configuracion[0]}\n")
		configfile.write(f"ARRANCAR_COLECCIONABLE = {configuracion[1]}\n")
		configfile.write(f"OBTENER_MULTIPLICADOR = {configuracion[2]}\n")
		configfile.write(f"VALOR_BASE_PRIMER_CARTA_DUO = {configuracion[3]}\n")
		configfile.write(f"BONUS_COMPLETAR_DUO = {configuracion[4]}\n")
		configfile.write(f"VALOR_BASE_SIRENA = 1{configuracion[5]}\n")
	
	while not logréCorrerExperimento1:
		try:
			simuladorMK1_1 = Matchup([PuntosBotMk1, PuntosBotMk2], ["MK1", "MK2"])
			simuladorMK1_1.simular(CANTIDAD_DE_PARTIDAS_POR_LADO_VS_MK1)
			simuladorMK1_1.guardarGráficos(f"../../../Desktop/Matchups/MK2/mk1vsmk2/MK1_vs_MK2-BO_MULT_OBT_{configuracion[0]}-OBT_MULT_{configuracion[1]}-ARR_COL_{configuracion[2]}-BA_PRI_DUO_{configuracion[3]}-BO_COMP_DUO_{configuracion[4]}-BA_SNA_{configuracion[5]}.jpg")
			logréCorrerExperimento1 = True
		except Exception:
			print("Tuvimos una excepción jugando! Reintentando...")
	
	while not logréCorrerExperimento2:
		try:
			simuladorMK1_2 = Matchup([PuntosBotMk2, PuntosBotMk1], ["MK2", "MK1"])
			simuladorMK1_2.simular(CANTIDAD_DE_PARTIDAS_POR_LADO_VS_MK1)
			simuladorMK1_2.guardarGráficos(f"../../../Desktop/Matchups/MK2/mk2vsmk1/MK2_vs_MK1-BO_MULT_OBT_{configuracion[0]}-OBT_MULT_{configuracion[1]}-ARR_COL_{configuracion[2]}-BA_PRI_DUO_{configuracion[3]}-BO_COMP_DUO_{configuracion[4]}-BA_SNA_{configuracion[5]}.jpg")
			logréCorrerExperimento2 = True
		except Exception:
			print("Tuvimos una excepción jugando! Reintentando...")
	
	#simuladorRANDY_1 = Matchup([RandyBot, PuntosBotMk2], ["RANDY", "MK2"])
	#simuladorRANDY_1.simular(CANTIDAD_DE_PARTIDAS_POR_LADO_VS_RANDY)
	#simuladorRANDY_1.guardarGráficos(f"explorador/imgs/RANDY_vs_MK2-BONUS_MULTIPLICADOR_OBTENIDO_{configuracion[0]}-OBTENER_MULTIPLICADOR_{configuracion[1]}-ARRANCAR_COLECCIONABLE_{configuracion[2]}-VALOR_BASE_PRIMER_CARTA_DUO_{configuracion[3]}-BONUS_COMPLETAR_DUO_{configuracion[4]}-VALOR_BASE_SIRENA_{configuracion[5]}")
	
	#simuladorRANDY_2 = Matchup([PuntosBotMk2, RandyBot], ["MK2", "RANDY"])
	#simuladorRANDY_2.simular(CANTIDAD_DE_PARTIDAS_POR_LADO_VS_RANDY)
	#simuladorRANDY_2.guardarGráficos(f"explorador/imgs/MK2_vs_RANDY-BONUS_MULTIPLICADOR_OBTENIDO_{configuracion[0]}-OBTENER_MULTIPLICADOR_{configuracion[1]}-ARRANCAR_COLECCIONABLE_{configuracion[2]}-VALOR_BASE_PRIMER_CARTA_DUO_{configuracion[3]}-BONUS_COMPLETAR_DUO_{configuracion[4]}-VALOR_BASE_SIRENA_{configuracion[5]}")
	
	winRate = (
		simuladorMK1_1.administrador._partidasGanadasPorJugador[1]
		+ simuladorMK1_2.administrador._partidasGanadasPorJugador[0]
	) * 100.0 / (CANTIDAD_DE_PARTIDAS_POR_LADO_VS_MK1 * 2.0)
	
	if winRate > mejorWinrate:
		mejorWinrate = winRate
		mejorConfiguracion = configuracion
	
	with open("../../../Desktop/Matchups/MK2/winrates.txt", "a") as file:
		file.write(f"{configuracion}: {winRate:.2f}\n")
	
	print(f"Experimento terminado en {time() - tiempo_inicial_configuracion :.2f}segs, winrate obtenido de {winRate:.3f}%")
print(f"Exploración total terminada en {time() - tiempo_inicial_explorador :.2f}segs")
	

print(f"Mejor winrate: {mejorWinrate:.2f}%")
print(f"BONUS_MULTIPLICADOR_OBTENIDO: {mejorConfiguracion[0]}")
print(f"OBTENER_MULTIPLICADOR: {mejorConfiguracion[1]}")
print(f"ARRANCAR_COLECCIONABLE: {mejorConfiguracion[2]}")
print(f"VALOR_BASE_PRIMER_CARTA_DUO: {mejorConfiguracion[3]}")
print(f"BONUS_COMPLETAR_DUO: {mejorConfiguracion[4]}")
print(f"VALOR_BASE_SIRENA: {mejorConfiguracion[5]}")
