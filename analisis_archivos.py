import pandas as pd
import geopandas as gpd

# Función para analizar archivos CSV o TXT
def analizar_csv(nombre_archivo):
    print(f"\n🔍 Analizando archivo CSV/TXT: {nombre_archivo}")
    
    try:
        df = pd.read_csv(nombre_archivo)

        print("\n📄 Columnas disponibles:")
        print(list(df.columns))

        print("\n📊 Tipos de datos por columna:")
        print(df.dtypes)

        print("\n🔎 Primeras filas:")
        print(df.head())

    except Exception as e:
        print(f"❌ Error al procesar el archivo {nombre_archivo}: {e}")

# Función para analizar archivos GeoJSON
def analizar_geojson(nombre_archivo):
    print(f"\n🗺️ Analizando archivo GeoJSON: {nombre_archivo}")
    
    try:
        gdf = gpd.read_file(nombre_archivo)

        print("\n📄 Columnas disponibles:")
        print(list(gdf.columns))

        print("\n📊 Tipos de datos por columna:")
        print(gdf.dtypes)

        print("\n🌍 Tipo de geometría:")
        print(gdf.geom_type.value_counts())

        print("\n🔎 Primeras filas:")
        print(gdf.head())

    except Exception as e:
        print(f"❌ Error al procesar el archivo {nombre_archivo}: {e}")

# Ejecutar análisis sobre todos los archivos
analizar_csv("stop_times.txt")
analizar_geojson("M4_Estaciones.geojson")
analizar_geojson("M4_Tramos.geojson")

