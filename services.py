# Lógica de negocio (Llamadas externas, ruta más cercana, limpieza)
import math
import httpx
from typing import List, Dict, Any

# Calcular distancias Tierra (Haversine)
def calcular_distancia(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0 # Radio de la Tierra (kms)
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

# Traer datos - Manejo de errores
async def fetch_bencina_data() -> List[Dict[str, Any]]:
    url = "https://api.bencinaenlinea.cl/api/busqueda_estacion_filtro"
    
    # Simular navegador. Evitar bloqueos de la API.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": "https://www.bencinaenlinea.cl/"
    }
    
    # Timeout 15 segundos
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            # Get sin parámetros. Devuelve toda la información nacional.
            response = await client.get(url, headers=headers)

            # Levantar error si status != 200
            response.raise_for_status() 
            
            json_response = response.json()
            
            # Extraer lista de estaciones. Validar estructura.
            if isinstance(json_response, dict) and "data" in json_response:
                estaciones = json_response["data"]
            else:
                raise ValueError("La API cambió su estructura y no se encontró la llave 'data'.")
                
            if not isinstance(estaciones, list):
                raise ValueError("La información de las estaciones no tiene el formato de lista esperado.")
                
            return estaciones
        
        # Errores de red (caídas, timeouts, rechazos)
        except httpx.RequestError as e:
            raise ConnectionError(f"Fallo de conexión con Bencina en Línea: {str(e)}") 
        except httpx.HTTPStatusError as e:
            raise ConnectionError(f"Bencina en Línea respondió con error HTTP: {e.response.status_code}")
        except Exception as e:
             raise ConnectionError(f"Error inesperado procesando los datos externos: {str(e)}")

# Filtrar y mapear estaciones
def procesar_estaciones(estaciones_crudas: List[Dict], params: Any) -> Dict:
    estaciones_validas = []
    
    # Recorrer estaciones
    for est in estaciones_crudas:
        # Validar coordenadas
        try:
            lat_est = float(est.get("latitud"))
            lon_est = float(est.get("longitud"))
        except (TypeError, ValueError):
            continue 
            
        # Filtrar por tienda.
        tiene_tienda = False
        datos_tienda = None
        servicios_raw = est.get("servicios", [])
        
        # Ids de servicios que pueden tener tienda (Usando conocimiento de mercado)
        ids_proxy_tienda = {1, 2, 3, 4} 
        
        # Palabras clave
        palabras_clave = ["tienda", "conveniencia", "pronto", "punto", "spacio", "upa", "ok market", "baño", "cajero"]
        
        for servicio in servicios_raw:
            if not isinstance(servicio, dict):
                continue
                
            id_servicio = servicio.get("id")
            nombre_servicio = servicio.get("nombre") or "" 
            nombre_limpio = nombre_servicio.lower()
            
            # Verificar Ids o palabras clave para determinar si la estación tiene tienda
            if id_servicio in ids_proxy_tienda or any(p in nombre_limpio for p in palabras_clave):
                tiene_tienda = True
                
                # Armamos respuesta estandarizada
                datos_tienda = {
                    "codigo": "4", # Código oficial de tienda
                    "nombre": "Tienda de Conveniencia / Servicios Anexos",
                    "tipo": "Conveniencia"
                }
                break # Al encontrar evidencia de tienda, dejar de iterar los servicios
                
        # Si el usuario exige tienda y la estación no tiene, se descarta
        if params.store and not tiene_tienda:
            continue
            
        # Filtrar por combustible - Obtener el precio
        precio_buscado = None
        mapa_combustibles = {
            "93": "93", "95": "95", "97": "97", 
            "diesel": "DI", "kerosene": "KE" 
        }
        codigo_buscado = mapa_combustibles.get(params.product.value)
        
        for comb in est.get("combustibles", []):
            if comb.get("nombre_corto") == codigo_buscado:
                try:
                    precio_buscado = int(float(comb.get("precio", 0)))
                except (ValueError, TypeError):
                    pass
                break
                
        if precio_buscado is None:
            continue 
            
        # Calcular distancia
        distancia = calcular_distancia(params.lat, params.lng, lat_est, lon_est)
        
        # Guardar estación que pasó los filtros
        estaciones_validas.append({
            "distancia": distancia,
            "precio": precio_buscado,
            "data_original": est,
            "tiene_tienda": tiene_tienda,
            "datos_tienda": datos_tienda
        })

    # Si se termina el loop y no hay estaciones válidas
    if not estaciones_validas:
        raise ValueError("No se encontraron estaciones que cumplan con los criterios especificados.")

    # Ordenar
    if params.cheapest and params.nearest:
        estacion_ganadora = sorted(estaciones_validas, key=lambda x: (x["precio"], x["distancia"]))[0]
    elif params.cheapest:
        estacion_ganadora = sorted(estaciones_validas, key=lambda x: x["precio"])[0]
    else:
        estacion_ganadora = sorted(estaciones_validas, key=lambda x: x["distancia"])[0]

    # Formato final
    cruda = estacion_ganadora["data_original"]
    
    diccionario_marcas = {
        23: "ABASTIBLE", 101: "Adquim", 113: "AGUESAN", 78: "Aire", 139: "ALANDRA DIESEL", 164: "AMCO", 169: "Andes Combustibles", 27: "APEX", 64: "APM", 151: "ARAMCO", 175: "Asmesol", 33: "ATT", 58: "BALTOLU", 178: "BIOCOM", 21: "CAVE", 162: "CES", 99: "CKR", 69: "CNC COMBUSTIBLES", 185: "Colun", 52: "Combustible Alhue", 135: "Combustibles HM", 65: "Combustibles J.L.T.", 18: "COMBUSTIBLES JCD", 102: "Combustibles Josefita Spa", 141: "Combustibles JRB", 100: "Combustibles JSP", 174: "Combustibles Mantul", 121: "Combustibles Nancagua SPA", 48: "Combustibles Ortiz", 181: "Combustibles San Gregorio", 166: "Combustibles San Roque", 154: "Combustibles Sandoval", 152: "Combustibles Santa María", 36: "COMERCIAL MAQUI", 129: "COMERCIAL Y SERVICIOS MS", 51: "Coopeserau", 146: "COOPEUMO COMBUSTIBLES", 5: "COPEC", 59: "CUSTOM SERVICE", 110: "Dale Combustibles", 80: "Del Sol Combustibles", 76: "Del Solar", 57: "DELPA", 85: "Doña Lucina", 53: "ECCO", 117: "ECOIL", 187: "EHL", 144: "Energy", 179: "Energy Woman", 88: "ENEX", 159: "ESA", 89: "ESTACION DE SERVICIO SANTA MARIA SPA", 54: "FACAZ", 32: "FLORES", 150: "G.O.A.T", 177: "Gasco Autogas", 165: "Gasolinera Makal", 90: "GASOLINERA MONTE AGUILA", 172: "Go Abastible", 122: "GO!", 153: "Groff", 128: "GSP Combustibles", 131: "GULF", 25: "HN", 157: "Hola", 167: "Infigas", 183: "INFINITY GROUP", 12: "JLC", 160: "JM-DIESEL", 71: "JVL COMBUSTIBLES", 168: "Lepe y Alamo", 24: "LIPIGAS", 130: "MAMG COMBUSTIBLES", 67: "Mimbral", 123: "MODENA", 77: "NavCar Combustibles", 92: "NEWEN", 180: "NOVA Service", 132: "OASIS", 119: "OIL BOX", 158: "OKEY", 138: "ORANGE COMBUSTIBLES", 149: "Pegasur", 2: "PETROBRAS", 72: "PETROCAMP", 171: "Petrofull", 39: "PETROJAC", 176: "Petroprix", 125: "PETROSI", 148: "Petrosur", 161: "Petrovic", 145: "Petrowork", 186: "POWER SPT", 66: "Punto Sur", 47: "Rafael Letelier Yañez y Cia Ltda", 73: "REDSUR", 182: "Ronda Combustibles", 107: "Ruta V45", 188: "SAMM", 97: "Servicentro Itata", 42: "SERVICENTRO LEAL", 46: "SERVICENTRO SAN MIGUEL", 45: "SERVICENTROS RABALME", 147: "Servisur", 136: "SERVITRUCK", 4: "SHELL", 10: "Sin Bandera", 118: "SIN BANDERA", 137: "SIVORI COMBUSTIBLES", 40: "SOCORRO", 106: "SOLOGAR", 184: "StarGas", 34: "SUAREZ COMBUSTIBLES", 37: "SURENERGY", 3: "TERPEL", 96: "Transpetrol", 26: "VIVA COMBUSTIBLES", 170: "WR FENIX"
    }
    
    llave_precio = f"precios{params.product.value}"

    respuesta_formateada = {
        "success": True,
        "data": {
            "id": str(cruda.get("id", "")),
            "compania": diccionario_marcas.get(cruda.get("marca"), "OTRA"),
            "direccion": cruda.get("direccion", "").strip(),
            "comuna": cruda.get("comuna", ""),
            "region": cruda.get("region", ""),
            "latitud": float(cruda.get("latitud", 0.0)),
            "longitud": float(cruda.get("longitud", 0.0)),
            "distancia(lineal)": round(estacion_ganadora["distancia"], 2),
            llave_precio: estacion_ganadora["precio"],
            "tienda": estacion_ganadora["datos_tienda"],
            "tiene_tienda": estacion_ganadora["tiene_tienda"]
        }
    }
    
    return respuesta_formateada