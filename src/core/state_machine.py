from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal

class UIState(Enum):
    LOADING = "LOADING"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    RETRYING = "RETRYING"

class StateMachine(QObject):
    """
    Máquina de Estados de la UI que implementa el Patrón Observer.
    Emite una señal cada vez que el estado del sistema cambia.
    """
    # Señal que notifica: (NuevoEstado, DiccionarioConDatosOErrores)
    state_changed = pyqtSignal(UIState, dict)

    def __init__(self):
        super().__init__()
        self._current_state = UIState.SUCCESS

    @property
    def current_state(self) -> UIState:
        return self._current_state

    def transition_to(self, new_state: UIState, payload: dict = None):
        """Cambia el estado actual y notifica a todos los suscriptores (UI)."""
        self._current_state = new_state
        self.state_changed.emit(new_state, payload or {})