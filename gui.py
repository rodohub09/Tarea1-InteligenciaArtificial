import os
import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
from src.base_map.mapa import Mapa
from src.agente import Agente
from src.base_map.celda import EstadoCelda


class SimuladorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Escape de Incendios - IA")
        self.root.geometry("1050x720")
        self.root.configure(bg="#2c3e50")

        # Variables de control
        self.mapa_path_var = tk.StringVar(value="maps/mapa_cuello_botella.txt")
        self.algoritmo_var = tk.StringVar(value="BFS")
        self.num_agentes_var = tk.IntVar(value=80)
        self.frecuencia_fuego_var = tk.IntVar(value=3)
        self.factor_propagacion_var = tk.DoubleVar(value=0.5)
        self.velocidad_ms_var = tk.IntVar(value=200)

        # Estado de la simulación
        self.mapa = None
        self.agentes = []
        self.rutas = {}
        self.turno_actual = 0
        self.simulando = False
        self.pausado = False

        self._crear_interfaz()
        self.cargar_mapa_inicial()

    def _crear_interfaz(self):
        # --- Panel Superior / Izquierdo de Controles ---
        panel_controles = tk.Frame(self.root, bg="#34495e", bd=2, relief=tk.RAISED, padx=10, pady=10)
        panel_controles.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        title_label = tk.Label(
            panel_controles, text="CONFIGURACIÓN", font=("Helvetica", 14, "bold"),
            bg="#34495e", fg="#ecf0f1"
        )
        title_label.pack(anchor="w", pady=(0, 15))

        # Selector de Mapa
        tk.Label(panel_controles, text="Seleccionar Mapa:", font=("Helvetica", 10, "bold"), bg="#34495e", fg="#ecf0f1").pack(anchor="w")
        self.cb_mapa = ttk.Combobox(
            panel_controles, textvariable=self.mapa_path_var, state="readonly", width=32,
            values=[
                "maps/mapa_cuello_botella.txt",
                "maps/mapa_corporativo.txt",
                "maps/mapa_semiabierto.txt"
            ]
        )
        self.cb_mapa.pack(anchor="w", pady=(2, 10))
        self.cb_mapa.bind("<<ComboboxSelected>>", lambda e: self.cargar_mapa_inicial())

        # Selector de Algoritmo
        tk.Label(panel_controles, text="Algoritmo de Búsqueda:", font=("Helvetica", 10, "bold"), bg="#34495e", fg="#ecf0f1").pack(anchor="w")
        self.cb_algoritmo = ttk.Combobox(
            panel_controles, textvariable=self.algoritmo_var, state="readonly", width=32,
            values=["BFS", "DFS", "A*", "Greedy", "Genético"]
        )
        self.cb_algoritmo.pack(anchor="w", pady=(2, 10))

        # Número de Agentes
        tk.Label(panel_controles, text="Número de Agentes:", font=("Helvetica", 10, "bold"), bg="#34495e", fg="#ecf0f1").pack(anchor="w")
        sp_agentes = tk.Spinbox(panel_controles, from_=1, to=100, textvariable=self.num_agentes_var, width=10, font=("Helvetica", 10))
        sp_agentes.pack(anchor="w", pady=(2, 10))

        # Factor de Propagación de Fuego (0.1 a 1.0)
        tk.Label(panel_controles, text="Factor Propagación Fuego:", font=("Helvetica", 10, "bold"), bg="#34495e", fg="#ecf0f1").pack(anchor="w")
        slider_factor = tk.Scale(
            panel_controles, from_=0.1, to=1.0, resolution=0.1, orient=tk.HORIZONTAL,
            variable=self.factor_propagacion_var, bg="#34495e", fg="#ecf0f1", highlightthickness=0
        )
        slider_factor.pack(fill=tk.X, pady=(2, 10))

        # Velocidad de Animación (MS)
        tk.Label(panel_controles, text="Velocidad (ms por turno):", font=("Helvetica", 10, "bold"), bg="#34495e", fg="#ecf0f1").pack(anchor="w")
        slider_vel = tk.Scale(
            panel_controles, from_=30, to=800, orient=tk.HORIZONTAL,
            variable=self.velocidad_ms_var, bg="#34495e", fg="#ecf0f1", highlightthickness=0
        )
        slider_vel.pack(fill=tk.X, pady=(2, 15))

        # Botones de Acción
        self.btn_iniciar = tk.Button(
            panel_controles, text="▶ Iniciar Simulación", font=("Helvetica", 11, "bold"),
            bg="#2ecc71", fg="white", activebackground="#27ae60", command=self.iniciar_simulacion, cursor="hand2"
        )
        self.btn_iniciar.pack(fill=tk.X, pady=4)

        self.btn_pausa = tk.Button(
            panel_controles, text="⏸ Pausar", font=("Helvetica", 10, "bold"),
            bg="#f39c12", fg="white", activebackground="#d35400", command=self.toggle_pausa, state=tk.DISABLED, cursor="hand2"
        )
        self.btn_pausa.pack(fill=tk.X, pady=4)

        self.btn_paso = tk.Button(
            panel_controles, text="⏭ Paso a Paso", font=("Helvetica", 10, "bold"),
            bg="#3498db", fg="white", activebackground="#2980b9", command=self.paso_a_paso, state=tk.DISABLED, cursor="hand2"
        )
        self.btn_paso.pack(fill=tk.X, pady=4)

        self.btn_reiniciar = tk.Button(
            panel_controles, text="🔄 Reiniciar", font=("Helvetica", 10, "bold"),
            bg="#e74c3c", fg="white", activebackground="#c0392b", command=self.cargar_mapa_inicial, cursor="hand2"
        )
        self.btn_reiniciar.pack(fill=tk.X, pady=4)

        # Leyenda de Colores
        tk.Label(panel_controles, text="LEYENDA", font=("Helvetica", 11, "bold"), bg="#34495e", fg="#ecf0f1").pack(anchor="w", pady=(20, 5))
        leyenda_items = [
            ("Inicio (I)", "#2ecc71"),
            ("Salida (E)", "#3498db"),
            ("Muro", "#1a252f"),
            ("Pasillo Libre", "#ffffff"),
            ("Fuego", "#e74c3c"),
            ("Ocupado (3 Agentes)", "#9b59b6"),
            ("Agentes Transitando", "#f1c40f")
        ]

        for texto, color in leyenda_items:
            f = tk.Frame(panel_controles, bg="#34495e")
            f.pack(anchor="w", pady=1)
            lbl_box = tk.Label(f, text="  ", bg=color, width=2, relief=tk.SOLID, bd=1)
            lbl_box.pack(side=tk.LEFT, padx=(0, 5))
            lbl_txt = tk.Label(f, text=texto, bg="#34495e", fg="#ecf0f1", font=("Helvetica", 9))
            lbl_txt.pack(side=tk.LEFT)

        # --- Panel Derecho Visual (Canvas y Estadísticas) ---
        panel_derecho = tk.Frame(self.root, bg="#2c3e50")
        panel_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas para la cuadrícula del mapa
        self.canvas = tk.Canvas(panel_derecho, bg="#1a252f", highlightthickness=1, highlightbackground="#7f8c8d")
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Panel de Estadísticas en tiempo real
        panel_stats = tk.Frame(panel_derecho, bg="#34495e", bd=2, relief=tk.GROOVE, padx=10, pady=5)
        panel_stats.pack(fill=tk.X)

        self.lbl_turno = tk.Label(panel_stats, text="Turno: 0", font=("Helvetica", 11, "bold"), bg="#34495e", fg="#ecf0f1")
        self.lbl_turno.pack(side=tk.LEFT, expand=True)

        self.lbl_escapados = tk.Label(panel_stats, text="Escapados: 0", font=("Helvetica", 11, "bold"), bg="#34495e", fg="#2ecc71")
        self.lbl_escapados.pack(side=tk.LEFT, expand=True)

        self.lbl_inhabilitados = tk.Label(panel_stats, text="Inhabilitados: 0", font=("Helvetica", 11, "bold"), bg="#34495e", fg="#e74c3c")
        self.lbl_inhabilitados.pack(side=tk.LEFT, expand=True)

        self.lbl_activos = tk.Label(panel_stats, text="En Camino: 0", font=("Helvetica", 11, "bold"), bg="#34495e", fg="#f1c40f")
        self.lbl_activos.pack(side=tk.LEFT, expand=True)

        self.lbl_inicio = tk.Label(panel_stats, text="En Inicio: 0", font=("Helvetica", 11, "bold"), bg="#34495e", fg="#3498db")
        self.lbl_inicio.pack(side=tk.LEFT, expand=True)

    def cargar_mapa_inicial(self):
        self.simulando = False
        self.pausado = False
        self.turno_actual = 0

        self.btn_iniciar.config(state=tk.NORMAL)
        self.btn_pausa.config(state=tk.DISABLED, text="⏸ Pausar")
        self.btn_paso.config(state=tk.DISABLED)

        ruta = self.mapa_path_var.get()
        if not os.path.exists(ruta):
            messagebox.showerror("Error", f"No se encontró el archivo de mapa: {ruta}")
            return

        self.mapa = Mapa(ruta)
        self.dibujar_mapa()

        self.lbl_turno.config(text="Turno: 0")
        self.lbl_escapados.config(text=f"Escapados: 0 / {self.num_agentes_var.get()}")
        self.lbl_inhabilitados.config(text="Inhabilitados: 0")
        self.lbl_activos.config(text=f"En Camino: {self.num_agentes_var.get()}")

    def dibujar_mapa(self):
        if not self.mapa:
            return

        self.canvas.delete("all")
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()

        if cw <= 1 or ch <= 1:
            cw, ch = 650, 600

        cols = self.mapa.columnas
        rows = self.mapa.filas

        cell_w = cw / cols
        cell_h = ch / rows
        cell_size = min(cell_w, cell_h)

        offset_x = (cw - (cols * cell_size)) / 2
        offset_y = (ch - (rows * cell_size)) / 2

        self.cell_size = cell_size
        self.offset_x = offset_x
        self.offset_y = offset_y

        for r in range(rows):
            for c in range(cols):
                celda = self.mapa.matriz[r][c]
                estado = celda.obtener_estado()

                x1 = offset_x + (c * cell_size)
                y1 = offset_y + (r * cell_size)
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                # Color de fondo según estado
                if estado == EstadoCelda.MURO:
                    color = "#1a252f"
                elif estado == EstadoCelda.FUEGO:
                    color = "#e74c3c"
                elif estado == EstadoCelda.OCUPADO:
                    color = "#8e44ad"
                elif celda.es_inicio:
                    color = "#2ecc71"
                elif celda.es_salida:
                    color = "#3498db"
                else:
                    color = "#ffffff"

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#bdc3c7", width=1)

                # Si es inicio o salida, dibujar letra y conteo de agentes dentro de la propia casilla
                if celda.es_inicio:
                    if celda.agentes > 0:
                        cx = (x1 + x2) / 2
                        cy = (y1 + y2) / 2
                        r_dot = cell_size * 0.42
                        self.canvas.create_oval(cx - r_dot, cy - r_dot, cx + r_dot, cy + r_dot, fill="#27ae60", outline="#ffffff", width=2)
                        self.canvas.create_text(cx, cy, text=f"I\n{celda.agentes}", fill="white", font=("Helvetica", max(7, int(cell_size*0.30)), "bold"))
                    else:
                        self.canvas.create_text((x1 + x2)/2, (y1 + y2)/2, text="I", fill="white", font=("Helvetica", int(cell_size*0.5), "bold"))
                elif celda.es_salida:
                    if celda.agentes > 0:
                        cx = (x1 + x2) / 2
                        cy = (y1 + y2) / 2
                        r_dot = cell_size * 0.42
                        self.canvas.create_oval(cx - r_dot, cy - r_dot, cx + r_dot, cy + r_dot, fill="#2980b9", outline="#ffffff", width=2)
                        self.canvas.create_text(cx, cy, text=f"E\n{celda.agentes}", fill="white", font=("Helvetica", max(7, int(cell_size*0.30)), "bold"))
                    else:
                        self.canvas.create_text((x1 + x2)/2, (y1 + y2)/2, text="E", fill="white", font=("Helvetica", int(cell_size*0.5), "bold"))
                elif celda.agentes > 0:
                    color_agente = "#f1c40f" if celda.agentes < 3 else "#e67e22"
                    cx = (x1 + x2) / 2
                    cy = (y1 + y2) / 2
                    r_dot = cell_size * 0.35
                    self.canvas.create_oval(cx - r_dot, cy - r_dot, cx + r_dot, cy + r_dot, fill=color_agente, outline="#d35400", width=2)
                    self.canvas.create_text(cx, cy, text=str(celda.agentes), fill="#2c3e50", font=("Helvetica", int(cell_size*0.4), "bold"))

    def iniciar_simulacion(self):
        if not self.mapa:
            return

        self.cargar_mapa_inicial()
        num_agentes = self.num_agentes_var.get()
        algoritmo = self.algoritmo_var.get()

        # Crear agentes
        self.agentes = [Agente(i + 1, self.mapa) for i in range(num_agentes)]

        # Precalcular ruta inicial para el algoritmo seleccionado
        self.rutas = {}
        cache_rutas = {}
        for a in self.agentes:
            pos_ini = a.posicion_actual
            if pos_ini not in cache_rutas:
                res = a.buscar_camino(algoritmo)
                cache_rutas[pos_ini] = res
            else:
                res = cache_rutas[pos_ini]

            if res.get("camino") and len(res["camino"]) > 1:
                self.rutas[a.id_agente] = deque(res["camino"][1:])
            else:
                self.rutas[a.id_agente] = deque()

        self.simulando = True
        self.pausado = False

        self.btn_iniciar.config(state=tk.DISABLED)
        self.btn_pausa.config(state=tk.NORMAL, text="⏸ Pausar")
        self.btn_paso.config(state=tk.NORMAL)

        self.bucle_simulacion()

    def toggle_pausa(self):
        self.pausado = not self.pausado
        if self.pausado:
            self.btn_pausa.config(text="▶ Reanudar", bg="#2ecc71")
        else:
            self.btn_pausa.config(text="⏸ Pausar", bg="#f39c12")
            self.bucle_simulacion()

    def paso_a_paso(self):
        if not self.simulando:
            return
        self.pausado = True
        self.btn_pausa.config(text="▶ Reanudar", bg="#2ecc71")
        self.ejecutar_turno()

    def bucle_simulacion(self):
        if not self.simulando or self.pausado:
            return

        continuar = self.ejecutar_turno()
        if continuar:
            delay = self.velocidad_ms_var.get()
            self.root.after(delay, self.bucle_simulacion)
        else:
            self.simulando = False
            self.btn_iniciar.config(state=tk.NORMAL)
            self.btn_pausa.config(state=tk.DISABLED)
            self.btn_paso.config(state=tk.DISABLED)

    def ejecutar_turno(self):
        self.turno_actual += 1

        agentes_activos = [a for a in self.agentes if not a.ha_escapado and not a.inhabilitado]
        if not agentes_activos:
            self.actualizar_estadisticas()
            self.dibujar_mapa()
            messagebox.showinfo("Simulación Finalizada", f"La simulación ha finalizado en el turno {self.turno_actual}.")
            return False

        algoritmo = self.algoritmo_var.get()

        # A. Movimiento de agentes en el turno actual
        for a in agentes_activos:
            if a.verificar_estado():
                continue

            cola_pasos = self.rutas[a.id_agente]

            # Recalcular ruta ÚNICAMENTE si hay fuego en su camino directo
            fuego_en_camino_directo = False
            if cola_pasos:
                for pos in cola_pasos:
                    celda_paso = self.mapa.obtener_celda(*pos)
                    if celda_paso and celda_paso.obtener_estado() == EstadoCelda.FUEGO:
                        fuego_en_camino_directo = True
                        break

            if fuego_en_camino_directo:
                nueva_busqueda = a.buscar_camino(algoritmo)
                if nueva_busqueda["exito"] and len(nueva_busqueda["camino"]) > 1:
                    self.rutas[a.id_agente] = deque(nueva_busqueda["camino"][1:])
                    cola_pasos = self.rutas[a.id_agente]
                else:
                    self.rutas[a.id_agente] = deque()
                    a.esperar()
                    continue

            if cola_pasos:
                siguiente_pos = cola_pasos[0]
                exito_mov = a.mover_a(siguiente_pos)

                if exito_mov and a.posicion_actual == siguiente_pos:
                    cola_pasos.popleft()
            else:
                if not a.ha_escapado:
                    nueva_busqueda = a.buscar_camino(algoritmo)
                    if nueva_busqueda["exito"] and len(nueva_busqueda["camino"]) > 1:
                        self.rutas[a.id_agente] = deque(nueva_busqueda["camino"][1:])
                        siguiente_pos = self.rutas[a.id_agente][0]
                        if a.mover_a(siguiente_pos) and a.posicion_actual == siguiente_pos:
                            self.rutas[a.id_agente].popleft()
                    else:
                        a.esperar()

        # B. Propagación de fuego cada N turnos con factor de propagación
        freq_fuego = self.frecuencia_fuego_var.get()
        if self.turno_actual % freq_fuego == 0:
            self.mapa.propagar_fuego(self.factor_propagacion_var.get())
            
            # Condición de salida temprana: si la salida fue consumida por el fuego
            celda_salida = self.mapa.obtener_celda(*self.mapa.salida)
            if celda_salida and celda_salida.obtener_estado() == EstadoCelda.FUEGO:
                self.actualizar_estadisticas()
                self.dibujar_mapa()
                messagebox.showinfo("Simulación Finalizada", f"La salida ha sido bloqueada por el fuego en el turno {self.turno_actual}.")
                return False

            for a in self.agentes:
                if not a.ha_escapado and not a.inhabilitado:
                    a.verificar_estado()

        self.actualizar_estadisticas()
        self.dibujar_mapa()
        return True

    def actualizar_estadisticas(self):
        escapados = sum(1 for a in self.agentes if a.ha_escapado)
        inhabilitados = sum(1 for a in self.agentes if a.inhabilitado)
        en_camino = len(self.agentes) - escapados - inhabilitados

        celda_ini = self.mapa.obtener_celda(*self.mapa.inicio) if self.mapa else None
        en_inicio = celda_ini.agentes if celda_ini else 0

        self.lbl_turno.config(text=f"Turno: {self.turno_actual}")
        self.lbl_escapados.config(text=f"Escapados: {escapados} / {len(self.agentes)}")
        self.lbl_inhabilitados.config(text=f"Inhabilitados: {inhabilitados}")
        self.lbl_activos.config(text=f"En Camino: {en_camino}")
        self.lbl_inicio.config(text=f"En Inicio: {en_inicio}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorGUI(root)

    # Redimensionamiento dinámico del canvas
    root.bind("<Configure>", lambda e: app.dibujar_mapa() if e.widget == root else None)

    root.mainloop()
