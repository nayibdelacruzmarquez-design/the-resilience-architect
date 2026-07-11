from abc import ABC, abstractmethod
from src.core.state_machine import StateMachine, UIState


class AsyncCommand(ABC):
    """Interfaz base para comandos asíncronos."""

    @abstractmethod
    async def execute(self) -> None:
        pass


class FetchDataCommand(AsyncCommand):
    """
    Comando concreto para solicitar datos de la API de forma resiliente.
    """

    def __init__(self, api_service, symbol: str, state_machine: StateMachine):
        self.api_service = api_service
        self.symbol = symbol
        self.state_machine = state_machine

    async def execute(self) -> None:
        # 1. Transición inmediata a estado de carga
        self.state_machine.transition_to(UIState.LOADING)

        try:
            # 2. Consumo asíncrono del servicio (No bloquea el hilo principal)
            data = await self.api_service.fetch_data(self.symbol)

            # 3. Éxito: Se envían los datos a la UI
            self.state_machine.transition_to(UIState.SUCCESS, {"data": data})

        except Exception as error:
            # El comando captura el error y lo propaga a través de la máquina de estados
            # delegando la decisión visual al ErrorHandler / UI
            self.state_machine.transition_to(UIState.ERROR, {"error": error, "command": self})