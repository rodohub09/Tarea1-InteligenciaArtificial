from collections import deque
from src.base_map.celda import EstadoCelda


def busqueda_bfs(mapa, inicio=None):
    """
    Ejecuta el algoritmo de Búsqueda en Anchura (BFS).
    Movimientos ortogonales: Arriba (-1,0), Abajo (1,0), Izquierda (0,-1), Derecha (0,1).
    Retorna un diccionario con el resultado de la búsqueda:
    - 'exito': bool
    - 'camino': list de tuplas (fila, columna) desde inicio hasta salida
    - 'costo_total': costo acumulado del camino
    - 'nodos_visitados': cantidad de nodos explorados
    """
    pos_inicio = inicio if inicio else mapa.inicio
    salida = mapa.salida

    if not pos_inicio or not salida:
        return {"exito": False, "camino": [], "costo_total": float('inf'), "nodos_visitados": 0}

    # Cola FIFO: almacena elementos (posicion_actual, camino_recorrido, costo_acumulado)
    cola = deque([(pos_inicio, [pos_inicio], 0)])
    visitados = set([pos_inicio])

    # 4 Direcciones ortogonales: Arriba, Abajo, Izquierda, Derecha
    movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while cola:
        pos_actual, camino, costo = cola.popleft()

        # Si llegamos a la salida
        if pos_actual == salida:
            return {
                "exito": True,
                "camino": camino,
                "costo_total": costo,
                "nodos_visitados": len(visitados)
            }

        r, c = pos_actual

        for dr, dc in movimientos:
            nr, nc = r + dr, c + dc
            pos_vecino = (nr, nc)

            if pos_vecino in visitados:
                continue

            celda = mapa.obtener_celda(nr, nc)
            if celda is None:
                continue

            estado = celda.obtener_estado()
            # Verificar si la celda es transitable (no es muro, fuego u ocupado)
            if estado not in [EstadoCelda.MURO, EstadoCelda.FUEGO, EstadoCelda.OCUPADO]:
                visitados.add(pos_vecino)
                costo_paso = celda.obtener_costo()
                cola.append((pos_vecino, camino + [pos_vecino], costo + costo_paso))

    return {
        "exito": False,
        "camino": [],
        "costo_total": float('inf'),
        "nodos_visitados": len(visitados)
    }
