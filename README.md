# The Resilience Architect: Forjando Interfaces Imperturbables

Este proyecto implementa una arquitectura de software de alta fidelidad, reactiva y resiliente en Python utilizando **PyQt6** y **asyncio**. Diseñado bajo los estándares del nivel *Senior Associate (SSR) de la Certificación 10001*, el sistema está blindado para entornos de red volátiles, garantizando una experiencia de usuario fluida (60 FPS) y tolerancia a fallos mediante el uso estratégico de patrones de diseño.

---

## Arquitectura y Patrones de Diseño

Para lograr un desacoplamiento total (Separation of Concerns - SoC) entre la capa de datos, la lógica de control y la interfaz gráfica, se implementaron los siguientes patrones:

* **Patrón Observer (Comportamiento):** Centralizado en la clase `StateMachine`. La interfaz gráfica no manipula los datos directamente ni interroga al motor; en su lugar, se suscribe de manera reactiva a la señal `state_changed`. La UI se redibuja automáticamente basándose en la transición de estados (`LOADING`, `SUCCESS`, `ERROR`, `RETRYING`).
* **Patrón Command (Comportamiento):** Implementado en `FetchDataCommand`. Encapsula por completo la petición de consulta de datos del clima, aislando el contexto de la ejecución. Esto permite que el motor de eventos controle y reintente acciones de forma independiente sin acoplar la UI con los servicios.
* **Patrón Proxy Structural (Estructura):** Materializado en `WeatherCacheProxy`. Actúa como un intermediario transparente del cliente HTTP real. Si la API colapsa de forma definitiva, el Proxy intercepta la solicitud y rescata el último estado válido conocido desde un almacenamiento en disco (`local_cache.json`), activando un **Modo Offline** transparente.

---

## Gestión de Asincronía y Concurrencia

El bucle de eventos de Qt se unificó con el de `asyncio` mediante la infraestructura de **`qasync`**. 
* **Cero Bloqueos del Main Thread:** Ninguna operación de I/O de red (`aiohttp`) corre sobre el hilo principal de la interfaz gráfica (GUI Thread), erradicando por completo los micro-congelamientos y *Deadlocks*.
* **Monitoreo de Conexión Lenta:** El `AsyncEngine` orquesta un hilo monitor no bloqueante (`_monitor_timeout`). Si una petición excede el umbral de confort de **2.0 segundos**, el motor emite una señal automática de de tipo *Slow Connection* para cambiar semánticamente la barra de estado de la UI sin interrumpir la descarga de datos de fondo.

---

## Ingeniería de Resiliencia ante Entornos Hostiles

El sistema clasifica y ataja los puntos de falla en tres rutas críticas (*Critical Paths*):
1.  **Errores de Red (Transitorios):** El cliente de la API simula de forma intencional un **30% de pérdida de paquetes** (`NetworkError`). Al detectarse, el motor de eventos mitiga el fallo aplicando un algoritmo de **Exponential Backoff** (3 reintentos con retraso duplicado progresivamente).
2.  **Errores de Validación (Inputs de Usuario):** Controlados mediante `InvalidInputError` (ej. si se alteraran las coordenadas a rangos fuera del mapa), mostrando retroalimentación descriptiva inmediata.
3.  **Trazabilidad y Logging:** Cada señal enviada, reintento o fallo se registra con marcas de tiempo en la consola mediante la librería estándar `logging`, permitiendo realizar auditorías de caja negra durante la ejecución.

---

## Instalación y Configuración

### 1. Requisitos Previos
Asegúrate de contar con Python 3.11 o superior.

### 2. Instalación de Dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecución de la suite de pruebas automáticas
```bash
pytest
```
### 4. Ejecución del Dashboard
```bash
python -m src.main
```