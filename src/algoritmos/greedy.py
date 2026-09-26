import heapq
from src.base_map.celda import EstadoCelda


def heuristica_manhattan(pos, pos_meta):
    return abs(pos[0] - pos_meta[0]) + abs(pos[1] - pos_meta[1])


def busqueda_greedy(mapa, inicio=None):
    """
    Ejecuta el algoritmo de Búsqueda Avara (Greedy Best-First Search) 
    utilizando la distancia de Manhattan como heurística.
    f(n) = h(n)
    """
    pos_inicio = inicio if inicio else mapa.inicio
    salida = mapa.salida

    if not pos_inicio or not salida:
        return {"exito": False, "camino": [], "costo_total": float('inf'), "nodos_visitados": 0}

    # Cola de prioridad (heapq): almacena (h_val, contador, pos_actual, camino, costo_acumulado)
    contador = 0
    h_inicio = heuristica_manhattan(pos_inicio, salida)
    pq = [(h_inicio, contador, pos_inicio, [pos_inicio], 0)]

    visitados = set([pos_inicio])

    movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while pq:
        h_val, _, pos_actual, camino, costo_acum = heapq.heappop(pq)

        if pos_actual == salida:
            return {
                "exito": True,
                "camino": camino,
                "costo_total": costo_acum,
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
            # Verificar si la celda es transitable
            if estado not in [EstadoCelda.MURO, EstadoCelda.FUEGO, EstadoCelda.OCUPADO]:
                visitados.add(pos_vecino)
                costo_paso = celda.obtener_costo()
                nuevo_h = heuristica_manhattan(pos_vecino, salida)

                contador += 1
                heapq.heappush(pq, (nuevo_h, contador, pos_vecino, camino + [pos_vecino], costo_acum + costo_paso))

    return {
        "exito": False,
        "camino": [],
        "costo_total": float('inf'),
        "nodos_visitados": len(visitados)
    }
