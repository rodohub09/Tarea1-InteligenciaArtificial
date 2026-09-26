from src.algoritmos.bfs import busqueda_bfs
from src.algoritmos.dfs import busqueda_dfs
from src.algoritmos.astar import busqueda_astar
from src.algoritmos.greedy import busqueda_greedy
from src.algoritmos.genetico import busqueda_genetica
from src.base_map.celda import EstadoCelda


class Agente:
    """
    Representa un agente de búsqueda para la simulación de escape de incendio.
    Soporta interacción multi-agente, movimientos ortogonales y búsqueda mediante
    algoritmos no informados (BFS, DFS), informados (A*, Greedy) y evolucionativos (Genético).
    """

    def __init__(self, id_agente, mapa, posicion_inicial=None):
        self.id_agente = id_agente
        self.mapa = mapa
        
        # Posición inicial: si no se especifica, usa la posición de inicio del mapa
        self.posicion_actual = posicion_inicial if posicion_inicial else mapa.inicio
        self.camino = []
        self.costo_total = 0
        self.ha_escapado = False
        self.inhabilitado = False

        # Registrar al agente en la celda inicial y verificar si la celda está en fuego
        if self.posicion_actual:
            celda_inicio = self.mapa.obtener_celda(*self.posicion_actual)
            if celda_inicio:
                celda_inicio.agregar_agente()
            self.verificar_estado()

    def verificar_estado(self):
        """
        Verifica si la celda actual del agente se ha incendiado.
        Si la celda está en FUEGO, el agente pasa a estar inhabilitado.
        """
        if self.inhabilitado:
            return True

        if self.posicion_actual:
            celda = self.mapa.obtener_celda(*self.posicion_actual)
            if celda and celda.obtener_estado() == EstadoCelda.FUEGO:
                self.inhabilitado = True

        return self.inhabilitado

    def obtener_movimientos_validos(self):
        """
        Retorna las posiciones vecinas válidas a las que se puede mover el agente.
        Si el agente está inhabilitado, no puede realizar ningún movimiento.
        """
        if self.verificar_estado():
            return []

        r, c = self.posicion_actual
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        movimientos = []

        for dr, dc in direcciones:
            nr, nc = r + dr, c + dc
            celda = self.mapa.obtener_celda(nr, nc)
            if celda and celda.obtener_costo() != float('inf'):
                movimientos.append((nr, nc))

        # Opción de esperar en la celda actual si la celda no es letal
        celda_actual = self.mapa.obtener_celda(r, c)
        if celda_actual and celda_actual.obtener_costo() != float('inf'):
            movimientos.append((r, c))

        return movimientos

    def buscar_camino(self, algoritmo="bfs"):
        """
        Ejecuta el algoritmo de búsqueda especificado desde la posición actual del agente.
        Opciones disponibles: 'bfs', 'dfs', 'astar' (o 'a*'), 'greedy', 'genetico' (o 'ga').
        """
        if self.verificar_estado():
            return {"exito": False, "camino": [], "costo_total": float('inf'), "nodos_visitados": 0, "mensaje": "Agente inhabilitado por fuego"}

        algoritmos_disponibles = {
            "bfs": busqueda_bfs,
            "dfs": busqueda_dfs,
            "astar": busqueda_astar,
            "a*": busqueda_astar,
            "greedy": busqueda_greedy,
            "genetico": busqueda_genetica,
            "ga": busqueda_genetica
        }

        nombre_alg = algoritmo.lower()
        if nombre_alg not in algoritmos_disponibles:
            raise ValueError(f"Algoritmo '{algoritmo}' no reconocido. Opciones disponibles: 'bfs', 'dfs', 'astar', 'greedy', 'genetico'")

        funcion_busqueda = algoritmos_disponibles[nombre_alg]
        resultado = funcion_busqueda(self.mapa, inicio=self.posicion_actual)

        if resultado["exito"]:
            self.camino = resultado["camino"]
            self.costo_total = resultado["costo_total"]

        return resultado

    def esperar(self):
        """
        Acción de esperar: el agente permanece en la posición actual durante 1 turno.
        Si la celda está en fuego, el agente pasa a estar inhabilitado.
        """
        if self.verificar_estado():
            return False

        celda_actual = self.mapa.obtener_celda(*self.posicion_actual)
        if celda_actual:
            self.costo_total += celda_actual.obtener_costo()
        return True

    def mover_a(self, nueva_posicion):
        """
        Mueve al agente a una nueva posición o espera si es la misma posición.
        Si la celda destino o actual está en fuego, el agente pasa a estar inhabilitado.
        """
        if self.verificar_estado():
            return False

        if nueva_posicion == self.posicion_actual:
            return self.esperar()

        celda_actual = self.mapa.obtener_celda(*self.posicion_actual)
        celda_nueva = self.mapa.obtener_celda(*nueva_posicion)

        if celda_nueva and celda_nueva.agregar_agente():
            if celda_actual:
                celda_actual.remover_agente()
            
            self.posicion_actual = nueva_posicion
            
            if self.verificar_estado():
                return False

            if nueva_posicion == self.mapa.salida:
                self.ha_escapado = True
                
            return True
        else:
            return self.esperar()
