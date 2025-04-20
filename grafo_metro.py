import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations

def cargar_datos():
    estaciones = gpd.read_file("Estaciones_filtrado.geojson")
    tramos = gpd.read_file("Tramos_filtrado.geojson")
    return estaciones, tramos

def crear_grafo(estaciones):
    G = nx.Graph()
    for _, row in estaciones.iterrows():
        G.add_node(
            row['CODIGOESTACION'],
            nombre=row['DENOMINACION'],
            geometry=row['geometry']
        )
    return G

def agregar_tramos(G, tramos):
    tramos_sorted = tramos.sort_values(['CODIGOITINERARIO', 'NUMEROORDEN'])
    for _, grupo in tramos_sorted.groupby('CODIGOITINERARIO'):
        codigos = grupo['CODIGOESTACION'].tolist()
        edges = zip(codigos, codigos[1:])
        for origen, destino in edges:
            if G.has_node(origen) and G.has_node(destino):
                G.add_edge(origen, destino, transbordo=False)

def agregar_transbordos(G, estaciones):
    nombre_a_codigos = estaciones.groupby('DENOMINACION')['CODIGOESTACION'].apply(list)
    for codigos in nombre_a_codigos:
        for origen, destino in combinations(codigos, 2):
            if G.has_node(origen) and G.has_node(destino):
                G.add_edge(origen, destino, transbordo=True)
    return nombre_a_codigos

def agregar_transbordo_manual(G, nombre_a_codigos, origen_nom, destino_nom):
    for origen in nombre_a_codigos.get(origen_nom.upper(), []):
        for destino in nombre_a_codigos.get(destino_nom.upper(), []):
            if G.has_node(origen) and G.has_node(destino):
                G.add_edge(origen, destino, transbordo=True)

def agregar_ramal(G, nombre_a_codigos, origen_nom, destino_nom):
    def solo_transbordos(nodo):
        return all(G[nodo][vecino].get('transbordo') for vecino in G.neighbors(nodo))
    
    origenes = [n for n in nombre_a_codigos.get(origen_nom.upper(), []) if solo_transbordos(n)]
    destinos = [n for n in nombre_a_codigos.get(destino_nom.upper(), []) if solo_transbordos(n)]
    
    for o in origenes:
        for d in destinos:
            G.add_edge(o, d, transbordo=False)

def obtener_posiciones(G):
    return {n: (d['geometry'].x, d['geometry'].y) for n, d in G.nodes(data=True)}

def dibujar_grafo(G, pos):
    plt.figure(figsize=(15, 12))
    
    # Aristas
    normales = [(u, v) for u, v, d in G.edges(data=True) if not d.get('transbordo')]
    transbordos = [(u, v) for u, v, d in G.edges(data=True) if d.get('transbordo')]
    
    nx.draw_networkx_edges(G, pos, edgelist=normales, edge_color='gray', alpha=0.5)
    nx.draw_networkx_edges(G, pos, edgelist=transbordos, edge_color='black', style='dashed', alpha=0.6)
    
    # Nodos y etiquetas
    nx.draw_networkx_nodes(G, pos, node_size=50, node_color='blue')
    labels = {n: d['nombre'] for n, d in G.nodes(data=True)}
    nx.draw_networkx_labels(G, pos, labels, font_size=6, font_family="sans-serif")
    
    # Leyenda
    plt.scatter([], [], c='blue', label='Estaciones')
    plt.plot([], [], color='gray', label='Conexiones entre estaciones')
    plt.plot([], [], color='black', linestyle='dashed', label='Transbordos')
    plt.legend(loc='upper right')

    plt.title("Mapa del Metro de Madrid (Grafo de estaciones y tramos)", fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.show()

# === Main ===
estaciones, tramos = cargar_datos()
G = crear_grafo(estaciones)
agregar_tramos(G, tramos)
nombre_a_codigos = agregar_transbordos(G, estaciones)
agregar_transbordo_manual(G, nombre_a_codigos, "NOVICIADO", "PLAZA DE ESPAÑA")
agregar_ramal(G, nombre_a_codigos, "OPERA", "PRINCIPE PIO")
pos = obtener_posiciones(G)
dibujar_grafo(G, pos)