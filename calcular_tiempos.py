import pandas as pd

def cargar_stop_times(path="stop_times.txt"):
    try:
        df = pd.read_csv(path)
        df['arrival_time'] = pd.to_timedelta(df['arrival_time'])
        df['departure_time'] = pd.to_timedelta(df['departure_time'])
        df = df.sort_values(by=['trip_id', 'stop_sequence'])
        return df
    except Exception as e:
        print(f"❌ Error cargando {path}: {e}")
        return None

def calcular_tiempo_en_estacion(df):
    # Verificar si hay registros con arrival_time y departure_time iguales
    problema = df[df['arrival_time'] == df['departure_time']]
    if not problema.empty:
        print("\n⚠️ Registros con arrival_time igual a departure_time:")
        print(problema[['trip_id', 'stop_sequence', 'stop_id', 'arrival_time', 'departure_time']])
    
    df['tiempo_en_estacion'] = df['departure_time'] - df['arrival_time']
    df_estaciones = df[['trip_id', 'stop_sequence', 'stop_id', 'arrival_time', 'departure_time', 'tiempo_en_estacion']]
    return df_estaciones

def calcular_tiempo_entre_estaciones(df):
    # Asegurarnos de que no haya valores nulos
    df = df.dropna(subset=['arrival_time', 'departure_time'])
    
    # Desplazamos la columna 'stop_id' y 'arrival_time' para obtener la siguiente estación
    df['siguiente_stop_id'] = df.groupby('trip_id')['stop_id'].shift(-1)
    df['tiempo_entre_estaciones'] = df.groupby('trip_id')['arrival_time'].shift(-1) - df['departure_time']
    
    # Filtramos los tramos que no tienen la siguiente estación
    df_tramos = df[['trip_id', 'stop_sequence', 'stop_id', 'siguiente_stop_id', 'departure_time', 'tiempo_entre_estaciones']]
    
    # Eliminamos tramos donde no haya una estación siguiente (finales de viaje)
    return df_tramos[df_tramos['siguiente_stop_id'].notnull()]

def mostrar_muestra(df_estaciones, df_tramos):
    print("\n--- Muestra aleatoria de tiempos en estación ---")
    print(df_estaciones.sample(n=5))  # Muestra aleatoria de 5 filas del DataFrame de tiempos en estación
    
    print("\n--- Muestra aleatoria de tiempos entre estaciones ---")
    print(df_tramos.sample(n=5))  # Muestra aleatoria de 5 filas del DataFrame de tiempos entre estaciones

def guardar_archivos(df_estaciones, df_tramos):
    # Si el DataFrame de tiempos en estación tiene solo 0 días, no se guardará el archivo
    if df_estaciones['tiempo_en_estacion'].eq('0 days').all():
        print("\n⚠️ El archivo 'tiempos_en_estaciones.csv' no se guardará porque todos los tiempos son 0 días.")
    else:
        df_estaciones.to_csv("tiempos_en_estaciones.csv", index=False)
        print("✅ Archivo 'tiempos_en_estaciones.csv' guardado.")
    
    df_tramos.to_csv("tiempos_entre_estaciones.csv", index=False)
    print("✅ Archivo 'tiempos_entre_estaciones.csv' guardado.")

def main():
    df = cargar_stop_times()
    if df is not None:
        df_estaciones = calcular_tiempo_en_estacion(df)
        df_tramos = calcular_tiempo_entre_estaciones(df)
        mostrar_muestra(df_estaciones, df_tramos)  # Muestra aleatoria
        guardar_archivos(df_estaciones, df_tramos)  # Guardamos los archivos

if __name__ == "__main__":
    main()
