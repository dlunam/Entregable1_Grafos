import geopandas as gpd
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations

# === COLORES Y METADATOS DE LÍNEAS ===

linea_colores = {
    'L1': '#00BFFF', 'L2': '#FF0000', 'L3': '#FFFF00', 'L4': '#A0522D',
    'L5': '#90EE90', 'L6': '#808080', 'L7': '#FFA500', 'L8': '#FFC0CB',
    'L9': '#800080', 'L10': '#00008B', 'L11': '#006400', 'L12': '#556B2F',
    'R': '#7B68EE'  
}

linea_nombres = {
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

# === FUNCIONES ===

def cargar_datos():
    estaciones = gpd.read_file("Estaciones_filtrado.geojson")
    tramos = gpd.read_file("Tramos_filtrado.geojson")
    return estaciones, tramos

def cargar_tiempos():
    df = pd.read_csv("tiempos_entre_estaciones.csv")
    # Asegurar que los IDs sean string para comparación segura
    df['stop_id'] = df['stop_id'].astype(str)
    df['siguiente_stop_id'] = df['siguiente_stop_id'].astype(str)
    return df

def crear_grafo(estaciones):
    G = nx.Graph()
    for _, row in estaciones.iterrows():
        G.add_node(
            str(row['CODIGOESTACION']),
            nombre=row['DENOMINACION'],
            geometry=row['geometry']
        )
    return G

def agregar_tramos(G, tramos):
    tramos_sorted = tramos.sort_values(['CODIGOITINERARIO', 'NUMEROORDEN'])
    for _, grupo in tramos_sorted.groupby('CODIGOITINERARIO'):
        codigos = grupo['CODIGOESTACION'].astype(str).tolist()
        lineas = grupo['NUMEROLINEAUSUARIO'].astype(str).tolist()
        for i in range(len(codigos) - 1):
            origen, destino = codigos[i], codigos[i + 1]
            linea = f'L{lineas[i]}'
            color = linea_colores.get(linea, 'gray')
            if G.has_node(origen) and G.has_node(destino):
                G.add_edge(
                    origen, destino,
                    transbordo=False,
                    linea=linea,
                    color=color,
                    weight=None  # se asignará después
                )

def agregar_tiempos(G, tiempos_df):
    for _, row in tiempos_df.iterrows():
        origen = str(row['stop_id'])
        destino = str(row['siguiente_stop_id'])
        tiempo = row['tiempo_entre_estaciones']
        if G.has_edge(origen, destino):
            G[origen][destino]['weight'] = tiempo

def agregar_transbordos(G, estaciones, peso_transbordo=5):
    nombre_a_codigos = estaciones.groupby('DENOMINACION')['CODIGOESTACION'].apply(lambda x: list(map(str, x)))
    for codigos in nombre_a_codigos:
        for origen, destino in combinations(codigos, 2):
            if G.has_node(origen) and G.has_node(destino):
                G.add_edge(origen, destino, transbordo=True, weight=peso_transbordo)
    return nombre_a_codigos

def agregar_transbordo_manual(G, nombre_a_codigos, origen_nom, destino_nom, peso_transbordo=5):
    for origen in nombre_a_codigos.get(origen_nom.upper(), []):
        for destino in nombre_a_codigos.get(destino_nom.upper(), []):
            if G.has_node(origen) and G.has_node(destino):
                G.add_edge(origen, destino, transbordo=True, weight=peso_transbordo)

def agregar_ramal(G, nombre_a_codigos, origen_nom, destino_nom):
    def solo_transbordos(nodo):
        return all(G[nodo][vecino].get('transbordo') for vecino in G.neighbors(nodo))
    
    origenes = [n for n in nombre_a_codigos.get(origen_nom.upper(), []) if solo_transbordos(n)]
    destinos = [n for n in nombre_a_codigos.get(destino_nom.upper(), []) if solo_transbordos(n)]
    
    for o in origenes:
        for d in destinos:
            G.add_edge(o, d, transbordo=False, linea='R', color=linea_colores['R'], weight=2)  # peso aproximado

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
        if len(lineas_conectadas) == 1:
            linea = list(lineas_conectadas)[0]
            G.nodes[node]['color'] = linea_colores.get(linea, 'gray')
        else:
            G.nodes[node]['color'] = '#444444'  # gris oscuro

def dibujar_grafo(G, pos):
    plt.figure(figsize=(15, 12))
    
    linea_edges = {}
    for u, v, d in G.edges(data=True):
        if not d.get('transbordo'):
            color = d.get('color', 'gray')
            linea_edges.setdefault(color, []).append((u, v))
    for color, edges in linea_edges.items():
        nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=color, width=2, alpha=0.6)

    transbordo_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('transbordo')]
    nx.draw_networkx_edges(G, pos, edgelist=transbordo_edges, edge_color='black', style='dashed', alpha=0.6)

    node_colors = [G.nodes[n].get('color', 'gray') for n in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_size=60, node_color=node_colors)

    labels = {n: d['nombre'] for n, d in G.nodes(data=True)}
    nx.draw_networkx_labels(G, pos, labels, font_size=6)

    plt.scatter([], [], c='blue', label='Estaciones')  # Placeholder
    plt.plot([], [], color='black', linestyle='dashed', label='Transbordos')

    for codigo, nombre in linea_nombres.items():
        plt.plot([], [], color=linea_colores[codigo], linewidth=3, label=nombre)

    plt.legend(loc='upper right', fontsize=8)
    plt.title("Mapa del Metro de Madrid (Grafo ponderado por tiempo)", fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.show()

# === MAIN ===

estaciones, tramos = cargar_datos()
tiempos_df = cargar_tiempos()

G = crear_grafo(estaciones)
agregar_tramos(G, tramos)
agregar_tiempos(G, tiempos_df)

nombre_a_codigos = agregar_transbordos(G, estaciones, peso_transbordo=5)
agregar_transbordo_manual(G, nombre_a_codigos, "NOVICIADO", "PLAZA DE ESPAÑA", peso_transbordo=5)
agregar_ramal(G, nombre_a_codigos, "OPERA", "PRINCIPE PIO")

pos = obtener_posiciones(G)
asignar_color_nodos(G)
dibujar_grafo(G, pos)

# Ver tiempos de viaje entre algunas estaciones
for u, v, d in G.edges(data=True):
    if not d['transbordo']:
        print(f"{G.nodes[u]['nombre']} - {G.nodes[v]['nombre']}: {d['weight']} min")
        #break  # quita el break si quieres ver más
