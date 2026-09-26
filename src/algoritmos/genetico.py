import random
import math
from src.base_map.celda import EstadoCelda


DIRECCIONES = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]


def heuristica_manhattan(pos, pos_meta):
    return abs(pos[0] - pos_meta[0]) + abs(pos[1] - pos_meta[1])


def simular_individuo(cromosoma, mapa, pos_inicio):
    """
    Simula la ejecución de un cromosoma sobre el mapa.
    """
    salida = mapa.salida
    pos_actual = pos_inicio
    camino = [pos_actual]
    costo_acumulado = 0
    pasos_usados = 0

    for gen in cromosoma:
        if pos_actual == salida:
            break

        dr, dc = DIRECCIONES[gen]
        nr, nc = pos_actual[0] + dr, pos_actual[1] + dc
        pasos_usados += 1

        celda = mapa.obtener_celda(nr, nc)
        if celda is None:
            # Movimiento fuera de límites: penaliza y permanece en la posición actual
            costo_acumulado += 5
            continue

        estado = celda.obtener_estado()
        if estado in [EstadoCelda.MURO, EstadoCelda.FUEGO, EstadoCelda.OCUPADO]:
            # Movimiento hacia casilla impasable: no se mueve
            costo_acumulado += 5
        else:
            # Movimiento válido
            pos_actual = (nr, nc)
            costo_acumulado += celda.obtener_costo()
            camino.append(pos_actual)

    llegó_a_salida = (pos_actual == salida)
    distancia_final = heuristica_manhattan(pos_actual, salida)

    return llegó_a_salida, camino, costo_acumulado, distancia_final, pos_actual


def evaluar_fitness(cromosoma, mapa, pos_inicio):
    """
    Calcula el valor de aptitud (fitness) de un individuo.
    Valores más altos indican mejor aptitud.
    """
    llegó, camino, costo, dist_final, _ = simular_individuo(cromosoma, mapa, pos_inicio)
    
    if llegó:
        # Recompensa alta si llega a la salida, menos costo y menos pasos
        fitness = 10000 - costo - (len(camino) * 2)
    else:
        # Si no llega, penaliza según la distancia que le faltó para llegar a la salida
        fitness = 1000 / (1.0 + dist_final) - (costo * 0.1)

    return max(0.1, fitness)


def busqueda_genetica(mapa, inicio=None, tamano_poblacion=60, generaciones=120, prob_cruce=0.8, prob_mutacion=0.15, longitud_cromosoma=60):
    """
    Ejecuta el Algoritmo Genético para encontrar un camino desde inicio a salida.
    """
    pos_inicio = inicio if inicio else mapa.inicio
    salida = mapa.salida

    if not pos_inicio or not salida:
        return {"exito": False, "camino": [], "costo_total": float('inf'), "nodos_visitados": 0}

    poblacion = [
        [random.randint(0, 4) for _ in range(longitud_cromosoma)]
        for _ in range(tamano_poblacion)
    ]

    mejor_solucion = None
    mejor_fitness_global = -1
    visitados = set()

    for gen_idx in range(generaciones):
        # Evalúa fitness
        evaluaciones = []
        for ind in poblacion:
            fit = evaluar_fitness(ind, mapa, pos_inicio)
            llegó, camino, costo, dist, _ = simular_individuo(ind, mapa, pos_inicio)
            
            for p in camino:
                visitados.add(p)

            evaluaciones.append((fit, ind, llegó, camino, costo))

            if fit > mejor_fitness_global:
                mejor_fitness_global = fit
                mejor_solucion = (llegó, camino, costo)

        # Al encontrar una solución de alta calidad termina antes
        if mejor_solucion and mejor_solucion[0]:
            break

        # Selecciona a los mejores para crear la nueva generación
        def torneo(k=3):
            aspirantes = random.sample(evaluaciones, k)
            aspirantes.sort(key=lambda x: x[0], reverse=True)
            return aspirantes[0][1]

        # Nueva Generación con elitismo
        evaluaciones.sort(key=lambda x: x[0], reverse=True)
        nueva_poblacion = [evaluaciones[0][1][:], evaluaciones[1][1][:]]

        while len(nueva_poblacion) < tamano_poblacion:
            padre1 = torneo()
            padre2 = torneo()

            # Cruce en un punto
            if random.random() < prob_cruce:
                punto_cruce = random.randint(1, longitud_cromosoma - 1)
                hijo1 = padre1[:punto_cruce] + padre2[punto_cruce:]
                hijo2 = padre2[:punto_cruce] + padre1[punto_cruce:]
            else:
                hijo1, hijo2 = padre1[:], padre2[:]

            # Mutación
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
        # Retornar la mejor aproximación obtenida
        llegó, camino, costo = mejor_solucion if mejor_solucion else (False, [], float('inf'))
        return {
            "exito": llegó,
            "camino": camino,
            "costo_total": costo,
            "nodos_visitados": len(visitados)
        }
