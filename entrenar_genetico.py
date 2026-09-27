import json
import os
import random
import time
from src.base_map.mapa import Mapa
from src.algoritmos.genetico import (
    simular_individuo_rapido,
    gen_guiado,
    OPUESTOS,
    DIRECCIONES
)


def entrenar_mapa(ruta_mapa, tamano_poblacion=150, generaciones=300, longitud_cromosoma=120):
    """
    Entrena el Algoritmo Genético sobre un mapa específico buscando el mejor cromosoma de escape.
    """
    if not os.path.exists(ruta_mapa):
        print(f"[-] Mapa no encontrado en: {ruta_mapa}")
        return None

    mapa = Mapa(ruta_mapa)
    pos_inicio = mapa.inicio
    salida = mapa.salida

    print(f"\n[+] Entrenando GA en '{os.path.basename(ruta_mapa)}' (Población: {tamano_poblacion}, Gen: {generaciones})...")
    t0 = time.time()

    # 1. Población inicial
    poblacion = []
    for _ in range(tamano_poblacion):
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

    mejor_cromosoma = None
    mejor_fitness_global = -1.0
    mejor_camino = []
    mejor_costo = float('inf')
    llegó_meta = False

    prob_cruce = 0.85
    prob_mutacion = 0.12

    for gen_idx in range(1, generaciones + 1):
        evaluaciones = []
        for ind in poblacion:
            llegó, camino, costo, dist, fit = simular_individuo_rapido(ind, mapa, pos_inicio)
            evaluaciones.append((fit, ind, llegó, camino, costo))

            if fit > mejor_fitness_global:
                mejor_fitness_global = fit
                mejor_cromosoma = ind[:]
                mejor_camino = camino
                mejor_costo = costo
                if llegó:
                    llegó_meta = True

        if gen_idx % 50 == 0 or gen_idx == generaciones:
            print(f"    Gen {gen_idx:>3}/{generaciones} | Mejor Fitness: {mejor_fitness_global:7.1f} | Meta Alcanzada: {llegó_meta}")

        if llegó_meta and gen_idx >= 100:
            print(f"    [!] Solución óptima alcanzada en la generación {gen_idx}.")
            break

        # Selección por Torneo (k=4)
        def torneo():
            aspirantes = random.sample(evaluaciones, 4)
            aspirantes.sort(key=lambda x: x[0], reverse=True)
            return aspirantes[0][1]

        # Elitismo: conservar los 4 mejores
        evaluaciones.sort(key=lambda x: x[0], reverse=True)
        nueva_poblacion = [e[1][:] for e in evaluaciones[:4]]

        while len(nueva_poblacion) < tamano_poblacion:
            p1 = torneo()
            p2 = torneo()

            if random.random() < prob_cruce:
                pt = random.randint(1, longitud_cromosoma - 1)
                h1 = p1[:pt] + p2[pt:]
                h2 = p2[:pt] + p1[pt:]
            else:
                h1, h2 = p1[:], p2[:]

            for hijo in [h1, h2]:
                for i in range(longitud_cromosoma):
                    if random.random() < prob_mutacion:
                        ult = hijo[i - 1] if i > 0 else None
                        op = OPUESTOS.get(ult, None)
                        cands = [g for g in range(5) if g != op]
                        hijo[i] = random.choice(cands)

            nueva_poblacion.extend([h1, h2])

        poblacion = nueva_poblacion[:tamano_poblacion]

    duracion = time.time() - t0
    print(f"[OK] Entrenamiento completado en {duracion:.2f}s.")

    return {
        "cromosoma": mejor_cromosoma,
        "fitness": mejor_fitness_global,
        "camino": mejor_camino,
        "costo_total": mejor_costo,
        "exito": llegó_meta,
        "mapa": os.path.basename(ruta_mapa)
    }


def ejecutar_entrenamiento_completo():
    mapas = {
        "cuello_botella": os.path.join("maps", "mapa_cuello_botella.txt"),
        "corporativo": os.path.join("maps", "mapa_corporativo.txt"),
        "semiabierto": os.path.join("maps", "mapa_semiabierto.txt")
    }

    modelos_guardados = {}
    dir_modelos = "models"
    os.makedirs(dir_modelos, exist_ok=True)
    ruta_archivo_modelo = os.path.join(dir_modelos, "ga_model.json")

    print("=========================================================================")
    print("      ENTRENAMIENTO DEL ALGORITMO GENÉTICO - GUARDADO DE MODELO")
    print("=========================================================================")

    for clave, ruta in mapas.items():
        res = entrenar_mapa(ruta, tamano_poblacion=150, generaciones=300, longitud_cromosoma=120)
        if res:
            modelos_guardados[clave] = res

    # Guardar en JSON
    with open(ruta_archivo_modelo, 'w', encoding='utf-8') as f:
        json.dump(modelos_guardados, f, indent=4, ensure_ascii=False)

    print(f"\n[OK] Modelo guardado exitosamente en: {ruta_archivo_modelo}")
    return modelos_guardados


if __name__ == "__main__":
    ejecutar_entrenamiento_completo()
