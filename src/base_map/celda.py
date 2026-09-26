from enum import Enum


class EstadoCelda(Enum):
    """
    Estados posibles para una celda del mapa.
    """
    MURO = "MURO"
    PASILLO = "PASILLO"
    FUEGO = "FUEGO"
    OCUPADO = "OCUPADO"


class Celda:
    """
    Representa una celda del mapa.
    Un pasillo puede contener hasta 3 agentes antes de cambiar a OCUPADO.
    El costo de tránsito de la celda es una función asociada a la cantidad de agentes en ella.
    """

    def __init__(self, fila, columna, estado=EstadoCelda.PASILLO):
        self.fila = fila
        self.columna = columna
        self.estado_base = estado  # EstadoCelda.MURO, EstadoCelda.PASILLO, etc.
        self.agentes = 0
        self.es_inicio = False
        self.es_salida = False

    def obtener_estado(self):
        """
        Retorna el estado actual de la celda.
        Si es un PASILLO con 3 o más agentes, su estado pasa a ser OCUPADO.
        """
        if self.estado_base == EstadoCelda.PASILLO and self.agentes >= 3:
            return EstadoCelda.OCUPADO
        return self.estado_base

    def obtener_costo(self, costo_base=1, penalizacion_por_agente=2):
        """
        Calcula y retorna la función de costo asociada a la celda según la cantidad de agentes.
        - Si la celda es MURO, FUEGO u OCUPADO (>= 3 agentes): costo infinito (float('inf')).
        - Si es PASILLO: costo_base + (agentes * penalizacion_por_agente).
        """
        estado = self.obtener_estado()
        if estado in [EstadoCelda.MURO, EstadoCelda.FUEGO, EstadoCelda.OCUPADO]:
            return float('inf')
        return costo_base + (self.agentes * penalizacion_por_agente)

    def agregar_agente(self):
        """
        Agrega un agente si la celda es PASILLO y no ha alcanzado la capacidad (máximo 3).
        """
        if self.estado_base == EstadoCelda.PASILLO and self.agentes < 3:
            self.agentes += 1
            return True
        return False

    def remover_agente(self):
        """
        Remueve un agente de la celda.
        """
        if self.agentes > 0:
            self.agentes -= 1
            return True
        return False
