import geopandas as gpd
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations

# === COLORES Y METADATOS DE LÍNEAS ===

LINEA_COLORES = {
    'L1': '#00BFFF', 'L2': '#FF0000', 'L3': '#FFFF00', 'L4': '#A0522D',
    'L5': '#90EE90', 'L6': '#808080', 'L7': '#FFA500', 'L8': '#FFC0CB',
    'L9': '#800080', 'L10': '#00008B', 'L11': '#006400', 'L12': '#556B2F',
    'R': '#7B68EE'
}

LINEA_NOMBRES = {
    'L1': 'L1: Pinar de Chamartín – Valdecarros',
    'L2': 'L2: Las Rosas – Cuatro Caminos',
    'L3': 'L3: Villaverde Alto – Moncloa',
    'L4': 'L4: Argüelles – Pinar de Chamartín',
    'L5': 'L5: Alameda de Osuna – Casa de Campo',
    'L6': 'L6: Circular',
    'L7': 'L7: Hospital del Henares – Pitis',
    'L8': 'L8: Nuevos Ministerios – Aeropuerto T4',
    'L9': 'L9: Paco de Lucía – Arganda del Rey',
    'L10': 'L10: Hospital Infanta Sofía – Puerta del Sur',
    'L11': 'L11: Plaza Elíptica – La Fortuna',
    'L12': 'L12: MetroSur',
    'R': 'Ramal: Ópera – Príncipe Pío'
}

# === FUNCIONES PARA CARGAR DATOS ===

def cargar_datos():
    estaciones = gpd.read_file("Estaciones_filtrado.geojson")
    tramos = gpd.read_file("Tramos_filtrado.geojson")
    tiempos = pd.read_csv("tiempos_entre_estaciones.csv")
    return estaciones, tramos, tiempos

# === FUNCIONES PARA CREAR Y MODIFICAR EL GRAFO ===

def crear_grafo(estaciones):
    G = nx.Graph()
    for _, row in estaciones.iterrows():
        codigo = str(row['CODIGOESTACION']).strip().upper()
        G.add_node(codigo, nombre=row['DENOMINACION'], geometry=row['geometry'])
    return G

def agregar_tramos(G, tramos):
    tramos_sorted = tramos.sort_values(['CODIGOITINERARIO', 'NUMEROORDEN'])
    for _, grupo in tramos_sorted.groupby('CODIGOITINERARIO'):
        codigos = grupo['CODIGOESTACION'].astype(str).str.strip().str.upper().tolist()
        lineas = grupo['NUMEROLINEAUSUARIO'].tolist()
        for i in range(len(codigos) - 1):
            origen, destino = codigos[i], codigos[i + 1]
            linea = str(lineas[i])
            color = LINEA_COLORES.get(f'L{linea}', 'gray')
            if G.has_node(origen) and G.has_node(destino):
                G.add_edge(
                    origen, destino,
                    transbordo=False,
                    linea=f'L{linea}',
                    color=color
                )

def agregar_tiempos(G, tiempos_df):
    for _, row in tiempos_df.iterrows():
        origen = str(row['stop_id']).strip().upper()
        destino = str(row['siguiente_stop_id']).strip().upper()
        
        # Intentamos convertir el tiempo de HH:MM:SS a segundos
        try:
            # Convertir el tiempo en formato HH:MM:SS a segundos
            tiempo_str = row['tiempo_entre_estaciones']
            horas, minutos, segundos = map(int, tiempo_str.split(':'))
            tiempo = horas * 3600 + minutos * 60 + segundos  # Convertimos todo a segundos
        except ValueError:
            print(f"⚠️ Tiempo inválido entre {origen} y {destino}: {row['tiempo_entre_estaciones']}")
            continue

        if G.has_node(origen) and G.has_node(destino):
            if G.has_edge(origen, destino):
                G[origen][destino]['tiempo'] = tiempo
            else:
                G.add_edge(origen, destino, transbordo=False, linea=None, color='gray', tiempo=tiempo)



def agregar_transbordos(G, estaciones):
    estaciones['CODIGOESTACION'] = estaciones['CODIGOESTACION'].astype(str).str.strip().str.upper()
    nombre_a_codigos = estaciones.groupby('DENOMINACION')['CODIGOESTACION'].apply(list)
    for codigos in nombre_a_codigos:
        for origen, destino in combinations(codigos, 2):
            if G.has_node(origen) and G.has_node(destino):
               G.add_edge(origen, destino, transbordo=True, tiempo=240)
    return nombre_a_codigos

def agregar_transbordo_manual(G, nombre_a_codigos, origen_nom, destino_nom):
    for origen in nombre_a_codigos.get(origen_nom.upper(), []):
        for destino in nombre_a_codigos.get(destino_nom.upper(), []):
            if G.has_node(origen) and G.has_node(destino):
               G.add_edge(origen, destino, transbordo=True, tiempo=240)

def agregar_ramal(G, nombre_a_codigos, origen_nom, destino_nom):
    def solo_transbordos(nodo):
        return all(G[nodo][vecino].get('transbordo') for vecino in G.neighbors(nodo))
    
    origenes = [n for n in nombre_a_codigos.get(origen_nom.upper(), []) if solo_transbordos(n)]
    destinos = [n for n in nombre_a_codigos.get(destino_nom.upper(), []) if solo_transbordos(n)]
    
    for o in origenes:
        for d in destinos:
            G.add_edge(o, d, transbordo=False, linea='R', color=LINEA_COLORES['R'])

def obtener_posiciones(G):
    return {n: (d['geometry'].x, d['geometry'].y) for n, d in G.nodes(data=True)}

def asignar_color_nodos(G):
    for node in G.nodes():
        lineas_conectadas = {
            G[node][vecino].get('linea')
            for vecino in G.neighbors(node)
            if not G[node][vecino].get('transbordo')
        }
        lineas_conectadas.discard(None)
        G.nodes[node]['color'] = LINEA_COLORES.get(list(lineas_conectadas)[0], '#444444') if len(lineas_conectadas) == 1 else '#444444'

import heapq

def calcular_multiples_caminos(G, nombre_a_codigos, origen_nombre, destino_nombre, cantidad=3):
    origenes = nombre_a_codigos.get(origen_nombre.upper())
    destinos = nombre_a_codigos.get(destino_nombre.upper())

    if not origenes:
        print(f"❌ No se encontró la estación de origen: {origen_nombre}")
        return
    if not destinos:
        print(f"❌ No se encontró la estación de destino: {destino_nombre}")
        return

    caminos_encontrados = []

    for o in origenes:
        for d in destinos:
            queue = [(0, [o])]
            visitados = set()

            while queue and len(caminos_encontrados) < cantidad:
                costo_total, camino_actual = heapq.heappop(queue)
                ultimo = camino_actual[-1]

                if (tuple(camino_actual), ultimo) in visitados:
                    continue
                visitados.add((tuple(camino_actual), ultimo))

                if ultimo == d:
                    caminos_encontrados.append((camino_actual, costo_total))
                    continue

                for vecino in G.neighbors(ultimo):
                    if vecino not in camino_actual:  # evitar ciclos
                        tiempo = G[ultimo][vecino].get("tiempo", 0)
                        heapq.heappush(queue, (costo_total + tiempo, camino_actual + [vecino]))

    if caminos_encontrados:
        print(f"\n✅ Se encontraron {len(caminos_encontrados)} caminos entre {origen_nombre} y {destino_nombre}:")
        for idx, (camino, tiempo_total) in enumerate(sorted(caminos_encontrados, key=lambda x: x[1]), 1):
            print(f"\n🔀 Camino {idx} (tiempo total: {tiempo_total // 60:.0f} min {tiempo_total % 60:.0f} s):")
            tiempo_acumulado = 0
            for i, codigo in enumerate(camino):
                nombre_estacion = G.nodes[codigo].get('nombre', '???')
                print(f" - {codigo}: {nombre_estacion}")
                if i < len(camino) - 1:
                    tramo_tiempo = G[codigo][camino[i + 1]].get('tiempo', 0)
                    tiempo_acumulado += tramo_tiempo
                    print(f"   ⏱️ +{tramo_tiempo} s → Total: {tiempo_acumulado} s")
    else:
        print(f"⚠️ No se encontró ningún camino entre {origen_nombre} y {destino_nombre}")


# === FUNCIONES DE DIBUJO DEL GRAFO ===

def dibujar_grafo(G, pos, mostrar_tiempos=False):
    plt.figure(figsize=(15, 12))
    
    # Dibujo de las líneas
    linea_edges = {}
    for u, v, d in G.edges(data=True):
        if not d.get('transbordo'):
            color = d.get('color', 'gray')
            linea_edges.setdefault(color, []).append((u, v))
    for color, edges in linea_edges.items():
        nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=color, width=2, alpha=0.6)

    # Dibujo de transbordos
    transbordo_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('transbordo')]
    nx.draw_networkx_edges(G, pos, edgelist=transbordo_edges, edge_color='black', style='dashed', alpha=0.6)

    # Dibujo de nodos y etiquetas
    node_colors = [G.nodes[n].get('color', 'gray') for n in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_size=60, node_color=node_colors)
    labels = {n: d['nombre'] for n, d in G.nodes(data=True)}
    nx.draw_networkx_labels(G, pos, labels, font_size=6)

    # Mostrar tiempos
    if mostrar_tiempos:
        edge_labels = {
            (u, v): f"{d['tiempo']} s"
            for u, v, d in G.edges(data=True)
            if 'tiempo' in d
        }
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)

    # Leyenda
    plt.scatter([], [], c='blue', label='Estaciones')  # Placeholder
    plt.plot([], [], color='black', linestyle='dashed', label='Transbordos')
    for codigo, nombre in LINEA_NOMBRES.items():
        plt.plot([], [], color=LINEA_COLORES[codigo], linewidth=3, label=nombre)

    plt.legend(loc='upper right', fontsize=8)
    plt.title("Mapa del Metro de Madrid (Grafo por líneas)", fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.show()

# === MAIN ===

def main():
    estaciones, tramos, tiempos = cargar_datos()
    G = crear_grafo(estaciones)
    agregar_tramos(G, tramos)
    agregar_tiempos(G, tiempos)
    nombre_a_codigos = agregar_transbordos(G, estaciones)
    agregar_transbordo_manual(G, nombre_a_codigos, "NOVICIADO", "PLAZA DE ESPAÑA")
    agregar_ramal(G, nombre_a_codigos, "OPERA", "PRINCIPE PIO")
    pos = obtener_posiciones(G)
    asignar_color_nodos(G)

    mostrar_tiempos = input("¿Deseas mostrar los tiempos en el grafo? (s/n): ").strip().lower() == 's'
    dibujar_grafo(G, pos, mostrar_tiempos)

    print("\n=== Cálculo de ruta más corta ===")
    while True:
        origen_usuario = input("Estación de origen: ")
        destino_usuario = input("Estación de destino: ")
        calcular_multiples_caminos(G, nombre_a_codigos, origen_usuario, destino_usuario)


        continuar = input("\n¿Quieres calcular otro viaje? (s/n): ").strip().lower()
        if continuar != 's':
            print("👋 ¡Hasta luego! Gracias por usar el sistema.")
            break


if __name__ == "__main__":
    main()
