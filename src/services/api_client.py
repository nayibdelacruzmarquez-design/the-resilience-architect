import asyncio
import random
import aiohttp


class NetworkError(Exception):
    """Excepción para fallos transitorios de red (Pérdida de paquetes, Timeouts)."""
    pass


class InvalidInputError(Exception):
    """Excepción para errores de usuario (Inputs inválidos / Bad Request)."""
    pass


class ResilientApiClient:
    """
    Cliente de API asíncrono que simula un entorno de red altamente volátil
    con un 30% de pérdida de paquetes (Stress Test).
    """

    def __init__(self, failure_rate: float = 0.30):
        self.failure_rate = failure_rate
        # Consumiremos una API pública meteorológica (Open-Meteo) que no requiere API Key
        self.base_url = "https://api.open-meteo.com/v1/forecast"

    async def fetch_weather_data(self, latitude: float, longitude: float) -> dict:
        """
        Obtiene datos del clima de forma asíncrona.
        Simula pérdida de paquetes y latencia de red.
        """
        # 1. Simulación de Validación de Usuario (User Error Path)
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            raise InvalidInputError("Las coordenadas provistas están fuera del rango geográfico válido.")

        # 2. Simulación de Entorno Hostil (30% de Pérdida de Paquetes)
        if random.random() < self.failure_rate:
            raise NetworkError("Fallo de conexión crítico: Paquete perdido en el socket (Simulado).")

        # 3. Llamada HTTP asíncrona real (No bloqueante)
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": "true"
        }

        try:
            async with aiohttp.ClientSession() as session:
                # Establecemos un timeout estricto para probar el "Slow Connection Monitor" si fuera necesario
                async with session.get(self.base_url, params=params, timeout=5.0) as response:
                    if response.status == 400:
                        raise InvalidInputError("La API externa rechazó los parámetros provistos.")
                    elif response.status != 200:
                        raise NetworkError(f"Error de servidor externo. Status: {response.status}")

                    data = await response.json()
                    current = data.get("current_weather", {})

                    return {
                        "temp": current.get("temperature"),
                        "windspeed": current.get("windspeed"),
                        "status": "Online"
                    }
        except asyncio.TimeoutError:
            raise NetworkError("La petición de red excedió el tiempo límite del socket.")
        except aiohttp.ClientError as e:
            raise NetworkError(f"Error de transporte HTTP: {str(e)}")