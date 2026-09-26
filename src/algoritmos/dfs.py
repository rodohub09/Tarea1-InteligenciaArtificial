from src.base_map.celda import EstadoCelda


def busqueda_dfs(mapa, inicio=None):
    """
    Ejecuta el algoritmo de Búsqueda en Profundidad (DFS).
    """
    pos_inicio = inicio if inicio else mapa.inicio
    salida = mapa.salida

    if not pos_inicio or not salida:
        return {"exito": False, "camino": [], "costo_total": float('inf'), "nodos_visitados": 0}

    # Pila LIFO: almacena elementos (posicion_actual, camino_recorrido, costo_acumulado)
    pila = [(pos_inicio, [pos_inicio], 0)]
    visitados = set([pos_inicio])

    movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while pila:
        pos_actual, camino, costo = pila.pop()

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
            # Verificar si la celda es transitable
            if estado not in [EstadoCelda.MURO, EstadoCelda.FUEGO, EstadoCelda.OCUPADO]:
                visitados.add(pos_vecino)
                costo_paso = celda.obtener_costo()
                pila.append((pos_vecino, camino + [pos_vecino], costo + costo_paso))

    return {
        "exito": False,
        "camino": [],
        "costo_total": float('inf'),
        "nodos_visitados": len(visitados)
    }
