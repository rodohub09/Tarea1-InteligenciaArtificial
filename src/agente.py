from src.algoritmos.bfs import busqueda_bfs
from src.algoritmos.dfs import busqueda_dfs
from src.base_map.celda import EstadoCelda


class Agente:

    def __init__(self, id_agente, mapa, posicion_inicial=None):
        self.id_agente = id_agente
        self.mapa = mapa
       
        self.posicion_actual = posicion_inicial if posicion_inicial else mapa.inicio
        self.camino = []
        self.costo_total = 0
        self.ha_escapado = False
        self.inhabilitado = False

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

        celda_actual = self.mapa.obtener_celda(r, c)
        if celda_actual and celda_actual.obtener_costo() != float('inf'):
            movimientos.append((r, c))

        return movimientos

    def buscar_camino(self, algoritmo="bfs"):
        if self.verificar_estado():
            return {"exito": False, "camino": [], "costo_total": float('inf'), "nodos_visitados": 0, "mensaje": "Agente inhabilitado por fuego"}

        algoritmos_disponibles = {
            "bfs": busqueda_bfs,
            "dfs": busqueda_dfs
        }

        nombre_alg = algoritmo.lower()
        if nombre_alg not in algoritmos_disponibles:
            raise ValueError(f"Algoritmo '{algoritmo}' no reconocido. Opciones: {list(algoritmos_disponibles.keys())}")

        funcion_busqueda = algoritmos_disponibles[nombre_alg]
        resultado = funcion_busqueda(self.mapa, inicio=self.posicion_actual)

        if resultado["exito"]:
            self.camino = resultado["camino"]
            self.costo_total = resultado["costo_total"]

        return resultado

    def esperar(self):
        if self.verificar_estado():
            return False

        celda_actual = self.mapa.obtener_celda(*self.posicion_actual)
        if celda_actual:
            self.costo_total += celda_actual.obtener_costo()
        return True

    def mover_a(self, nueva_posicion):
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
