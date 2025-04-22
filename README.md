# Grafo Metro Madrid

Este repositorio contiene un script para calcular las tres rutas más rápidas entre estaciones de metro, utilizando datos del Consorcio Regional de Transportes de Madrid (CRTM).

## Archivos necesarios (ya incluidos)

- `Estaciones_filtrado.geojson`  
- `Tramos_filtrado.geojson`  
- `tiempos_entre_estaciones.csv`  

Estos archivos ya han sido limpiados y preparados, por lo que no necesitas ejecutar los scripts auxiliares a menos que quieras trabajar con los datos originales descargados del CRTM.

## Requisitos

Asegúrate de tener las siguientes bibliotecas instaladas:

pip install pandas geopandas networkx matplotlib heapq


## Cómo ejecutar

1. Coloca los archivos filtrados en la misma carpeta que `grafo_metro.py`.
2. Ejecuta el programa.
3. El programa te preguntará si quieres visualizar el grafo **con tiempos (ponderado)** o **sin tiempos**.  
4. Te pedirá la **estación de origen** y la **de destino** (recuerda: en **MAYÚSCULAS y SIN TILDES**).  
5. Mostrará las **tres rutas más rápidas**, con sus tiempos individuales, el tiempo total y el camino recorrido.  
6. Podrás hacer nuevas consultas si lo deseas.
