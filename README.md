# Escape de la Torre - Inteligencia Artificial (Tarea 1)

Este proyecto implementa un simulador dinámico de evacuación de incendios en grillas de 25$\times$25 celdas utilizando agentes inteligentes impulsados por 5 algoritmos de búsqueda: **BFS**, **DFS**, **A\***, **Greedy Best-First Search** y **Algoritmo Genético**.

Incluye una **interfaz gráfica interactiva (GUI)** basada en Tkinter y una **suite de benchmark automatizado** que registra tasas de supervivencia y métricas estadísticas a través de 200 iteraciones por mapa.

---

## Requisitos del Sistema

- **Python 3.10 o superior** (probado en Python 3.12).
- **Librerías estándar de Python** (no requiere instalación de paquetes de terceros):
  - `tkinter` y `ttk` (interfaz gráfica visual)
  - `heapq` (cola de prioridad para A* y Greedy)
  - `collections.deque` (colas FIFO para BFS y rutas de agentes)
  - `random`, `math`, `json`, `os`, `sys`, `time`, `argparse`

---

## Instrucciones de Ejecución

### 1. Interfaz Gráfica de Usuario (GUI)

Para lanzar la simulación interactiva con controles visuales, ejecutor paso a paso, sliders de velocidad y propagación de fuego:

```bash
python gui.py
```

**Controles de la GUI:**
- **Seleccionar Mapa**: Elige entre Cuello de Botella, Piso Corporativo o Espacio Semiabierto.
- **Algoritmo de Búsqueda**: Selecciona BFS, DFS, A*, Greedy o Genético.
- **Número de Agentes**: Configura de 1 a 100 agentes simultáneos (por defecto: 80).
- **Factor Propagación Fuego**: Define la probabilidad de expansión del fuego (0.1 a 1.0, por defecto: 0.5).
- **Velocidad (ms por turno)**: Ajusta la velocidad de la animación.
- **Botones de Control**: ▶ Iniciar, ⏸ Pausar, ⏭ Paso a Paso y 🔄 Reiniciar.

---

### 2. Suite de Benchmark Automatizado

Para ejecutar el experimento masivo (200 iteraciones por algoritmo en los 3 mapas con 80 agentes simultáneos):

```bash
# Ejecución completa por defecto (200 iteraciones, 80 agentes)
python main.py

# Ejecución personalizada rápida (ejemplo: 10 iteraciones y 80 agentes)
python main.py -i 10 -a 80
```

**Parámetros aceptados por `main.py`:**
- `-i`, `--iteraciones`: Número de iteraciones por algoritmo por mapa (defecto: `200`).
- `-a`, `--agentes`: Número de agentes simultáneos (defecto: `80`).

---

### 3. Entrenamiento del Algoritmo Genético

El Algoritmo Genético cuenta con un modelo pre-entrenado guardado en `models/ga_model.json`. Si deseas re-entrenar el modelo en todos los mapas:

```bash
python entrenar_genetico.py
```

Esto evolucionará la población a lo largo de los escenarios y guardará el mejor cromosoma en `models/ga_model.json`.

---
