# API Estaciones de Combustible (Wrapper)

API RESTful desarrollada en **Python** con **FastAPI**. Actúa como intermediario (wrapper) para buscar y filtrar estaciones de combustible en Chile usando la ubicación geográfica (latitud/longitud) y criterios como cercanía, precio y disponibilidad de tienda de conveniencia.

El sistema consume los datos de la API "[Bencina en Línea](https://www.bencinaenlinea.cl/#/busqueda_estaciones)", los procesa usando la **Fórmula de Haversine** para calcular distancias de forma precisa y retornar un JSON estructurado y limpio.

## Requisitos

Tener instalado en equipo local:
* Python 3.10 o superior.
* `pip` (Package manager de Python).

## Instalación y Ejecución

**1. Clonar repositorio**
\`\`\`bash
git clone <URL_DE_TU_REPOSITORIO>
cd api_bencina
\`\`\`

**2. Crear y activar un entorno virtual (Recomendado)**
\`\`\`bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
\`\`\`

**3. Instalar dependencias**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

**4. Ejecutar servidor local**
\`\`\`bash
uvicorn main:app --reload
\`\`\`
El servidor se iniciará en `http://127.0.0.1:8000`.

## Estructura del Proyecto

El proyecto tiene un diseño que separa las responsabilidades en archivos:

* `main.py`: Entrada de la aplicación. Configura FastAPI, metadatos y el manejador global de excepciones.
* `api.py`: Contiene los endpoints de la API y la inyección de dependencias.
* `models.py`: Contiene los esquemas de Pydantic y Enums para validar correctamente los datos de entrada.
* `services.py`: Contiene la lógica de negocio. Maneja el cliente HTTP asíncrono para comunicarse con la API de Bencina en Línea, la fórmula de Haversine para calcular distancias y el algoritmo de filtrado/mapeo de datos.

## Documentación de la API y Ejemplos de Uso

Al estar construido con FastAPI, la documentación interactiva (Swagger UI) se genera automáticamente. Una vez el servidor esté corriendo, se puede visitar:
* **Swagger UI:** `http://127.0.0.1:8000/docs`
* **ReDoc:** `http://127.0.0.1:8000/redoc`

### Endpoint Principal
\`GET /api/stations/search\`

**Parámetros (Query):**
* `lat` (float, requerido): Latitud de origen.
* `lng` (float, requerido): Longitud de origen.
* `product` (string, requerido): Tipo de combustible. Valores permitidos: `93`, `95`, `97`, `diesel`, `kerosene`.
* `nearest` (bool, opcional): Si es `true`, busca la estación más cercana.
* `store` (bool, opcional): Si es `true`, filtra estaciones que tengan **Tienda de Conveniencia**.
* `cheapest` (bool, opcional): Si es `true`, busca la estación con menor precio.

### Ejemplos de uso

**1. Estación más cercana por producto (Gasolina 93)**
\`\`\`text
GET /api/stations/search?lat=-33.685&lng=-71.215&product=93&nearest=true
\`\`\`

**2. Estación más cercana con tienda y menor precio (Diesel)**
\`\`\`text
GET /api/stations/search?lat=-33.685&lng=-71.215&product=diesel&store=true&cheapest=true
\`\`\`

**Ejemplo de Respuesta Exitosa (Status 200 OK):**
\`\`\`json
{
    "success": true,
    "data": {
        "id": "10056",
        "compania": "COPEC",
        "direccion": "San Martin Esq. Uribe",
        "comuna": "Antofagasta",
        "region": "ANTOFAGASTA",
        "latitud": -23.6491868026,
        "longitud": -70.4011811037,
        "distancia(lineal)": 0.5,
        "precios93": 1347,
        "tienda": {
            "codigo": "2510",
            "nombre": "Tienda Pronto Antofagasta",
            "tipo": "Pronto / Punto"
        },
        "tiene_tienda": true
    }
}
\`\`\`

## Manejo de Errores y Excepciones

La API está construida para no fallar de forma silenciosa ni exponer detalles del servidor ante situaciones inesperadas. Se han implementado los siguientes manejos:

* **Error 422 Unprocessable Entity:** Gestionado por las validaciones de Pydantic, si el usuario envía tipos de datos incorrectos (ej. texto en lugar de latitud) o valores de combustible no permitidos en el Enum.
* **Error 400 Bad Request (`ValueError`):** Lanzado cuando se procesan los datos exitosamente, pero no se encuentran estaciones que cumplan con los filtros solicitados por el usuario.
* **Error 503 Service Unavailable (`ConnectionError` / `httpx`):** Implementado en `services.py` como salvaguarda para dependencia externa. Si la librería `httpx` detecta que la API de Bencina en Línea experimenta una caída (Timeouts, bloqueos de conexión o respuestas HTTP 5xx), el error interno `httpx.RequestError` es capturado y transformado en un HTTP 503, informando al cliente que el proveedor de datos está fuera de servicio, sin detener el servicio.
* **Error 500 Internal Server Error:** Un Exception Handler global (En `main.py`), actúa como última red de seguridad. Atrapa fallos no manejados del código interno (Ej: cambios en la estructura del JSON en la API de bencina en línea), devolviendo un JSON estandarizado y manteniendo la aplicación viva.
