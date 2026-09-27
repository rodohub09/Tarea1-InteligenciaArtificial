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
    - Las celdas pasillo normales pueden contener hasta 3 agentes antes de cambiar a OCUPADO.
    - Las celdas de INICIO y SALIDA no tienen límite de agentes (permiten albergar múltiples agentes simultáneamente).
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
        Las celdas de INICIO y SALIDA nunca pasan a estado OCUPADO por límite de agentes.
        Las celdas de PASILLO normales pasan a OCUPADO si tienen 3 o más agentes.
        """
        if self.es_inicio or self.es_salida:
            return self.estado_base
        if self.estado_base == EstadoCelda.PASILLO and self.agentes >= 3:
            return EstadoCelda.OCUPADO
        return self.estado_base

    def obtener_costo(self, costo_base=1, penalizacion_por_agente=2):
        """
        Calcula y retorna la función de costo asociada a la celda.
        - Si la celda es MURO, FUEGO u OCUPADO: costo infinito (float('inf')).
        - Si es la celda de INICIO o SALIDA: costo_base fijo.
        - Si es PASILLO normal: costo_base + (agentes * penalizacion_por_agente).
        """
        estado = self.obtener_estado()
        if estado in [EstadoCelda.MURO, EstadoCelda.FUEGO, EstadoCelda.OCUPADO]:
            return float('inf')
        if self.es_inicio or self.es_salida:
            return costo_base
        return costo_base + (self.agentes * penalizacion_por_agente)

    def agregar_agente(self):
        """
        Agrega un agente a la celda.
        Las celdas de INICIO y SALIDA no tienen límite de capacidad.
        Las celdas de pasillo normales tienen un límite de máximo 3 agentes.
        """
        if self.estado_base != EstadoCelda.PASILLO:
            return False
        if self.es_inicio or self.es_salida:
            self.agentes += 1
            return True
        if self.agentes < 3:
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
