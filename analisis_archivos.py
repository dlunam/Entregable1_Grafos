import geopandas as gpd

# Función para analizar un archivo GeoJSON
def analizar_geojson(nombre_archivo):
    print(f"\n🔍 Analizando: {nombre_archivo}")
    
    try:
        gdf = gpd.read_file(nombre_archivo)

        print("\n📄 Columnas disponibles:")
        print(list(gdf.columns))

        print("\n📊 Tipos de datos por columna:")
        print(gdf.dtypes)

        print("\n🔎 Primeras filas:")
        print(gdf.head())

    except Exception as e:
        print(f"❌ Error al procesar el archivo: {e}")

# Ejecutar análisis sobre los dos archivos
analizar_geojson("M4_Estaciones.geojson")
analizar_geojson("M4_Tramos.geojson")
