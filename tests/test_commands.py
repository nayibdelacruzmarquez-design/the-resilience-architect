import pytest
from src.core.state_machine import StateMachine, UIState
from src.core.commands import FetchDataCommand


class MockWeatherProxyService:
    """Mock controlado del servicio proxy para aislar las pruebas de la UI."""

    def __init__(self, should_fail=False):
        self.should_fail = should_fail

    async def fetch_data(self, symbol: str) -> dict:
        if self.should_fail:
            raise Exception("Error forzado en Mock")
        return {"temp": 22.5, "windspeed": 12.0, "status": "Online"}


@pytest.mark.asyncio
async def test_fetch_command_success_lifecycle():
    """Valida que el comando transicione la UI a LOADING y luego a SUCCESS con los datos."""
    state_machine = StateMachine()
    mock_service = MockWeatherProxyService(should_fail=False)

    # Lista para capturar los estados por los que pasa la UI dinámicamente
    captured_states = []
    state_machine.state_changed.connect(lambda state, payload: captured_states.append((state, payload)))

    command = FetchDataCommand(mock_service, "CDMX", state_machine)
    await command.execute()

    # Verificaciones del patrón de comportamiento
    assert len(captured_states) == 2
    assert captured_states[0][0] == UIState.LOADING
    assert captured_states[1][0] == UIState.SUCCESS
    assert captured_states[1][1]["data"]["temp"] == 22.5


@pytest.mark.asyncio
async def test_fetch_command_error_lifecycle():
    """Valida que si el servicio falla, el comando encapsule el error y mueva la UI a ERROR."""
    state_machine = StateMachine()
    mock_service = MockWeatherProxyService(should_fail=True)

    captured_states = []
    state_machine.state_changed.connect(lambda state, payload: captured_states.append((state, payload)))

    command = FetchDataCommand(mock_service, "GUADALAJARA", state_machine)
    await command.execute()

    assert captured_states[0][0] == UIState.LOADING
    assert captured_states[1][0] == UIState.ERROR
    assert "error" in captured_states[1][1]