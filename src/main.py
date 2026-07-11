import sys
import asyncio
from PyQt6.QtWidgets import QApplication
from qasync import QEventLoop

from src.core.engine import AsyncEngine
from src.core.state_machine import StateMachine
from src.services.api_client import ResilientApiClient
from src.services.cache_proxy import WeatherCacheProxy
from src.ui.main_window import MainWindow


def main():
    # 1. Configurar la aplicación de Qt
    app = QApplication(sys.argv)

    # 2. Hacer el "Bridge" mágico entre asyncio y Qt
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # 3. Inicializar Componentes de la Arquitectura (Inyección de Dependencias)
    state_machine = StateMachine()
    engine = AsyncEngine()

    real_api_client = ResilientApiClient(failure_rate=0.30)  # 30% pérdida
    proxy_cache_service = WeatherCacheProxy(real_api_client)

    # 4. Levantar Ventana Principal pasándole el motor desacoplado
    window = MainWindow(engine, state_machine, proxy_cache_service)
    window.show()

    # 5. Correr el bucle de eventos unificado de forma asíncrona
    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()