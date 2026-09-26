import argparse
import os
import time
from src.benchmark import Benchmark, imprimir_reporte


def ejecutar_benchmark_completo(num_iteraciones=200, num_agentes=80, algoritmos=None):
    if algoritmos is None:
        algoritmos = ["bfs", "dfs", "astar", "greedy", "genetico"]

    mapas = {
        "1. Cuello de Botella (Laberinto)": os.path.join("maps", "mapa_cuello_botella.txt"),
        "2. Piso Corporativo": os.path.join("maps", "mapa_corporativo.txt"),
        "3. Espacio Semiabierto": os.path.join("maps", "mapa_semiabierto.txt")
    }

    print("\n" + "=" * 90)
    print("      BENCHMARK DE SIMULACIÓN DE ESCAPE DE INCENDIO (TAREA 1)")
    print(f" Configuración: {num_agentes} agentes simultáneos | {num_iteraciones} iteraciones por algoritmo")
    print(" Propagación de fuego: Cada 3 turnos")
    print(" Mapas a evaluar: 3 (Cuello de botella, Corporativo, Semiabierto)")
    print(" Algoritmos: BFS, DFS, A*, Greedy, Genético")
    print("=" * 90 + "\n")

    tiempo_inicio_global = time.time()
    reporte_global = {}

    for nombre_mapa, ruta_mapa in mapas.items():
        if not os.path.exists(ruta_mapa):
            print(f"[!] ADVERTENCIA: El archivo de mapa no existe en: {ruta_mapa}")
            continue

        print(f"\n>>> INICIANDO EVALUACIÓN DE MAPA: {nombre_mapa} ({ruta_mapa}) <<<")
        bench = Benchmark(ruta_mapa, num_iteraciones=num_iteraciones, num_agentes=num_agentes)
        resultados_mapa = bench.ejecutar_todos(algoritmos)
        
        imprimir_reporte(nombre_mapa, resultados_mapa)
        reporte_global[nombre_mapa] = resultados_mapa

    tiempo_total_global = time.time() - tiempo_inicio_global

    print("=" * 90)
    print(f"   BENCHMARK FINALIZADO CON ÉXITO EN {tiempo_total_global / 60:.2f} MINUTOS ({tiempo_total_global:.1f} SEGUNDOS)")
    print("=" * 90 + "\n")

    return reporte_global


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ejecutar Benchmark del Simulador de Escape de Incendio")
    parser.add_argument(
        "-i", "--iteraciones",
        type=int,
        default=200,
        help="Número de iteraciones por algoritmo por mapa (defecto: 200)"
    )
    parser.add_argument(
        "-a", "--agentes",
        type=int,
        default=80,
        help="Número de agentes simultáneos (defecto: 80)"
    )
    
    args = parser.parse_args()
    ejecutar_benchmark_completo(num_iteraciones=args.iteraciones, num_agentes=args.agentes)
