# Validar datos con Pydantic
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

# Valores exactos para product
class ProductType(str, Enum):
    gasolina_93 = "93"
    gasolina_95 = "95"
    gasolina_97 = "97"
    diesel = "diesel"
    kerosene = "kerosene"

# Parámetros de búsqueda
"""
lat: Latitud (número decimal, requerido)
lng: Longitud (número decimal, requerido)
product: Tipo de combustible ("93", "95", "97", "diesel", "kerosene", requerido)
nearest: Buscar la más cercana (opcional: true/false)
store: Con tienda (opcional: true/false)
cheapest: Con menor precio (opcional: true/false)
"""
class SearchParams(BaseModel):
    # Campos obligatorios con Pydantic Field (...)
    lat: float = Field(
        ..., 
        description="Latitud geográfica de origen para el cálculo de cercanía.",
        json_schema_extra={"example": -33.685}
    )
    
    lng: float = Field(
        ..., 
        description="Longitud geográfica de origen para el cálculo de cercanía.",
        json_schema_extra={"example": -71.215}
    )
    
    product: ProductType = Field(
        ..., 
        description="Tipo de combustible a consultar en las estaciones."
    )
    
    # Campos opcionales con valores por defecto
    nearest: bool = Field(
        False, 
        description="Si es verdadero, el sistema devolverá la estación con menor distancia lineal."
    )
    
    store: bool = Field(
        False, 
        description="Si es verdadero, se aplicará el filtro de tienda de conveniencia y servicios proxy."
    )
    
    cheapest: bool = Field(
        False, 
        description="Si es verdadero, se priorizará el precio más bajo del mercado."
    )