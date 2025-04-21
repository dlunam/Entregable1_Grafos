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
    problema = df[df['arrival_time'] == df['departure_time']]
    if not problema.empty:
        print("\n⚠️ Registros con arrival_time igual a departure_time:")
        print(problema[['trip_id', 'stop_sequence', 'stop_id', 'arrival_time', 'departure_time']])
    
    df['tiempo_en_estacion'] = df['departure_time'] - df['arrival_time']
    df['tiempo_en_estacion'] = df['tiempo_en_estacion'].apply(lambda x: str(x).split()[-1])
    
    df_estaciones = df[['trip_id', 'stop_sequence', 'stop_id', 'arrival_time', 'departure_time', 'tiempo_en_estacion']]
    return df_estaciones

def calcular_tiempo_entre_estaciones(df):
    df = df.dropna(subset=['arrival_time', 'departure_time'])
    
    df['siguiente_stop_id'] = df.groupby('trip_id')['stop_id'].shift(-1)
    df['tiempo_entre_estaciones'] = df.groupby('trip_id')['arrival_time'].shift(-1) - df['departure_time']
    
    df_tramos = df[['trip_id', 'stop_sequence', 'stop_id', 'siguiente_stop_id', 'departure_time', 'tiempo_entre_estaciones']]
    
    df_tramos['stop_id'] = df_tramos['stop_id'].str.replace('par_4_', '', regex=False)
    df_tramos['siguiente_stop_id'] = df_tramos['siguiente_stop_id'].str.replace('par_4_', '', regex=False)
    
    df_tramos['tiempo_entre_estaciones'] = df_tramos['tiempo_entre_estaciones'].apply(lambda x: str(x).split()[-1])
    
    return df_tramos[df_tramos['siguiente_stop_id'].notnull()]

def mostrar_muestra(df_estaciones, df_tramos):
    print("\n--- Muestra aleatoria de tiempos en estación ---")
    print(df_estaciones.sample(n=5))
    
    print("\n--- Muestra aleatoria de tiempos entre estaciones ---")
    print(df_tramos.sample(n=5))

def guardar_archivos(df_estaciones, df_tramos):
    tiempos_raw = pd.to_timedelta(df_estaciones['tiempo_en_estacion'])
    
    if tiempos_raw.dt.total_seconds().eq(0).all():
        print("\n⚠️ El archivo 'tiempos_en_estaciones.csv' no se guardará porque todos los tiempos son 0 segundos.")
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
        mostrar_muestra(df_estaciones, df_tramos)
        guardar_archivos(df_estaciones, df_tramos)

if __name__ == "__main__":
    main()
