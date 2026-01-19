class ExcepciónEsperando(Exception):
    """Excepción que se lanza cuando el administrador necesita esperar a que el juego continúe."""
    def __init__(self, message="Esperando continuar..."):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message