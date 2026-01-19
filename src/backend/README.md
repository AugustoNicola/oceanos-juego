# Módulo Backend

Este módulo se encarga de responder a las peticiones de la [interfaz web](https://github.com/AugustoNicola/oceanos-interfaz) para poder jugar una partida desde el navegador. Utiliza instancias del [`AdministradorDeJuego`](https://github.com/AugustoNicola/oceanos-juego/tree/main/src/administrador) para jugar las partidas.

## Cómo Usar

Para poder activar el backend, ejecutar desde `src/` el comando `python -m uvicorn backend.main:app --reload --port 8321`. Esto activa el sistema para que pueda responder a la interfaz web.

