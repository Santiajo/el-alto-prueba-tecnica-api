# Configuración FastAPI. Manejo de errores globales
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

# Config logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Estaciones de Combustible",
    description="API para buscar las estaciones de combustible más cercanas y económicas.",
    version="1.0.0"
)

# Error 500 - Manejo de error global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error inesperado en {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "message": "Ha ocurrido una situación inesperada procesando tu solicitud.",
            # "detail": str(exc) # Opcional, quitar en producción. Lo dejo comentado para demostración y debugging.
        }
    )

# Rutas de API
from api import router as api_router
app.include_router(api_router, prefix="/api")