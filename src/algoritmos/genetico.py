import random
import math
from src.base_map.celda import EstadoCelda

# Movimientos posibles (genes): 0=Arriba, 1=Abajo, 2=Izquierda, 3=Derecha, 4=Esperar
DIRECCIONES = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]


def heuristica_manhattan(pos, pos_meta):
    return abs(pos[0] - pos_meta[0]) + abs(pos[1] - pos_meta[1])


def simular_individuo_rapido(cromosoma, mapa, pos_inicio):
    """
    Simula la ejecución de un cromosoma sobre el mapa de forma optimizada (1 sola llamada por individuo).
    Retorna: (llegó_a_salida, camino_recorrido, costo_acumulado, distancia_final, fitness)
    """
    salida = mapa.salida
    pos_actual = pos_inicio
    camino = [pos_actual]
    costo_acumulado = 0
    filas = mapa.filas
    cols = mapa.columnas

    for gen in cromosoma:
        if pos_actual == salida:
            break

        dr, dc = DIRECCIONES[gen]
        nr, nc = pos_actual[0] + dr, pos_actual[1] + dc

        if 0 <= nr < filas and 0 <= nc < cols:
            celda = mapa.matriz[nr][nc]
            estado = celda.obtener_estado()
            if estado not in [EstadoCelda.MURO, EstadoCelda.FUEGO, EstadoCelda.OCUPADO]:
                pos_actual = (nr, nc)
                costo_acumulado += celda.obtener_costo()
                camino.append(pos_actual)
            else:
                costo_acumulado += 4
        else:
            costo_acumulado += 4

    llegó = (pos_actual == salida)
    dist_final = heuristica_manhattan(pos_actual, salida)

    if llegó:
        fitness = 10000 - costo_acumulado - (len(camino) * 2)
    else:
        fitness = 1000 / (1.0 + dist_final) - (costo_acumulado * 0.1)

    return llegó, camino, costo_acumulado, dist_final, max(0.1, fitness)


def busqueda_genetica(mapa, inicio=None, tamano_poblacion=25, generaciones=35, prob_cruce=0.8, prob_mutacion=0.15, longitud_cromosoma=50):
    """
    Ejecuta el Algoritmo Genético optimizado para encontrar un camino desde inicio a salida.
    
    Ajustes de rendimiento:
    - Evaluación de individuo en 1 solo paso (eliminadas llamadas duplicadas).
    - Población por defecto = 25, Generaciones = 35.
    - Parada temprana si se encuentra la salida.
    """
    pos_inicio = inicio if inicio else mapa.inicio
    salida = mapa.salida

    if not pos_inicio or not salida:
        return {"exito": False, "camino": [], "costo_total": float('inf'), "nodos_visitados": 0}

    # 1. Población inicial
    poblacion = [
        [random.randint(0, 4) for _ in range(longitud_cromosoma)]
        for _ in range(tamano_poblacion)
    ]

    mejor_solucion = None
    mejor_fitness_global = -1
    visitados = set()

    for gen_idx in range(generaciones):
        # 2. Evaluación de Fitness en 1 solo paso por individuo
        evaluaciones = []
        for ind in poblacion:
            llegó, camino, costo, dist, fit = simular_individuo_rapido(ind, mapa, pos_inicio)
            
            for p in camino:
                visitados.add(p)

            evaluaciones.append((fit, ind, llegó, camino, costo))

            if fit > mejor_fitness_global:
                mejor_fitness_global = fit
                mejor_solucion = (llegó, camino, costo)

        # Si encontramos una solución exitosa a la salida, terminamos temprano
        if mejor_solucion and mejor_solucion[0]:
            break

        # 3. Selección por torneo
        def torneo(k=3):
            aspirantes = random.sample(evaluaciones, k)
            aspirantes.sort(key=lambda x: x[0], reverse=True)
            return aspirantes[0][1]

        # 4. Nueva Generación con Elitismo (conservar los 2 mejores)
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
                        hijo[i] = random.randint(0, 4)

            nueva_poblacion.extend([hijo1, hijo2])

        poblacion = nueva_poblacion[:tamano_poblacion]

    if mejor_solucion and mejor_solucion[0]:
        llegó, camino, costo = mejor_solucion
        return {
            "exito": True,
            "camino": camino,
            "costo_total": costo,
            "nodos_visitados": len(visitados)
        }
    else:
        llegó, camino, costo = mejor_solucion if mejor_solucion else (False, [], float('inf'))
        return {
            "exito": llegó,
            "camino": camino,
            "costo_total": costo,
            "nodos_visitados": len(visitados)
        }
