import json
import os
from src.services.api_client import ResilientApiClient, NetworkError


class WeatherCacheProxy:
    """
    Proxy estructural que controla el acceso al ApiClient real.
    Implementa un mecanismo de caché local (Modo Offline) para sobrevivir a caídas totales.
    """

    def __init__(self, real_client: ResilientApiClient, cache_file: str = "local_cache.json"):
        self._real_client = real_client
        self._cache_file = cache_file
        self._memory_cache = {}
        self._load_cache_from_disk()

    def _load_cache_from_disk(self):
        """Carga los datos previos del disco de forma segura al inicializar."""
        if os.path.exists(self._cache_file):
            try:
                with open(self._cache_file, "r", encoding="utf-8") as f:
                    self._memory_cache = json.load(f)
            except Exception:
                self._memory_cache = {}

    def _save_cache_to_disk(self):
        """Persiste la caché actual en disco."""
        try:
            with open(self._cache_file, "w", encoding="utf-8") as f:
                json.dump(self._memory_cache, f, indent=4)
        except Exception:
            pass

    async def fetch_data(self, symbol: str) -> dict:
        """
        Intenta obtener datos frescos de la API. Si la red colapsa,
        rescata el último estado conocido guardado en caché.

        Nota: 'symbol' mapeará a coordenadas predefinidas por simplicidad (ej: 'CDMX', 'NY').
        """
        # Mapeo simple de ciudades a coordenadas para cumplir con la interfaz limpia del Command
        coordinates = {
            "CDMX": (19.4326, -99.1332),
            "MONTERREY": (25.6866, -100.3161),
            "GUADALAJARA": (20.6597, -103.3496)
        }

        location = symbol.upper()
        lat, lon = coordinates.get(location, (19.4326, -99.1332))  # Default CDMX si no existe

        try:
            # Intento a través del canal real (Red Volátil)
            fresh_data = await self._real_client.fetch_weather_data(lat, lon)

            # Si tiene éxito, actualizamos la caché local
            self._memory_cache[location] = fresh_data
            self._save_cache_to_disk()
            return fresh_data

        except NetworkError as network_exc:
            # ¡INGENIERÍA DE RESILIENCIA EN ACCIÓN!
            # Si la red falla por completo, revisamos si tenemos datos antiguos de esa ciudad
            if location in self._memory_cache:
                fallback_data = self._memory_cache[location].copy()
                fallback_data["status"] = "Offline (Datos de Caché)"
                return fallback_data

            # Si no hay datos en caché para este recurso, dejamos ir el error hacia arriba
            raise network_exc