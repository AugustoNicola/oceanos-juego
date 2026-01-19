# Módulo Matchup

[`src/matchup/matchup.py`](https://github.com/AugustoNicola/oceanos-juego/blob/main/src/matchup/matchup.py) utiliza los parámetros definidos al principio del archivo para disputar una serie de partidas entre [Jugadores](https://github.com/AugustoNicola/oceanos-juego/tree/main/src/jugador). Para ello, utiliza el [`AdministradorDeJuego`](https://github.com/AugustoNicola/oceanos-juego/tree/main/src/administrador) y las métricas que éste recolecta para generar estadísticas del duelo.

## Cómo usar

### Desde la terminal

Desde `src/`, correr `python -m matchup.matchup <cantidadPartidas> <cantidadJugadores> <jugador1> ... <jugadorN> <apodo1> ... <apodoN> `, especificando la cantidad de partidas a jugar, la cantidad de jugadores, los jugadores del duelo (sus [nombres de jugador](https://github.com/AugustoNicola/oceanos-juego/tree/main/src/jugador)) y cómo apodarlos en los gráficos.

Esto correrá las partidas indicadas en el sistema, y al terminar abre una ventana con las estadísticas.

### Desde otro archivo

Esta clase espera ser creada con un arreglo de nombres de los jugadores que van a jugar y con los apodos para los gráficos (es decir, se invoca como `Matchup(jugadoresDelMatchup=['randybot', 'sirena_enjoyer'], nombres=['BotCopado', 'BotFachero'])`).

Una vez creado, el objeto `Matchup` provee un método `simular(cantidadDePartidasAJugar)` para simular una cantidad de partidas seguidas.

Además, están los métodos `mostrarGráficos` y `guardarGráficos`, para visualizar las estadísticas de todas las partidas jugadas hasta ahora.

## ¿Cómo le juego a mi Bot?

El sistema de matchups está pensado para correr muchas partidas rápidamente sin input humano y ver tendencias a largo plazo. Si querés probar jugar contra tu bot, o simplemente ver qué acciones toma en un partido, probá la [interfaz web](https://github.com/AugustoNicola/oceanos-interfaz)!