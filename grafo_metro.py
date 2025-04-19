import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt

# Leer archivos filtrados
estaciones = gpd.read_file("Estaciones_filtrado.geojson")
tramos = gpd.read_file("Tramos_filtrado.geojson")

# Crear grafo vacío no dirigido
G = nx.Graph()

# Añadir nodos con atributos (nombre, líneas, geometría)
for _, row in estaciones.iterrows():
    codigo = row['CODIGOESTACION']
    G.add_node(
        codigo,
        nombre=row['DENOMINACION'],
        lineas=row['LINEAS'],
        geometry=row['geometry']
    )

# Añadir aristas basadas en itinerarios y orden
tramos_sorted = tramos.sort_values(['CODIGOITINERARIO', 'NUMEROORDEN'])
grupos = tramos_sorted.groupby('CODIGOITINERARIO')

for _, grupo in grupos:
    codigos = grupo['CODIGOESTACION'].tolist()
    for i in range(len(codigos) - 1):
        origen = codigos[i]
        destino = codigos[i+1]
        if G.has_node(origen) and G.has_node(destino):
            G.add_edge(origen, destino)

# Preparar posiciones a partir de coordenadas
pos = {
    node: (data['geometry'].x, data['geometry'].y)
    for node, data in G.nodes(data=True)
}

# Dibujar grafo
plt.figure(figsize=(15, 12))

# Aristas (conexiones)
nx.draw_networkx_edges(G, pos, edge_color='gray', alpha=0.5)

# Nodos (estaciones)
nx.draw_networkx_nodes(G, pos, node_size=50, node_color='blue', label='Estaciones')

# Etiquetas (nombres de paradas)
labels = {node: data['nombre'] for node, data in G.nodes(data=True)}
nx.draw_networkx_labels(G, pos, labels, font_size=6, font_family="sans-serif")

# Leyenda manual
plt.scatter([], [], c='blue', label='Estaciones')
plt.plot([], [], color='gray', label='Conexiones entre estaciones')
plt.legend(loc='upper right')

plt.title("Mapa del Metro de Madrid (Grafo de estaciones y tramos)", fontsize=14)
plt.axis('off')
plt.tight_layout()
plt.show()
