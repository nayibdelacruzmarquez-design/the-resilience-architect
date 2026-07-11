import asyncio
import logging
from PyQt6.QtCore import QObject, pyqtSignal
from src.core.commands import AsyncCommand

# Configuración básica de logs para la trazabilidad solicitada en la rúbrica
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class AsyncEngine(QObject):
    """
    Orquestador asíncrono encargado de ejecutar comandos, monitorear
    tiempos de respuesta y aplicar políticas de reintento (Resilience Engineering).
    """
    # Señal emitida si una petición tarda más de un umbral establecido (ej. 2 segundos)
    slow_connection_detected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("AsyncEngine")

    async def run_command_with_retry(self, command: AsyncCommand, max_retries: int = 3, initial_delay: float = 1.0):
        """
        Ejecuta un comando con un mecanismo de Exponential Backoff si ocurren fallos de red.
        Monitorea de forma concurrente si la conexión es lenta.
        """
        delay = initial_delay

        for attempt in range(1, max_retries + 1):
            self.logger.info(f"Ejecutando comando (Intento {attempt}/{max_retries})...")

            # Creamos la tarea del comando y el monitor de conexión lenta
            command_task = asyncio.create_task(command.execute())
            monitor_task = asyncio.create_task(self._monitor_timeout(command_task))

            try:
                # Esperamos a que el comando termine
                await command_task
                self.logger.info("Comando ejecutado con éxito.")
                return  # Salida exitosa

            except Exception as exc:
                # Cancelamos el monitor si el comando falla antes
                monitor_task.cancel()

                # Identificación de "Critical Paths" y clasificación de errores (Network vs Logic)
                # Nota: Asumimos que tu servicio lanzará una excepción personalizada para red
                is_network_error = "Network" in exc.__class__.__name__ or "Timeout" in str(exc)

                self.logger.warning(f"Fallo detectado en intento {attempt}: {exc}")

                if is_network_error and attempt < max_retries:
                    self.logger.info(f"Error transitorio de red. Reintentando en {delay}s (Exponential Backoff)...")
                    await asyncio.sleep(delay)
                    delay *= 2  # Duplicamos el tiempo de espera para el siguiente intento
                else:
                    # Si es un error de lógica, input inválido o se agotaron los reintentos, se propaga
                    self.logger.error("Error crítico o reintentos agotados. Propagando excepción.")
                    raise exc

    async def _monitor_timeout(self, target_task: asyncio.Task, threshold: float = 2.0):
        """Monitorea de forma no bloqueante si la tarea excede el tiempo límite de confort."""
        try:
            await asyncio.sleep(threshold)
            if not target_task.done():
                self.logger.warning("La conexión está tardando más de 2 segundos.")
                self.slow_connection_detected.emit("Advertencia: Conexión lenta detectada. Esperando respuesta...")
        except asyncio.CancelledError:
            # El comando terminó antes del umbral, el monitor se cancela limpiamente
            pass