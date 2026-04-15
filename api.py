# Endpoints de API
from fastapi import APIRouter, Depends, HTTPException
from models import SearchParams
from services import fetch_bencina_data
from services import procesar_estaciones

router = APIRouter(tags=["Búsqueda de Estaciones"])

@router.get(
    "/stations/search",
    summary="Buscar la mejor estación de combustible",
    response_description="JSON estructurado con la estación que cumple los criterios."
)
async def search_stations(params: SearchParams = Depends()):
    # Comentarios para swagger:
    """
    Busca y filtra las estaciones de combustible a nivel nacional basándose en los parámetros del usuario.

    Este endpoint consume la API oficial de Bencina en Línea, calcula las distancias utilizando la 
    **Fórmula de Haversine** y aplica filtros de negocio.

    ### Reglas de filtrado:
    * **Cercanía**: Si `nearest=true`, devuelve la estación con menor distancia lineal.
    * **Precio**: Si `cheapest=true`, prioriza el valor más bajo del mercado. En caso de empate, gana la más cercana.
    * **Tienda**: Si `store=true`, descarta cualquier estación que no posea tiendas (Pronto, Upa!, Spacio 1, etc.).

    **Nota:** La latitud, longitud y el tipo de producto son obligatorios.
    """
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