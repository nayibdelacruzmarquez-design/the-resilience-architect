import pytest
from src.core.engine import AsyncEngine
from src.core.commands import AsyncCommand
from src.services.api_client import NetworkError

class DummyNetworkFailCommand(AsyncCommand):
    """Comando simulado que simula fallas de red repetidas para pruebas."""
    def __init__(self):
        self.execution_count = 0

    async def execute(self) -> None:
        self.execution_count += 1
        raise NetworkError("Fallo de red persistente simulado.")

@pytest.mark.asyncio
async def test_engine_exponential_backoff_retry_exhaustion():
    """Valida que el motor ejecute los reintentos declarados y luego propague el error."""
    engine = AsyncEngine()
    fail_command = DummyNetworkFailCommand()

    # Intentamos correr el comando con 3 intentos máximos y retraso inicial de 0.01s para velocidad del test
    with pytest.raises(NetworkError):
        await engine.run_command_with_retry(
            command=fail_command,
            max_retries=3,
            initial_delay=0.01
        )

    # El comando debe haber sido ejecutado exactamente 3 veces antes de rendirse
    assert fail_command.execution_count == 3