# -*- coding: utf-8 -*-
"""Carrera EN VIVO en MuJoCo: los 3 NAOs a la vez, cada uno en su carril y con su CAMARA.

    uv run python demo/run_demo.py --live                              # lo mismo (entrada principal)
    uv run python -m demo.caminatas.carrera_vivo                       # con la camara de cada robot
    uv run python -m demo.caminatas.carrera_vivo --vision no           # sin vision (se ve como se desvian)
    uv run python -m demo.caminatas.carrera_vivo --inicio-d 12 --inicio-psi -8   # los 3 colocados chuecos
    uv run python -m demo.caminatas.carrera_vivo --mu 0.6              # piso mas resbaloso

Carriles (vistos desde la salida, mirando hacia la meta):
    izquierdo = baseline 2: tipo B-Human (VERDE) · centro = RL del equipo (AZUL) · derecho = baseline 1: tipo NAOqi (NARANJA)

Ventanas:
    - visor 3D de MuJoCo con la pista de 3 carriles (salida y meta en los tres) y los 3 robots;
    - "Lo que ve cada NAO": la camara inferior de cada robot, con las lineas detectadas en celeste y la
      posicion estimada por la vision (d, psi) frente a la real.

Como funciona: cada robot se simula en su propia fisica (no se tocan, igual que en la carrera real, donde
corren por separado) y en el visor se dibujan los tres juntos. Con --vision camara (por defecto) cada robot
corrige su rumbo con SU camara renderizada y la vision de carril/; con --vision simulada se usa el modelo de
error medido (sigma 1.6 cm y 1.2 deg), como en el benchmark.

En el visor: ESPACIO pausa. Para reiniciar, cierra y vuelve a correr. Con el raton se mueve la camara.
macOS: usar `uv run mjpython -m demo.caminatas.carrera_vivo`.
"""
import os

# Laptops con dos GPU (NVIDIA + integrada AMD/Intel): pedir la NVIDIA para OpenGL. Con la integrada AMD de la
# laptop de desarrollo, el visor de MuJoCo dibujaba la escena rota (bitacora 2026-10-10). Sin NVIDIA no tiene efecto.
os.environ.setdefault("SHIM_MCCOMPAT", "0x800000001")

import argparse
import math
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "demo"))

CARRILES = {"bhuman": 0.719, "rl": 0.0, "naoqi": -0.719}     # centro de cada carril [m] (izquierda +)
PREFIJO = {"rl": "", "bhuman": "B_", "naoqi": "N_"}
NOMBRES = {"bhuman": "Baseline 2: tipo B-Human (verde, izq.)", "rl": "RL del equipo (azul, centro)",
           "naoqi": "Baseline 1: tipo NAOqi (naranja, der.)"}
CORTOS = {"bhuman": "B-Human (baseline 2)", "rl": "RL del equipo", "naoqi": "NAOqi (baseline 1)"}
COLORES = {"bhuman": (0.20, 0.72, 0.30), "rl": (0.20, 0.45, 0.95), "naoqi": (0.98, 0.55, 0.10)}
ORDEN_VENTANA = ("bhuman", "rl", "naoqi")                     # de izquierda a derecha, como se ven los carriles


# ---------------------------------------------------------------------------- un robot por fisica
class CorredorClasico(object):
    def __init__(self, nombre, mu, d0, psi0, vision, pista, seed):
        from demo.caminatas.benchmark import VX, VisionSimulada
        from demo.caminatas.simular import Simulacion, cargar_modelo, crear
        from demo.caminatas.vision_camara import VisionCamara
        self.nombre = nombre
        m = cargar_modelo(mu)
        self.cam = crear(nombre, m)
        self.sim = Simulacion(m, self.cam, y0=d0, psi0=psi0)
        self.sim.postura_inicial()
        self.t0 = self.sim.t
        self.vx = VX[nombre]
        rng = np.random.RandomState(seed + 7)
        self.vis = {"camara": lambda: VisionCamara(m, self.sim.d, self.sim.torso, pista, rng),
                    "simulada": lambda: VisionSimulada(rng), "no": lambda: None}[vision]()
        self.resultado, self.t_fin = None, None

    @property
    def t(self):
        return self.sim.t - self.t0

    @property
    def qpos(self):
        return self.sim.d.qpos

    def paso(self):
        x, y, yaw = self.sim.pose()
        wz = self.vis.giro(self.sim.t, y, yaw) if self.vis is not None else 0.0
        ang = self.cam.paso(self.vx, 0.0, wz, self.sim.sensores())
        self.sim.aplicar(ang)
        self.sim.avanzar()
        if self.sim.cayo():
            self.resultado = "CAIDA"
        elif self.sim.fuera():
            self.resultado = "SALIO DEL CARRIL"
        elif self.sim.meta():
            self.resultado = "META"
        if self.resultado:
            self.t_fin = self.t

    def pose(self):
        return self.sim.pose()


class CorredorRL(object):
    def __init__(self, mu, d0, psi0, vision, pista, seed):
        import pickle

        import mujoco
        import yaml
        from stable_baselines3 import PPO
        import src.envs.nao_walk_env as E
        from demo.caminatas.benchmark import VisionSimulada
        from demo.caminatas.vision_camara import VisionCamara
        E.SCENE_PATH = ROOT / "assets" / "nao" / "scene_carril.xml"
        cfg = yaml.safe_load(open(ROOT / "checkpoints/best_model_config.yaml"))
        self.model = PPO.load(ROOT / "checkpoints/best_model.zip", device="cpu")
        self.vn = pickle.load(open(ROOT / "checkpoints/best_model_vecnormalize.pkl", "rb"))
        self.env = E.NaoWalkEnv(**cfg["env"])
        self.obs, _ = self.env.reset(seed=seed)
        m, d = self.env.model, self.env.data
        self.env.set_friction(mu)
        d.qpos[1] = d0
        d.qpos[3:7] = [math.cos(psi0 / 2), 0, 0, math.sin(psi0 / 2)]
        mujoco.mj_forward(m, d)
        for _ in range(int(1.0 / self.env.dt)):
            d.ctrl[:] = self.env._home_ctrl
            mujoco.mj_step(m, d, nstep=self.env.frame_skip)
        self.env._step_count = 0
        self.env._prev_action[:] = 0.0
        self.obs = self.env._get_obs()
        rng = np.random.RandomState(seed + 7)
        self.vis = {"camara": lambda: VisionCamara(m, d, self.env._torso_id, pista, rng),
                    "simulada": lambda: VisionSimulada(rng), "no": lambda: None}[vision]()
        self.k = 0
        self.nombre = "rl"
        self.resultado, self.t_fin = None, None

    @property
    def t(self):
        return self.k * self.env.dt

    @property
    def qpos(self):
        return self.env.data.qpos

    def pose(self):
        d = self.env.data
        pl, pr = d.site("left_foot").xpos, d.site("right_foot").xpos
        R = d.xmat[self.env._torso_id].reshape(3, 3)
        return 0.5 * (pl[0] + pr[0]), 0.5 * (pl[1] + pr[1]), math.atan2(R[1, 0], R[0, 0])

    def paso(self):
        from demo.caminatas.benchmark import GYRO_OBS, MAX_BIAS, TURN_GAIN
        from demo.caminatas.simular import FOOT_HALF_WIDTH, LANE_HALF, LENGTH
        x, y, yaw = self.pose()
        o = self.obs.copy()
        if self.vis is not None:
            # La politica actual no tiene comando de giro: se le suma un sesgo al giroscopio (ver run_demo.py)
            o[GYRO_OBS] += float(np.clip(-self.vis.giro(self.t, y, yaw) / TURN_GAIN, -MAX_BIAS, MAX_BIAS))
        action, _ = self.model.predict(self.vn.normalize_obs(o), deterministic=True)
        self.obs, _, terminated, _, _ = self.env.step(action)
        self.k += 1
        d = self.env.data
        R = d.xmat[self.env._torso_id].reshape(3, 3)
        if terminated or d.xpos[self.env._torso_id][2] < 0.2 or R[2, 2] < math.cos(math.radians(45)):
            self.resultado = "CAIDA"
        elif any(abs(d.site(f).xpos[1]) + FOOT_HALF_WIDTH > LANE_HALF for f in ("left_foot", "right_foot")):
            self.resultado = "SALIO DEL CARRIL"
        elif max(d.site("left_foot").xpos[0], d.site("right_foot").xpos[0]) >= LENGTH:
            self.resultado = "META"
        if self.resultado:
            self.t_fin = self.t


# ---------------------------------------------------------------------------- escena con los 3 robots
def escena_tres(mujoco):
    """Pista con 3 NAOs solo para DIBUJAR (nunca se simula: se copian las poses de cada fisica).

    Cada robot lleva su color en las piezas blancas de la carcasa, y cada carril una marca del mismo color en
    el piso, antes de la salida y despues de la meta.
    """
    from demo.caminatas.simular import LENGTH
    esc = mujoco.MjSpec.from_file(str(ROOT / "assets" / "nao" / "scene_carril.xml"))
    for nombre in ("bhuman", "naoqi"):
        robot = mujoco.MjSpec.from_file(str(ROOT / "assets" / "nao" / "nao_cam.xml"))
        for k in list(robot.keys):
            robot.delete(k)
        esc.worldbody.add_frame().attach_body(robot.body("torso"), PREFIJO[nombre], "")
    for k in list(esc.keys):
        esc.delete(k)
    for nombre, y in CARRILES.items():
        r, g, b = COLORES[nombre]
        for x in (-0.40, LENGTH + 0.55):        # marca antes de la salida y despues de la meta
            geom = esc.worldbody.add_geom()
            geom.type = mujoco.mjtGeom.mjGEOM_BOX
            geom.pos = [x, y, 0.0008]
            geom.size = [0.12, 0.30, 0.0008]
            geom.rgba = [r, g, b, 1.0]
            geom.contype = geom.conaffinity = 0
    m = esc.compile()
    # Color de cada robot: se reemplaza el material blanco (nao_0) de su carcasa por el color del carril.
    for g in range(m.ngeom):
        mat = m.geom_matid[g]
        if mat < 0 or not m.material(mat).name.endswith("nao_0"):
            continue
        cuerpo = m.body(m.geom_bodyid[g]).name
        nombre = "bhuman" if cuerpo.startswith("B_") else "naoqi" if cuerpo.startswith("N_") else "rl"
        r, gr, b = COLORES[nombre]
        m.geom_matid[g] = -1
        m.geom_rgba[g] = [0.35 + 0.65 * r, 0.35 + 0.65 * gr, 0.35 + 0.65 * b, 1.0]
    return m


def mapa_qpos(mujoco, m_uno, m_tres, prefijo):
    """Indices de qpos de un robot en la escena de 3 (por nombre de articulacion)."""
    origen, destino = [], []
    for j in range(m_uno.njnt):
        nom = m_uno.joint(j).name
        n = {int(mujoco.mjtJoint.mjJNT_FREE): 7, int(mujoco.mjtJoint.mjJNT_BALL): 4}.get(int(m_uno.jnt_type[j]), 1)
        a = m_uno.jnt_qposadr[j]
        b = m_tres.joint(prefijo + nom).qposadr[0]
        origen += range(a, a + n)
        destino += range(b, b + n)
    return np.array(origen), np.array(destino)


# ---------------------------------------------------------------------------- ventana de las camaras
class VentanaCamaras(object):
    """Lo que ve la camara inferior de cada NAO, con las lineas detectadas y d/psi estimados vs reales."""

    def __init__(self, corredores, interactiva=True):
        import matplotlib
        if not interactiva:
            matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        self.plt = plt
        self.corredores = {c.nombre: c for c in corredores}
        if interactiva:
            plt.ion()
        self.fig, axs = plt.subplots(1, 3, figsize=(13.5, 4.3))
        self.fig.canvas.manager.set_window_title("Lo que ve cada NAO") if interactiva else None
        self.fig.suptitle("Camara inferior de cada NAO (QVGA, 10 FPS) - en celeste, las lineas que detecta la vision")
        self.ax, self.im, self.pts, self.txt = {}, {}, {}, {}
        for ax, nombre in zip(axs, ORDEN_VENTANA):
            ax.set_title(CORTOS[nombre], color=COLORES[nombre], fontweight="bold")
            ax.axis("off")
            self.ax[nombre] = ax
            self.im[nombre] = ax.imshow(np.zeros((240, 320, 3), dtype=np.uint8))
            self.pts[nombre], = ax.plot([], [], ".", color="#00e5ff", markersize=3)
            self.txt[nombre] = ax.text(4, 236, "", color="white", fontsize=8, va="bottom",
                                       bbox=dict(facecolor="black", alpha=0.55, pad=2, edgecolor="none"))
        self.fig.tight_layout()
        if interactiva:
            plt.show(block=False)

    def actualizar(self):
        for nombre, c in self.corredores.items():
            vis = c.vis
            if vis is None or getattr(vis, "imagen", None) is None:
                self.txt[nombre].set_text("sin camara (vision apagada o simulada)")
                continue
            self.im[nombre].set_data(vis.imagen)
            if vis.puntos is not None:
                self.pts[nombre].set_data(vis.puntos[:, 0], vis.puntos[:, 1])
            else:
                self.pts[nombre].set_data([], [])
            x, y, yaw = c.pose()
            linea = "real:     d = %+5.1f cm  psi = %+5.1f deg" % (100 * y, math.degrees(yaw))
            if vis.d_est is not None:
                linea += "\nestimada: d = %+5.1f cm  psi = %+5.1f deg%s" % (
                    100 * vis.d_est, math.degrees(vis.psi_est), "" if vis.valida else "  (sin lineas)")
            self.txt[nombre].set_text(linea)
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def abierta(self):
        return self.plt.fignum_exists(self.fig.number)

    def guardar(self, ruta):
        self.fig.savefig(ruta, dpi=90)


# ---------------------------------------------------------------------------- programa
def agregar_argumentos(ap):
    ap.add_argument("--vision", choices=("camara", "simulada", "no"), default="camara",
                    help="camara = cada robot usa su camara renderizada (por defecto); simulada = modelo de error")
    ap.add_argument("--sin-vision", action="store_true", help="igual que --vision no")
    ap.add_argument("--mu", type=float, default=1.0, help="friccion piso-pie")
    ap.add_argument("--semilla", type=int, default=1000, help="cambia el error de colocacion en la salida")
    ap.add_argument("--inicio-d", type=float, default=None,
                    help="colocacion de los 3: corridos a la izquierda (+) o derecha (-) [cm]; por defecto, aleatoria")
    ap.add_argument("--inicio-psi", type=float, default=None,
                    help="colocacion de los 3: girados a la izquierda (+) o derecha (-) [grados]")
    ap.add_argument("--velocidad", type=float, default=1.0, help="1 = tiempo real, 2 = el doble de rapido")
    ap.add_argument("--sin-camaras", action="store_true", help="no abrir la ventana 'Lo que ve cada NAO'")
    ap.add_argument("--captura", default=None,
                    help="(pruebas, sin pantalla) guarda <ruta>.png del visor y <ruta>_camaras.png a los 8 s")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    agregar_argumentos(ap)
    import build_scene
    build_scene.add_color_args(ap)
    a = ap.parse_args(argv)
    vision = "no" if a.sin_vision else a.vision

    from demo.caminatas.benchmark import inicio
    d0, psi0 = inicio(a.semilla)
    if a.inicio_d is not None:
        d0 = a.inicio_d / 100.0
    if a.inicio_psi is not None:
        psi0 = math.radians(a.inicio_psi)
    pista = build_scene.build(build_scene.config_from_args(a))     # colores de config/pista.yaml (+ opciones)

    print("Preparando los 3 robots (vision: %s, mu = %.2f, colocacion d = %+.1f cm, psi = %+.1f grados)..."
          % (vision, a.mu, 100 * d0, math.degrees(psi0)))
    corredores = [CorredorRL(a.mu, d0, psi0, vision, pista, a.semilla)]   # primero el RL: importa torch antes que OpenGL
    import mujoco
    corredores += [CorredorClasico(n, a.mu, d0, psi0, vision, pista, a.semilla) for n in ("bhuman", "naoqi")]
    m = escena_tres(mujoco)
    d = mujoco.MjData(m)
    mapas = {c.nombre: mapa_qpos(mujoco, (c.env.model if c.nombre == "rl" else c.sim.m), m, PREFIJO[c.nombre])
             for c in corredores}

    def dibujar():
        for c in corredores:
            o, de = mapas[c.nombre]
            d.qpos[de] = c.qpos[o]
            d.qpos[de[1]] += CARRILES[c.nombre]            # cada uno en su carril
        mujoco.mj_forward(m, d)

    def avanzar_hasta(t):
        for c in corredores:
            while c.resultado is None and c.t < t:
                c.paso()

    def textos(t):
        izq = ["Carrera 5 m", "vision", "friccion", "tiempo", ""]
        der = ["", vision, "%.1f" % a.mu, "%.1f s" % t, ""]
        for c in sorted(corredores, key=lambda c: ORDEN_VENTANA.index(c.nombre)):
            izq.append(NOMBRES[c.nombre])
            der.append("%s %.1f s" % (c.resultado, c.t_fin) if c.resultado else "%.2f m" % c.pose()[0])
        return "\n".join(izq), "\n".join(der)

    dibujar()
    if a.captura:                                              # modo de prueba sin pantalla
        ventana = VentanaCamaras(corredores, interactiva=False) if vision == "camara" else None
        avanzar_hasta(8.0)
        dibujar()
        r = mujoco.Renderer(m, 540, 960)
        cam = mujoco.MjvCamera()
        cam.distance, cam.azimuth, cam.elevation = 4.6, 15, -28
        cam.lookat[:] = [2.0, 0, 0.1]
        r.update_scene(d, camera=cam)
        from PIL import Image
        Image.fromarray(r.render()).save(a.captura + ".png")
        if ventana is not None:
            ventana.actualizar()
            ventana.guardar(a.captura + "_camaras.png")
        print(textos(8.0)[1])
        return 0

    ventana = VentanaCamaras(corredores) if (vision == "camara" and not a.sin_camaras) else None
    from mujoco import viewer as mj_viewer
    with mj_viewer.launch_passive(m, d, show_left_ui=False, show_right_ui=False) as v:
        v.cam.lookat[:] = [1.2, 0.0, 0.15]
        v.cam.distance, v.cam.azimuth, v.cam.elevation = 4.6, 15, -28    # desde atras de la salida, mirando a la meta
        print("Listo: corriendo. Cierra el visor para terminar.")
        t_sim, ultimo, ultimo_cam = 0.0, time.time(), 0.0
        while v.is_running():
            ahora = time.time()
            t_sim += min(0.1, ahora - ultimo) * a.velocidad
            ultimo = ahora
            avanzar_hasta(t_sim)
            dibujar()
            xs = [c.pose()[0] for c in corredores]
            v.cam.lookat[0] += 0.05 * (min(4.2, max(1.2, 0.5 * (min(xs) + max(xs)) + 0.3)) - v.cam.lookat[0])
            try:
                v.set_texts((None, mujoco.mjtGridPos.mjGRID_TOPLEFT) + textos(t_sim))
            except Exception:  # noqa: BLE001  (versiones viejas del visor no tienen textos)
                pass
            v.sync()
            if ventana is not None and ahora - ultimo_cam > 0.1 and ventana.abierta():
                ventana.actualizar()
                ultimo_cam = ahora
            time.sleep(max(0.0, 1.0 / 60 - (time.time() - ahora)))
        for c in corredores:
            print("%-42s %s" % (NOMBRES[c.nombre], ("%s en %.1f s" % (c.resultado, c.t_fin)) if c.resultado else "sin terminar"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
