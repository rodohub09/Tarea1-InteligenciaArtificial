import math
import random
from .celda import Celda, EstadoCelda


class Mapa:
    """
    Representa la matriz del mapa y su carga desde un archivo .txt.
    Coloca exactamente 1 celda de fuego aleatoria a un radio >= 5 del inicio y salida.
    """

    def __init__(self, ruta_archivo=None):
        self.matriz = []
        self.filas = 0
        self.columnas = 0
        self.inicio = None  # Tupla (fila, columna)
        self.salida = None  # Tupla (fila, columna)

        if ruta_archivo:
            self.cargar_mapa(ruta_archivo)

    def cargar_mapa(self, ruta_archivo):
        """
        Lee un archivo .txt y genera la matriz de celdas del mapa.
        Símbolos:
        - M / #: Muro (MURO)
        - P / .: Pasillo (PASILLO)
        - I / S: Inicio de agentes (PASILLO, es_inicio = True)
        - E / X: Salida de escape (PASILLO, es_salida = True)
        - F    : Pasillo candidato para el fuego
        """
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            lineas = [linea.strip() for linea in f if linea.strip()]

        self.matriz = []
        self.filas = len(lineas)
        self.columnas = 0

        for r, linea in enumerate(lineas):
            fila_celdas = []
            caracteres = linea.split() if ' ' in linea else list(linea)
            self.columnas = len(caracteres)

            for c, char in enumerate(caracteres):
                simbolo = char.upper()

                if simbolo in ['M', '#']:
                    celda = Celda(r, c, EstadoCelda.MURO)
                elif simbolo in ['I', 'S']:
                    celda = Celda(r, c, EstadoCelda.PASILLO)
                    celda.es_inicio = True
                    self.inicio = (r, c)
                elif simbolo in ['E', 'X']:
                    celda = Celda(r, c, EstadoCelda.PASILLO)
                    celda.es_salida = True
                    self.salida = (r, c)
                elif simbolo in ['P', '.', 'F']:
                    celda = Celda(r, c, EstadoCelda.PASILLO)
                else:
                    celda = Celda(r, c, EstadoCelda.MURO)

                fila_celdas.append(celda)

            self.matriz.append(fila_celdas)

        # Colocar exactamente 1 fuego en una posición válida
        self._colocar_fuego_unico()

    def _colocar_fuego_unico(self):
        """
        Selecciona exactamente 1 celda aleatoria de tipo PASILLO a radio de distancia >= 5
        tanto del inicio como de la salida para convertirla en FUEGO.
        """
        candidatos = []

        for r in range(self.filas):
            for c in range(self.columnas):
                celda = self.matriz[r][c]

                if celda.estado_base == EstadoCelda.PASILLO and not celda.es_inicio and not celda.es_salida:
                    dist_inicio = self._calcular_distancia(r, c, self.inicio)
                    dist_salida = self._calcular_distancia(r, c, self.salida)

                    if dist_inicio >= 5 and dist_salida >= 5:
                        candidatos.append(celda)

        if candidatos:
            celda_fuego = random.choice(candidatos)
            celda_fuego.estado_base = EstadoCelda.FUEGO

    def _calcular_distancia(self, r, c, pos_referencia):
        if pos_referencia is None:
            return float('inf')
        ref_r, ref_c = pos_referencia
        return math.sqrt((r - ref_r) ** 2 + (c - ref_c) ** 2)

    def obtener_celda(self, fila, columna):
        if 0 <= fila < self.filas and 0 <= columna < self.columnas:
            return self.matriz[fila][columna]
        return None
