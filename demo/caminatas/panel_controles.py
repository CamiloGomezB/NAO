# -*- coding: utf-8 -*-
"""Ventana "Controles de la carrera" del visor en vivo (demo/caminatas/carrera_vivo.py).

Permite cambiar los datos de la carrera sin volver a ejecutar el comando:
  - version del RL (todas las politicas de carrera de policies/);
  - velocidad pedida al RL (vx_cmd), friccion del piso, semilla de la salida, colocacion a mano (d, psi) y vision;
  - velocidad de reproduccion (se aplica al instante, sin reiniciar).
Flujo (pedido de Camilo, 2026-10-15): el programa abre con los robots QUIETOS en sus marcas.
  1. Aplicar: guarda lo que muestra el panel (todavia no toca a los robots);
  2. Reiniciar (o tecla R): pone a los 3 robots en la salida con lo aplicado, quietos;
  3. Iniciar: arranca la carrera.
El panel dice que esta en pista, que esta aplicado pero falta reiniciar y que hay sin aplicar.

Va en el hilo principal: el bucle del visor llama a actualizar() en cada vuelta (como la ventana de las camaras), asi
que los botones corren en el mismo hilo que la simulacion y no hace falta sincronizar nada.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def versiones_disponibles():
    """[(nombre, ruta del model.zip)] de policies/: primero las rl_vX.Y[.Z] de la mas nueva a la mas vieja, luego carrera_vNN."""
    def clave(nombre):
        return tuple(int(n) for n in re.findall(r"\d+", nombre))
    carpetas = [p for p in (ROOT / "policies").iterdir() if (p / "model.zip").exists()]
    rl = sorted((p for p in carpetas if p.name.startswith("rl_v")), key=lambda p: clave(p.name), reverse=True)
    otras = sorted((p for p in carpetas if p.name.startswith("carrera_v")), key=lambda p: clave(p.name), reverse=True)
    return [(p.name, p / "model.zip") for p in rl + otras]


class PanelControles(object):
    def __init__(self, estado, pedido):
        """estado: dict compartido con el visor (rl, vx, mu, semilla, inicio_d, inicio_psi, vision, velocidad).
        pedido: dict del visor; "reiniciar" = True pide el reinicio en la siguiente vuelta del bucle."""
        import tkinter as tk
        from tkinter import ttk
        self.tk, self.estado, self.pedido, self.cerrado = tk, estado, pedido, False
        self.versiones = versiones_disponibles()
        r = self.root = tk.Tk()
        # TODAS las variables llevan master=r. Sin eso, tkinter las crea en el PRIMER Tk del programa, que es la ventana
        # de las camaras (matplotlib): las barras escribian en este Tk y el codigo leia del otro, asi que "Aplicar"
        # siempre tomaba los valores iniciales (E60).
        r.title("Controles de la carrera")
        # A la derecha de la ventana de camaras (que va arriba a la izquierda, 1350 px), si cabe en la pantalla.
        if r.winfo_screenwidth() >= 1350 + 480:
            r.geometry("+%d+0" % (r.winfo_screenwidth() - 480))
        r.resizable(False, False)
        r.protocol("WM_DELETE_WINDOW", self._cerrar)
        f = ttk.Frame(r, padding=10)
        f.grid(sticky="nsew")
        fila = [0]

        def etiqueta(texto):
            ttk.Label(f, text=texto).grid(row=fila[0], column=0, sticky="w", pady=3, padx=(0, 8))

        def siguiente():
            fila[0] += 1

        # Version del RL
        nombre_actual = next((n for n, z in self.versiones if Path(z) == Path(estado["rl"])), Path(estado["rl"]).parent.name)
        self.v_version = tk.StringVar(master=r, value=nombre_actual)
        etiqueta("Versión del RL")
        ttk.Combobox(f, textvariable=self.v_version, values=[n for n, _ in self.versiones], state="readonly",
                     width=16).grid(row=fila[0], column=1, columnspan=2, sticky="w")
        siguiente()

        self._pasos = {}

        def deslizador(texto, var, desde, hasta, paso, fmt):
            # El valor va a la izquierda, junto al nombre, y se actualiza con CUALQUIER cambio de la barra (trace_add):
            # el `command` de ttk.Scale no siempre se llamaba y el numero quedaba quieto mientras la barra se movia.
            lbl = ttk.Label(f, width=34, anchor="w")
            lbl.grid(row=fila[0], column=0, sticky="w", pady=3, padx=(0, 8))
            self._pasos[str(var)] = paso

            def mostrar(*_):
                valor = self._valor(var)
                if valor is not None:
                    lbl.config(text="%s: %s" % (texto, fmt % valor))
                    self._marcar_pendientes()
            ttk.Scale(f, from_=desde, to=hasta, variable=var, length=210).grid(row=fila[0], column=1, columnspan=2, sticky="w")
            var.trace_add("write", mostrar)
            mostrar()
            siguiente()

        self.v_vx = tk.DoubleVar(master=r, value=estado["vx"])
        deslizador("Velocidad pedida al RL [m/s]", self.v_vx, 0.15, 0.55, 0.01, "%.2f")
        self.v_mu = tk.DoubleVar(master=r, value=estado["mu"])
        deslizador("Fricción del piso (μ)", self.v_mu, 0.4, 1.2, 0.05, "%.2f")

        etiqueta("Semilla (salida)")
        self.v_semilla = tk.IntVar(master=r, value=estado["semilla"])
        ttk.Spinbox(f, from_=1000, to=1999, textvariable=self.v_semilla, width=8).grid(row=fila[0], column=1, sticky="w")
        siguiente()

        self.v_mano = tk.BooleanVar(master=r, value=estado["inicio_d"] is not None or estado["inicio_psi"] is not None)
        ttk.Checkbutton(f, text="Colocación a mano (si no, la de la semilla)", variable=self.v_mano).grid(
            row=fila[0], column=0, columnspan=3, sticky="w", pady=(6, 0))
        siguiente()
        self.v_d = tk.DoubleVar(master=r, value=estado["inicio_d"] or 0.0)
        deslizador("   Corrida a la izquierda [cm]", self.v_d, -15, 15, 1, "%+.0f")
        self.v_psi = tk.DoubleVar(master=r, value=estado["inicio_psi"] or 0.0)
        deslizador("   Girada a la izquierda [°]", self.v_psi, -25, 25, 1, "%+.0f")

        etiqueta("Visión")
        self.v_vision = tk.StringVar(master=r, value=estado["vision"])
        cuadro = ttk.Frame(f)
        cuadro.grid(row=fila[0], column=1, columnspan=2, sticky="w")
        for valor, texto in (("camara", "cámara"), ("simulada", "simulada"), ("no", "sin visión")):
            ttk.Radiobutton(cuadro, text=texto, value=valor, variable=self.v_vision).pack(side="left", padx=(0, 6))
        siguiente()

        ttk.Separator(f).grid(row=fila[0], column=0, columnspan=3, sticky="ew", pady=8)
        siguiente()
        self.v_velocidad = tk.DoubleVar(master=r, value=estado["velocidad"])
        lbl_vel = ttk.Label(f, width=34, anchor="w")
        lbl_vel.grid(row=fila[0], column=0, sticky="w", pady=3, padx=(0, 8))

        def cambiar_velocidad(*_):
            # Con trace_add: se aplica con cualquier cambio de la variable, no solo al arrastrar el control.
            try:
                v = round(round(self.v_velocidad.get() / 0.25) * 0.25, 2) or 0.25
            except (ValueError, self.tk.TclError):
                return
            self.estado["velocidad"] = v
            lbl_vel.config(text="Reproducción (al instante): %.2fx" % v)
        ttk.Scale(f, from_=0.25, to=3.0, variable=self.v_velocidad, length=210).grid(row=fila[0], column=1, columnspan=2, sticky="w")
        self.v_velocidad.trace_add("write", cambiar_velocidad)
        cambiar_velocidad()
        siguiente()

        botones = ttk.Frame(f)
        botones.grid(row=fila[0], column=0, columnspan=3, sticky="ew", pady=(10, 0))
        ttk.Button(botones, text="1. Aplicar", command=self.aplicar).pack(side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Button(botones, text="2. Reiniciar (R)", command=self.reiniciar).pack(side="left", expand=True, fill="x", padx=(0, 4))
        self.btn_iniciar = ttk.Button(botones, text="3. Iniciar", command=self.iniciar)
        self.btn_iniciar.pack(side="left", expand=True, fill="x")
        siguiente()
        self.lbl_fase = ttk.Label(f, font=("Segoe UI", 10, "bold"))
        self.lbl_fase.grid(row=fila[0], column=0, columnspan=3, sticky="w", pady=(10, 0))
        siguiente()
        self.lbl_estado = ttk.Label(f, foreground="#52514e", wraplength=430, justify="left")
        self.lbl_estado.grid(row=fila[0], column=0, columnspan=3, sticky="w", pady=(4, 0))
        siguiente()
        self.lbl_aplicado = ttk.Label(f, foreground="#2a78d6", wraplength=430, justify="left")
        self.lbl_aplicado.grid(row=fila[0], column=0, columnspan=3, sticky="w", pady=(4, 0))
        siguiente()
        self.lbl_pendiente = ttk.Label(f, foreground="#a26800", wraplength=430, justify="left")
        self.lbl_pendiente.grid(row=fila[0], column=0, columnspan=3, sticky="w", pady=(4, 0))
        self.en_pista = dict(estado)
        self.fase = "en sus marcas"
        for var in (self.v_version, self.v_semilla, self.v_mano, self.v_vision):
            var.trace_add("write", lambda *_: self._marcar_pendientes())
        self.mostrar_estado()
        self.poner_fase("en sus marcas")

    # ------------------------------------------------------------------ acciones
    def aplicar(self):
        e = self.estado
        e["rl"] = str(dict(self.versiones).get(self.v_version.get(), e["rl"]))
        e["vx"] = self._valor(self.v_vx, e["vx"])
        e["mu"] = self._valor(self.v_mu, e["mu"])
        try:
            e["semilla"] = int(self.v_semilla.get())
        except (ValueError, self.tk.TclError):
            self.v_semilla.set(e["semilla"])
        if self.v_mano.get():
            e["inicio_d"], e["inicio_psi"] = self._valor(self.v_d, 0.0), self._valor(self.v_psi, 0.0)
        else:
            e["inicio_d"] = e["inicio_psi"] = None
        e["vision"] = self.v_vision.get()
        print("Aplicado: %s. Pulsa Reiniciar para ponerlo en pista." % self._describir(e), flush=True)
        self.mostrar_estado()

    def _valor(self, var, defecto=None):
        """Valor de un deslizador redondeado a su paso (o `defecto` si no se puede leer)."""
        try:
            paso = self._pasos.get(str(var))
            v = float(var.get())
            return round(round(v / paso) * paso, 4) if paso else v
        except (ValueError, self.tk.TclError):
            return defecto

    def _marcar_pendientes(self):
        """Avisa si lo que hay en el panel todavia no esta en la pista (falta 'Aplicar y reiniciar')."""
        if not hasattr(self, "lbl_pendiente"):
            return
        e = self.estado
        cambios = []
        if str(dict(self.versiones).get(self.v_version.get(), e["rl"])) != str(e["rl"]):
            cambios.append("versión")
        if self._valor(self.v_vx) != round(e["vx"], 4):
            cambios.append("velocidad")
        if self._valor(self.v_mu) != round(e["mu"], 4):
            cambios.append("fricción")
        try:
            if int(self.v_semilla.get()) != e["semilla"]:
                cambios.append("semilla")
        except (ValueError, self.tk.TclError):
            pass
        mano = self.v_mano.get()
        if mano != (e["inicio_d"] is not None) or (mano and (self._valor(self.v_d) != e["inicio_d"] or
                                                         self._valor(self.v_psi) != e["inicio_psi"])):
            cambios.append("colocación")
        if self.v_vision.get() != e["vision"]:
            cambios.append("visión")
        self.lbl_pendiente.config(text=("Sin aplicar: %s. Pulsa «1. Aplicar»." % ", ".join(cambios)) if cambios else "")
        # Aplicado pero todavia no en pista (falta Reiniciar).
        claves = ("rl", "vx", "mu", "semilla", "inicio_d", "inicio_psi", "vision")
        if hasattr(self, "lbl_aplicado"):
            falta = any(str(e[k]) != str(self.en_pista.get(k)) for k in claves)
            self.lbl_aplicado.config(text=("Aplicado, falta «2. Reiniciar»: %s" % self._describir(e)) if falta else "")

    def reiniciar(self):
        self.pedido["reiniciar"] = True
        self.poner_fase("reiniciando…")

    def iniciar(self):
        self.pedido["iniciar"] = True

    @staticmethod
    def _describir(e):
        colocacion = ("semilla %d" % e["semilla"] if e["inicio_d"] is None else
                      "a mano: %+.0f cm, %+.0f°" % (e["inicio_d"], e["inicio_psi"]))
        return "%s · %.2f m/s · μ %.2f · %s · visión %s" % (Path(e["rl"]).parent.name, e["vx"], e["mu"], colocacion,
                                                         e["vision"])

    def en_pista_nuevo(self, valores):
        """Lo llama el visor al crear los robots: esto es lo que esta en pista ahora."""
        self.en_pista = dict(valores)
        self.mostrar_estado()

    def poner_fase(self, fase):
        """en sus marcas / corriendo / terminada / reiniciando (lo llama el visor)."""
        self.fase = fase
        ayuda = {"en sus marcas": " — pulsa «3. Iniciar»", "terminada": " — «2. Reiniciar» para otra"}.get(fase, "")
        self.lbl_fase.config(text="Carrera: %s%s" % (fase.upper(), ayuda))
        self.btn_iniciar.state(["!disabled"] if fase == "en sus marcas" else ["disabled"])

    def mostrar_estado(self, extra=""):
        self.lbl_estado.config(text="En pista: " + self._describir(self.en_pista) + ("\n" + extra if extra else ""))
        self._marcar_pendientes()

    # ------------------------------------------------------------------ bucle
    def actualizar(self):
        """Procesa los eventos de la ventana sin bloquear. Se llama en cada vuelta del bucle del visor."""
        if self.cerrado:
            return
        try:
            self.root.update()
        except self.tk.TclError:
            self.cerrado = True

    def _cerrar(self):
        self.cerrado = True
        self.root.destroy()
