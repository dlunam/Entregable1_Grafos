import geopandas as gpd
import re

# Archivos originales
ruta_estaciones = "M4_Estaciones.geojson"
ruta_tramos = "M4_Tramos.geojson"

# Leer los archivos originales
estaciones = gpd.read_file(ruta_estaciones)
tramos = gpd.read_file(ruta_tramos)

# Filtrar columnas necesarias de cada archivo
estaciones_filtrado = estaciones[['CODIGOESTACION', 'DENOMINACION', 'LINEAS', 'geometry']].copy()
tramos_filtrado = tramos[['CODIGOITINERARIO', 'CODIGOESTACION', 'NUMEROORDEN', 'LONGITUDTRAMOANTERIOR', 'NUMEROLINEAUSUARIO', 'geometry']].copy()

# Modificar NUMEROLINEAUSUARIO para dejar solo el número inicial
def extraer_numero_inicial(valor):
    valor_str = str(valor)
    coincidencia = re.match(r'^(\d+)', valor_str)
    if coincidencia:
        return coincidencia.group(1)
    return valor_str

tramos_filtrado['NUMEROLINEAUSUARIO'] = tramos_filtrado['NUMEROLINEAUSUARIO'].apply(extraer_numero_inicial)

# Guardar como nuevos archivos GeoJSON
estaciones_filtrado.to_file("Estaciones_filtrado.geojson", driver='GeoJSON')
tramos_filtrado.to_file("Tramos_filtrado.geojson", driver='GeoJSON')

print("✅ Archivos guardados:\n - Estaciones_filtrado.geojson\n - Tramos_filtrado.geojson\n - Paradas_filtrado.geojson")

# ------------------------------
# Verificación: leer y mostrar columnas y tipos
# ------------------------------

# Leer los archivos nuevos
estaciones_check = gpd.read_file("Estaciones_filtrado.geojson")
tramos_check = gpd.read_file("Tramos_filtrado.geojson")

# Mostrar info de estaciones
print("\n🔎 Verificación Estaciones:")
print("Columnas:", list(estaciones_check.columns))
print(estaciones_check.dtypes)

# Mostrar info de tramos
print("\n🔎 Verificación Tramos:")
print("Columnas:", list(tramos_check.columns))
print(tramos_check.dtypes)