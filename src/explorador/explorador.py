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
#valores_COEF_MULTIPLICADOR_OBTENIDO = [1.0, 3.0]
#valores_PLUS_OBTENER_MULTIPLICADOR = [0.0, 1.0]
#valores_COEF_ARRANCAR_COLECCIONABLE =  [1.0, 3.0]
#valores_VALOR_BASE_PRIMER_CARTA_DUO = [1.0, 3.0]
#valores_COEF_COMPLETAR_DUO = [3.0, 6.0]
#valores_PLUS_SIRENA = [10.0, 15.0]


## Segundo experimento (nuevo)
#valores_COEF_MULTIPLICADOR_OBTENIDO = [2.0,3.0]
#valores_PLUS_OBTENER_MULTIPLICADOR = [0.0,0.5,1.0]
#valores_COEF_ARRANCAR_COLECCIONABLE =  [0.5,1.0,1.5,2.0,2.5,3.0]
#valores_VALOR_BASE_PRIMER_CARTA_DUO = [1.0]
#valores_COEF_COMPLETAR_DUO = [3.0,4.0,5.0]
#valores_PLUS_SIRENA = [0.0]


## Tercer experimento (priemra vez que le ganamos a MK1)
valores_COEF_MULTIPLICADOR_OBTENIDO = [1.0]
valores_PLUS_OBTENER_MULTIPLICADOR = [0.0]
valores_COEF_ARRANCAR_COLECCIONABLE = [1.0]
#*valores_VALOR_BASE_PRIMER_CARTA_DUO = [0.0]
valores_COEF_COMPLETAR_DUO = [1.0]
valores_PLUS_SIRENA = [0.0]
valores_COEF_SEGUIR_COLECCIONABLE = [1.0]
valores_PLUS_PRIMER_PEZ = [0.005, 0.01, 0.02]
valores_PLUS_PRIMER_BARCO = [0.015, 0.03, 0.06]
valores_PLUS_PRIMER_CANGREJO = [0.03, 0.06, 0.12]
valores_PLUS_PRIMER_NADADORTIBURÓN = [0.04, 0.08, 0.16]


combinacionesTotales = (
	len(valores_COEF_MULTIPLICADOR_OBTENIDO) * 
	len(valores_PLUS_OBTENER_MULTIPLICADOR) * 
	len(valores_COEF_ARRANCAR_COLECCIONABLE) * 
	len(valores_COEF_COMPLETAR_DUO) * 
	len(valores_PLUS_SIRENA) *
	len(valores_COEF_SEGUIR_COLECCIONABLE) *
	len(valores_PLUS_PRIMER_PEZ) * 
	len(valores_PLUS_PRIMER_BARCO) * 
	len(valores_PLUS_PRIMER_CANGREJO) * 
	len(valores_PLUS_PRIMER_NADADORTIBURÓN)
)
índiceCombinacion = 0

mejorWinrate = -1.0
mejorConfiguracion = None


with open("../../../Desktop/Matchups/MK2/winrates.txt", "a") as file:
	file.write(f"========== nuevo experimento ===========\n")

tiempo_inicial_explorador = time()
for configuracion in product(
	valores_COEF_MULTIPLICADOR_OBTENIDO,
	valores_PLUS_OBTENER_MULTIPLICADOR,
	valores_COEF_ARRANCAR_COLECCIONABLE,
	valores_COEF_COMPLETAR_DUO,
	valores_PLUS_SIRENA,
	valores_COEF_SEGUIR_COLECCIONABLE,
	valores_PLUS_PRIMER_PEZ,
	valores_PLUS_PRIMER_BARCO,
	valores_PLUS_PRIMER_CANGREJO,
	valores_PLUS_PRIMER_NADADORTIBURÓN
):
	índiceCombinacion += 1
	nombreFile = f"C_MULT_OBT_{configuracion[0]}-P_OBT_MULT_{configuracion[1]}-C_ARR_COL_{configuracion[2]}-C_COMP_DUO_{configuracion[3]}-P_SNA_{configuracion[4]}-C_SEG_COL_{configuracion[5]}-P_PRI_PEZ_{configuracion[6]}-P_PRI_BCO_{configuracion[7]}-P_PRI_CJO_{configuracion[8]}-P_PRI_NYT_{configuracion[9]}"
	
	if os.path.isfile(f"../../../Desktop/Matchups/MK2/mk2vsmk1/MK2_vs_MK1-{nombreFile}.jpg"):
		print(f"skip iteración {índiceCombinacion}...")
		continue

	print(f"Probando combinación {índiceCombinacion}/{combinacionesTotales}...")
	
	tiempo_inicial_configuracion = time()
	
	logréCorrerExperimento1 = False
	logréCorrerExperimento2 = False
	simuladorMK1_1 = None
	simuladorMK1_2 = None
	
	with open("configuracion_mk2.txt", "w") as configfile:
		configfile.write(f"COEF_MULTIPLICADOR_OBTENIDO = {configuracion[0]}\n")
		configfile.write(f"PLUS_OBTENER_MULTIPLICADOR = {configuracion[1]}\n")
		configfile.write(f"COEF_ARRANCAR_COLECCIONABLE = {configuracion[2]}\n")
		configfile.write(f"COEF_COMPLETAR_DUO = {configuracion[3]}\n")
		configfile.write(f"PLUS_SIRENA = {configuracion[4]}\n")
		configfile.write(f"COEF_SEGUIR_COLECCIONABLE = {configuracion[5]}\n")
		configfile.write(f"PLUS_PRIMER_PEZ = {configuracion[6]}\n")
		configfile.write(f"PLUS_PRIMER_BARCO = {configuracion[7]}\n")
		configfile.write(f"PLUS_PRIMER_CANGREJO = {configuracion[8]}\n")
		configfile.write(f"PLUS_PRIMER_NADADORTIBURON = {configuracion[9]}\n")
	
	while not logréCorrerExperimento1:
		try:
			simuladorMK1_1 = Matchup([PuntosBotMk1, PuntosBotMk2], ["MK1", "MK2"])
			simuladorMK1_1.simular(CANTIDAD_DE_PARTIDAS_POR_LADO_VS_MK1)
			simuladorMK1_1.guardarGráficos(f"../../../Desktop/Matchups/MK2/mk1vsmk2/MK1_vs_MK2-{nombreFile}.jpg")
			logréCorrerExperimento1 = True
		except Exception:
			print("Tuvimos una excepción jugando! Reintentando...")
	
	while not logréCorrerExperimento2:
		try:
			simuladorMK1_2 = Matchup([PuntosBotMk2, PuntosBotMk1], ["MK2", "MK1"])
			simuladorMK1_2.simular(CANTIDAD_DE_PARTIDAS_POR_LADO_VS_MK1)
			simuladorMK1_2.guardarGráficos(f"../../../Desktop/Matchups/MK2/mk2vsmk1/MK2_vs_MK1-{nombreFile}.jpg")
			logréCorrerExperimento2 = True
		except Exception:
			print("Tuvimos una excepción jugando! Reintentando...")
	
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
print(f"COEF_MULTIPLICADOR_OBTENIDO: {mejorConfiguracion[0]}")
print(f"PLUS_OBTENER_MULTIPLICADOR: {mejorConfiguracion[1]}")
print(f"COEF_ARRANCAR_COLECCIONABLE: {mejorConfiguracion[2]}")
print(f"COEF_COMPLETAR_DUO: {mejorConfiguracion[3]}")
print(f"PLUS_SIRENA: {mejorConfiguracion[4]}")
print(f"COEF_SEGUIR_COLECCIONABLE: {mejorConfiguracion[5]}")
print(f"PLUS_PRIMER_PEZ: {mejorConfiguracion[6]}")
print(f"PLUS_PRIMER_BARCO: {mejorConfiguracion[7]}")
print(f"PLUS_PRIMER_CANGREJO: {mejorConfiguracion[8]}")
print(f"PLUS_PRIMER_NADADORTIBURÓN: {mejorConfiguracion[9]}")

