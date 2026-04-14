# Endpoints de API
from fastapi import APIRouter, Depends, HTTPException
from models import SearchParams
from services import fetch_bencina_data
from services import procesar_estaciones

router = APIRouter()

@router.get("/stations/search")
async def search_stations(params: SearchParams = Depends()):
    try:
        # Traer data cruda de Bencina en Línea
        raw_data = await fetch_bencina_data()

        # Procesar data. Filtros y Mapeo.
        resultado_final = procesar_estaciones(raw_data, params)

        return resultado_final
    
    except ConnectionError as e:
        # Si fetch_bencina_data da error -> Devolver 503
        raise HTTPException(status_code=503, detail=str(e))
        
    except ValueError as e:
        # Si procesar_estaciones lanza error (ej. no hay estaciones con esos filtros) -> Devolver 400
        raise HTTPException(status_code=400, detail=str(e))