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
    lat: float = Field(-33.685, description="Latitud de origen (ej. -33.685)")
    lng: float = Field(-71.215, description="Longitud de origen (ej. -71.215)")
    product: ProductType = Field(..., description="Tipo de combustible requerido")
    nearest: Optional[bool] = Field(False, description="Buscar la más cercana")
    store: Optional[bool] = Field(False, description="Debe tener tienda")
    cheapest: Optional[bool] = Field(False, description="Debe tener el menor precio")