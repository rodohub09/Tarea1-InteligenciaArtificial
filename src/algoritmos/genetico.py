import os
import json
import random
import math
from src.base_map.celda import EstadoCelda

# Movimientos posibles (genes): 0=Arriba, 1=Abajo, 2=Izquierda, 3=Derecha, 4=Esperar
DIRECCIONES = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

# Movimientos opuestos directos para evitar bucles (0<->1, 2<->3)
OPUESTOS = {0: 1, 1: 0, 2: 3, 3: 2, 4: None}

MODELO_GA_PATH = os.path.join("models", "ga_model.json")
_CACHE_MODELO_GA = None


def cargar_modelo_entrenado():
    """
    Carga el modelo guardado del algoritmo genético desde models/ga_model.json.
    """
    global _CACHE_MODELO_GA
    if _CACHE_MODELO_GA is not None:
        return _CACHE_MODELO_GA

    if os.path.exists(MODELO_GA_PATH):
        try:
            with open(MODELO_GA_PATH, 'r', encoding='utf-8') as f:
                _CACHE_MODELO_GA = json.load(f)
                return _CACHE_MODELO_GA
        except Exception:
            return None
    return None


def heuristica_manhattan(pos, pos_meta):
    return abs(pos[0] - pos_meta[0]) + abs(pos[1] - pos_meta[1])


def gen_guiado(pos_actual, pos_meta, ultimo_gen=None):
    """
    Genera un gen con tendencia estocástica hacia la salida evitando el movimiento opuesto.
    """
    dr = pos_meta[0] - pos_actual[0]
    dc = pos_meta[1] - pos_actual[1]
    opuesto = OPUESTOS.get(ultimo_gen, None)

    opciones = []
    if dr < 0 and opuesto != 0: opciones.append(0)
    if dr > 0 and opuesto != 1: opciones.append(1)
    if dc < 0 and opuesto != 2: opciones.append(2)
    if dc > 0 and opuesto != 3: opciones.append(3)

    if opciones and random.random() < 0.70:
        return random.choice(opciones)

    candidatos = [g for g in range(5) if g != opuesto]
    return random.choice(candidatos)


def simular_individuo_rapido(cromosoma, mapa, pos_inicio):
    """
    Simula la ejecución de un cromosoma sobre el mapa.
    """
    salida = mapa.salida
    pos_actual = pos_inicio
    camino = [pos_actual]
    costo_acumulado = 0
    filas = mapa.filas
    cols = mapa.columnas
    ultimo_gen = None

    for gen in cromosoma:
        if pos_actual == salida:
            break

        if ultimo_gen is not None and OPUESTOS.get(ultimo_gen) == gen:
            costo_acumulado += 4
            continue

        dr, dc = DIRECCIONES[gen]
        nr, nc = pos_actual[0] + dr, pos_actual[1] + dc

        if 0 <= nr < filas and 0 <= nc < cols:
            celda = mapa.matriz[nr][nc]
            estado = celda.obtener_estado()
            if estado not in [EstadoCelda.MURO, EstadoCelda.FUEGO, EstadoCelda.OCUPADO]:
                pos_actual = (nr, nc)
                costo_acumulado += celda.obtener_costo()
                camino.append(pos_actual)
                if gen != 4:
                    ultimo_gen = gen
            else:
                costo_acumulado += 3
        else:
            costo_acumulado += 3

    llegó = (pos_actual == salida)
    dist_final = heuristica_manhattan(pos_actual, salida)

    if llegó:
        fitness = 10000 - costo_acumulado - (len(camino) * 2)
    else:
        fitness = 2000 / (1.0 + dist_final) - (costo_acumulado * 0.1)

    return llegó, camino, costo_acumulado, dist_final, max(0.1, fitness)


def busqueda_genetica(mapa, inicio=None, tamano_poblacion=30, generaciones=40, prob_cruce=0.8, prob_mutacion=0.15, longitud_cromosoma=100, usar_modelo=True):
    """
    Ejecuta el Algoritmo Genético. Si existe un modelo guardado en models/ga_model.json,
    intenta utilizar el mejor cromosoma entrenado como semilla élite o respuesta inmediata.
    """
    pos_inicio = inicio if inicio else mapa.inicio
    salida = mapa.salida

    if not pos_inicio or not salida:
        return {"exito": False, "camino": [], "costo_total": float('inf'), "nodos_visitados": 0}

    # 1. Intentar cargar versión entrenada guardada
    cromosoma_semilla = None
    if usar_modelo:
        modelos = cargar_modelo_entrenado()
        if modelos:
            # Buscar el modelo que coincida con las dimensiones o clave
            for clave, mdata in modelos.items():
                c_guardado = mdata.get("cromosoma")
                if c_guardado:
                    llegó, camino_m, costo_m, _, _ = simular_individuo_rapido(c_guardado, mapa, pos_inicio)
                    # Si el camino guardado es válido y no está bloqueado por fuego
                    if llegó:
                        return {
                            "exito": True,
                            "camino": camino_m,
                            "costo_total": costo_m,
                            "nodos_visitados": len(camino_m)
                        }
                    elif len(camino_m) > 1 and pos_inicio == mapa.inicio:
                        cromosoma_semilla = c_guardado

    # 2. Población inicial (usando semilla entrenada si está disponible)
    poblacion = []
    if cromosoma_semilla:
        poblacion.append(cromosoma_semilla[:])

    while len(poblacion) < tamano_poblacion:
        crom = []
        pos_temp = pos_inicio
        ultimo_g = None
        for _ in range(longitud_cromosoma):
            g = gen_guiado(pos_temp, salida, ultimo_g)
            crom.append(g)
            dr, dc = DIRECCIONES[g]
            pos_temp = (pos_temp[0] + dr, pos_temp[1] + dc)
            if g != 4:
                ultimo_g = g
        poblacion.append(crom)

    mejor_solucion = None
    mejor_fitness_global = -1
    visitados = set()

    for gen_idx in range(generaciones):
        evaluaciones = []
        for ind in poblacion:
            llegó, camino, costo, dist, fit = simular_individuo_rapido(ind, mapa, pos_inicio)
            
            for p in camino:
                visitados.add(p)

            evaluaciones.append((fit, ind, llegó, camino, costo))

            if fit > mejor_fitness_global:
                mejor_fitness_global = fit
                mejor_solucion = (llegó, camino, costo)

        if mejor_solucion and mejor_solucion[0]:
            break

        def torneo(k=3):
            aspirantes = random.sample(evaluaciones, k)
            aspirantes.sort(key=lambda x: x[0], reverse=True)
            return aspirantes[0][1]

        evaluaciones.sort(key=lambda x: x[0], reverse=True)
        nueva_poblacion = [evaluaciones[0][1][:], evaluaciones[1][1][:]]

        while len(nueva_poblacion) < tamano_poblacion:
            padre1 = torneo()
            padre2 = torneo()

            if random.random() < prob_cruce:
                punto_cruce = random.randint(1, longitud_cromosoma - 1)
                hijo1 = padre1[:punto_cruce] + padre2[punto_cruce:]
                hijo2 = padre2[:punto_cruce] + padre1[punto_cruce:]
            else:
                hijo1, hijo2 = padre1[:], padre2[:]

            for hijo in [hijo1, hijo2]:
                for i in range(longitud_cromosoma):
                    if random.random() < prob_mutacion:
                        ultimo_g = hijo[i - 1] if i > 0 else None
                        opuesto_g = OPUESTOS.get(ultimo_g, None)
                        candidatos = [g for g in range(5) if g != opuesto_g]
                        hijo[i] = random.choice(candidatos)

            nueva_poblacion.extend([hijo1, hijo2])

        poblacion = nueva_poblacion[:tamano_poblacion]

    if mejor_solucion:
        llegó, camino, costo = mejor_solucion
        return {
            "exito": llegó or (len(camino) > 1),
            "camino": camino,
            "costo_total": costo,
            "nodos_visitados": len(visitados)
        }
    else:
        return {
            "exito": False,
            "camino": [pos_inicio],
            "costo_total": float('inf'),
            "nodos_visitados": len(visitados)
        }
