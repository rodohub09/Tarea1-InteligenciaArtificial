import math
import sys
import statistics
import time
from collections import deque
from src.base_map.mapa import Mapa
from src.agente import Agente
from src.base_map.celda import EstadoCelda


class Simulacion:
    """
    Ejecuta una iteración/corrida de simulación para un algoritmo dado en un mapa.
    - 80 agentes simultáneos que inician en mapa.inicio.
    - Propagación de fuego cada 3 turnos.
    - Recorrido turno a turno respetando capacidad de celdas (3 por pasillo).
    """

    def __init__(self, ruta_mapa, algoritmo, num_agentes=80, max_turnos=300):
        self.ruta_mapa = ruta_mapa
        self.algoritmo = algoritmo
        self.num_agentes = num_agentes
        self.max_turnos = max_turnos

    def ejecutar(self):
        # 1. Cargar el mapa (genera 1 fuego aleatorio a radio >= 5)
        mapa = Mapa(self.ruta_mapa)

        # 2. Inicializar los 80 agentes en el punto de inicio
        agentes = [Agente(i + 1, mapa) for i in range(self.num_agentes)]

        # 3. Cachear cálculo de rutas para agentes en la misma posición inicial
        cache_rutas = {}
        rutas = {}
        for a in agentes:
            pos_ini = a.posicion_actual
            if pos_ini not in cache_rutas:
                res = a.buscar_camino(self.algoritmo)
                cache_rutas[pos_ini] = res
            else:
                res = cache_rutas[pos_ini]

            if res["exito"]:
                rutas[a.id_agente] = deque(res["camino"][1:])
            else:
                rutas[a.id_agente] = deque()

        turnos_escape = {}
        turno = 0

        # 4. Bucle principal por turnos
        while turno < self.max_turnos:
            turno += 1

            # Filtrar agentes activos (ni escapados ni inhabilitados)
            agentes_activos = [a for a in agentes if not a.ha_escapado and not a.inhabilitado]
            if not agentes_activos:
                break

            # A. Movimiento de cada agente activo en este turno
            for a in agentes_activos:
                if a.verificar_estado():
                    continue

                cola_pasos = rutas[a.id_agente]

                if cola_pasos:
                    siguiente_pos = cola_pasos[0]
                    exito_mov = a.mover_a(siguiente_pos)
                    
                    if exito_mov and a.posicion_actual == siguiente_pos:
                        cola_pasos.popleft()
                        if a.ha_escapado:
                            turnos_escape[a.id_agente] = turno
                    elif not exito_mov and not a.inhabilitado:
                        pos_pos = a.posicion_actual
                        if pos_pos not in cache_rutas:
                            nueva_busqueda = a.buscar_camino(self.algoritmo)
                            cache_rutas[pos_pos] = nueva_busqueda
                        else:
                            nueva_busqueda = cache_rutas[pos_pos]

                        if nueva_busqueda["exito"]:
                            rutas[a.id_agente] = deque(nueva_busqueda["camino"][1:])
                else:
                    if not a.ha_escapado:
                        pos_pos = a.posicion_actual
                        if pos_pos not in cache_rutas:
                            nueva_busqueda = a.buscar_camino(self.algoritmo)
                            cache_rutas[pos_pos] = nueva_busqueda
                        else:
                            nueva_busqueda = cache_rutas[pos_pos]

                        if nueva_busqueda["exito"] and len(nueva_busqueda["camino"]) > 1:
                            rutas[a.id_agente] = deque(nueva_busqueda["camino"][1:])
                            siguiente_pos = rutas[a.id_agente][0]
                            if a.mover_a(siguiente_pos) and a.posicion_actual == siguiente_pos:
                                rutas[a.id_agente].popleft()
                                if a.ha_escapado:
                                    turnos_escape[a.id_agente] = turno
                        else:
                            a.esperar()

            # B. Propagar el fuego cada 3 turnos (turno % 3 == 0)
            if turno % 3 == 0:
                mapa.propagar_fuego()
                # Invalidar caché de rutas tras propagación de fuego para recalcular si es necesario
                cache_rutas.clear()

                for a in agentes:
                    if not a.ha_escapado and not a.inhabilitado:
                        a.verificar_estado()

        # 5. Métricas de esta iteración
        supervivientes = sum(1 for a in agentes if a.ha_escapado)
        turno_ultimo_superviviente = max(turnos_escape.values()) if turnos_escape else None

        return {
            "supervivientes": supervivientes,
            "total_agentes": self.num_agentes,
            "turno_ultimo_superviviente": turno_ultimo_superviviente
        }


class Benchmark:
    """
    Ejecuta el benchmark completo con contador de iteraciones en tiempo real.
    """

    def __init__(self, ruta_mapa, num_iteraciones=200, num_agentes=80):
        self.ruta_mapa = ruta_mapa
        self.num_iteraciones = num_iteraciones
        self.num_agentes = num_agentes

    def evaluar_algoritmo(self, algoritmo):
        tiempo_inicio = time.time()
        total_supervivientes = 0
        turnos_ultimos_supervivientes = []

        for i in range(1, self.num_iteraciones + 1):
            sim = Simulacion(self.ruta_mapa, algoritmo, num_agentes=self.num_agentes)
            res = sim.ejecutar()

            total_supervivientes += res["supervivientes"]
            if res["turno_ultimo_superviviente"] is not None:
                turnos_ultimos_supervivientes.append(res["turno_ultimo_superviviente"])

            # Contador de iteraciones en tiempo real
            tiempo_transcurrido = time.time() - tiempo_inicio
            pct = (i / self.num_iteraciones) * 100.0
            
            bar_len = 20
            filled_len = int(bar_len * i // self.num_iteraciones)
            bar = '=' * filled_len + '-' * (bar_len - filled_len)

            progreso_str = (
                f"\r  [{algoritmo.upper():<7}] [{bar}] {i:>3}/{self.num_iteraciones} "
                f"({pct:5.1f}%) | Sup. en corrida: {res['supervivientes']:>2}/{self.num_agentes} "
                f"| Tiempo: {tiempo_transcurrido:6.1f}s"
            )
            sys.stdout.write(progreso_str)
            sys.stdout.flush()

        sys.stdout.write(f"\r  [{algoritmo.upper():<7}] Finalizado {self.num_iteraciones}/{self.num_iteraciones} en {time.time() - tiempo_inicio:.1f}s.                     \n")
        sys.stdout.flush()

        tiempo_total = time.time() - tiempo_inicio
        pct_supervivencia = (total_supervivientes / (self.num_agentes * self.num_iteraciones)) * 100.0

        if turnos_ultimos_supervivientes:
            media = statistics.mean(turnos_ultimos_supervivientes)
            std_dev = statistics.stdev(turnos_ultimos_supervivientes) if len(turnos_ultimos_supervivientes) > 1 else 0.0
            val_min = min(turnos_ultimos_supervivientes)
            val_max = max(turnos_ultimos_supervivientes)
        else:
            media = 0.0
            std_dev = 0.0
            val_min = 0
            val_max = 0

        return {
            "algoritmo": algoritmo.upper(),
            "pct_supervivencia": pct_supervivencia,
            "media_ultimo_superviviente": media,
            "std_ultimo_superviviente": std_dev,
            "min_ultimo_superviviente": val_min,
            "max_ultimo_superviviente": val_max,
            "corridas_con_supervivientes": len(turnos_ultimos_supervivientes),
            "tiempo_segundos": tiempo_total
        }

    def ejecutar_todos(self, algoritmos=None):
        if algoritmos is None:
            algoritmos = ["bfs", "dfs", "astar", "greedy", "genetico"]

        resultados = []
        for alg in algoritmos:
            res = self.evaluar_algoritmo(alg)
            resultados.append(res)

        return resultados


def imprimir_reporte(nombre_escenario, resultados):
    print(f"\n==========================================================================================")
    print(f" BENCHMARK REPORT - ESCENARIO: {nombre_escenario}")
    print(f" Configuración: 80 agentes | 200 iteraciones | Propagación fuego cada 3 turnos")
    print(f"==========================================================================================\n")

    header = f"| {'Algoritmo':<10} | {'Supervivencia (%)':<18} | {'Media Ult. Sup.':<16} | {'Std Dev':<10} | {'Mín':<6} | {'Máx':<6} | {'Tiempo (s)':<10} |"
    sep = "|------------|--------------------|------------------|------------|--------|--------|------------|"
    
    print(header)
    print(sep)

    for r in resultados:
        row = (
            f"| {r['algoritmo']:<10} "
            f"| {r['pct_supervivencia']:>17.2f}% "
            f"| {r['media_ultimo_superviviente']:>16.2f} "
            f"| {r['std_ultimo_superviviente']:>10.2f} "
            f"| {r['min_ultimo_superviviente']:>6} "
            f"| {r['max_ultimo_superviviente']:>6} "
            f"| {r['tiempo_segundos']:>10.2f} |"
        )
        print(row)
    print(sep + "\n")
