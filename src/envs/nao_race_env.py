"""Entorno de la Carrera Individual (NaoRace-v0): contrato v1 con camara simulada (pasos 53-58 del PLAN).

- Observacion de 54 valores y accion de 13 angulos cada 24 ms, con las funciones de src/race/contract.py (las mismas
  que usara el NAO real). Solo sensores del NAO: nada de velocidad lineal ni posicion global.
- Pista: carril de 70 cm centrado en y = 0, salida en x = 0, meta en x = 5 m. Las lineas no son geometria: la salida
  de carril se mide con las esquinas de los pies (un pie que toca el borde interior de la linea = falta).
- Camara simulada (seccion 7 del diseno): d y psi reales + ruido gaussiano, retardo, perdidas y mediciones malas, a
  10 Hz y mantenidas entre fotos, con la convencion de la seccion 6.7 (d + = robot a la izquierda; psi + = girado a la
  izquierda).
- Episodio (seccion 6.5): desde quieto con error de colocacion, 0.5 s de pie para que la camara mida, luego la politica
  camina hasta 30 s. Sigue despues de la meta. Friccion sorteada por episodio y por pie.
- Perdida de rectitud (seccion 8): ganancia de servos por pierna, calibracion por articulacion, centro de masa
  corrido, suelo inclinado, empujones, deriva de la IMU y tramos sin vision.
- Recompensa: pesos de configs/carrera/pesos.yaml (seccion 6.4), con la d, psi y velocidad REALES del simulador.
"""

import math
from pathlib import Path

import gymnasium as gym
import mujoco
import numpy as np
import yaml
from gymnasium import spaces

from src.envs.nao_walk_env import FRICTION_MIN, gait_pattern_reward
from src.race import contract as C
from src.race import valores_v6 as V6

ROOT = Path(__file__).resolve().parents[2]
SCENE_PATH = ROOT / "assets" / "nao" / "scene.xml"
PESOS_PATH = ROOT / "configs" / "carrera" / "pesos.yaml"

MEDIO_CARRIL_M = 0.35          # 70 cm interiores: el borde interior de cada linea esta a 35 cm del centro
LARGO_CARRERA_M = 5.0
MARGEN_BARRERA_M = 0.10        # la barrera castiga acercarse a menos de 10 cm de la linea
SIGMA_VX = 0.1
SIGMA_PSI = 0.1
DURACION_S = 30.0
QUIETO_S = 0.5                 # de pie antes de arrancar, para que la camara mida
G = 9.81

PIERNA_L = ("LThigh", "LTibia", "left_foot")
PIERNA_R = ("RThigh", "RTibia", "right_foot")
PIERNAS_ACT = {"L": ("LHipYawPitch", "LHipRoll", "LHipPitch", "LKneePitch", "LAnklePitch", "LAnkleRoll"),
               "R": ("RHipRoll", "RHipPitch", "RKneePitch", "RAnklePitch", "RAnkleRoll")}

# Camara simulada: rango de entrenamiento (seccion 7). Cada episodio sortea sus parametros.
CAMARA_DEFECTO = {
    "sigma_d_m": (0.010, 0.050),       # nominal 1.6 cm; hasta ~3x
    "sigma_psi_grados": (1.0, 4.0),    # nominal 1.2 grados
    "retardo_s": (0.05, 0.25),         # nominal 100-200 ms
    "perdidas": (0.0, 0.30),           # nominal 5-10 %
    "malas": (0.0, 0.08),              # nominal 2-5 %, hasta +-15 cm
    "mala_max_m": 0.15,
    "apagon_prob": 0.3,                # probabilidad de un tramo sin vision por episodio
    "apagon_s": (0.5, 2.0),
}
# Perdida de rectitud (seccion 8). Todo se sortea por episodio.
RECTITUD_DEFECTO = {
    "colocacion_sigma_m": 0.02, "colocacion_max_m": 0.10,
    "colocacion_sigma_grados": 2.0, "colocacion_max_grados": 8.0,
    "ganancia_pierna": 0.15,           # kp de cada pierna x U(1-0.15, 1+0.15)
    "calibracion_grados": 1.5,         # error por articulacion, U(-1.5, 1.5)
    "centro_masa_m": 0.01,             # corrimiento del centro de masa del torso en x e y
    "inclinacion_suelo_grados": 1.0,
    "empujon_cada_s": (2.0, 6.0), "empujon_dur_s": (0.05, 0.15),
    "empujon_fuerza_n": 6.0, "empujon_torque_nm": 0.4,
    "deriva_imu_rad_por_raiz_s": 0.003, "ruido_imu_rad": 0.005,
    "ruido_articular_rad": 0.002, "ruido_giro_rad_s": 0.02,
}


def cargar_pesos(sobrescribir=None):
    pesos = yaml.safe_load(PESOS_PATH.read_text(encoding="utf-8"))["pesos"]
    desconocidos = set(sobrescribir or {}) - set(pesos)
    if desconocidos:
        raise ValueError(f"Terminos de recompensa desconocidos: {sorted(desconocidos)}")
    pesos.update(sobrescribir or {})
    return {k: float(v) for k, v in pesos.items()}


def _u(rng, rango):
    return float(rng.uniform(*rango))


class NaoRaceEnv(gym.Env):
    metadata = {"render_modes": ["rgb_array"], "render_fps": int(round(1 / C.PERIODO_POLITICA_S))}

    def __init__(
        self,
        pesos: dict | None = None,
        vx_rango: tuple[float, float] = (0.15, 0.50),
        vx_cambio_prob: float = 0.3,        # probabilidad de que vx_cmd cambie una vez a mitad del episodio
        friction: float | None = None,
        friction_range: tuple[float, float] = (0.4, 1.2),
        friction_asym: float = 0.1,
        gait_period: float = C.PERIODO_MARCHA_S,
        stance_fraction: float = 0.6,
        camara: dict | None = None,
        rectitud: dict | None = None,
        perturbaciones: bool = True,        # asimetrias, empujones, suelo inclinado, deriva de la IMU
        camara_perfecta: bool = False,      # d y psi reales sin ruido ni retardo (pruebas)
        vision: bool = True,                # False: la camara simulada nunca mide (sin vision, o camara externa)
        sin_vision_prob: float = 0.0,       # probabilidad de un episodio ENTERO sin camara (carrera_v02)
        rumbo_objetivo: str = "carril",     # "carril": rumbo de la IMU - psi medido de pie (paso 58c, E50);
                                            # "arranque": rumbo de la IMU al arrancar (como se entrenaron v01 y v02)
        escena: str | None = None,          # MJCF de la escena (default assets/nao/scene.xml); la demo usa la pista
        render_mode: str | None = None,
        render_size: tuple[int, int] = (640, 480),
    ):
        self.model = mujoco.MjModel.from_xml_path(str(escena or SCENE_PATH))
        self.data = mujoco.MjData(self.model)
        self.frame_skip = V6.FRAME_SKIP
        self.dt = self.model.opt.timestep * self.frame_skip
        assert abs(self.dt - C.PERIODO_POLITICA_S) < 1e-9, self.dt
        self.pesos = cargar_pesos(pesos)
        self.vx_rango = tuple(vx_rango)
        self.vx_cambio_prob = vx_cambio_prob
        self.friction_fixed = friction
        self.friction_range = tuple(friction_range)
        self.friction_asym = friction_asym
        self.gait_period = gait_period
        self.stance_fraction = stance_fraction
        self.cam_cfg = {**CAMARA_DEFECTO, **(camara or {})}
        self.rect_cfg = {**RECTITUD_DEFECTO, **(rectitud or {})}
        self.perturbaciones = perturbaciones
        self.camara_perfecta = camara_perfecta
        self.vision = vision
        self.sin_vision_prob = sin_vision_prob
        self._vision_ep = vision
        if rumbo_objetivo not in ("carril", "arranque"):
            raise ValueError(f"rumbo_objetivo debe ser 'carril' o 'arranque', no {rumbo_objetivo!r}")
        self.rumbo_objetivo = rumbo_objetivo
        self.render_mode = render_mode
        self.render_size = render_size
        self._renderer = None

        m = self.model
        self._torso = m.body("torso").id
        self._floor = m.geom("floor").id
        self._pies = (m.geom("left_foot").id, m.geom("right_foot").id)
        self._pie_sitios = (m.site("left_foot").id, m.site("right_foot").id)
        self._pierna_l = {m.geom(n).id for n in PIERNA_L}
        self._pierna_r = {m.geom(n).id for n in PIERNA_R}
        self._act = np.array([m.actuator(n).id for n in C.ARTICULACIONES_ACCION])
        jid = [m.joint(n).id for n in C.ARTICULACIONES_ACCION]
        self._qadr = m.jnt_qposadr[jid]
        self._vadr = m.jnt_dofadr[jid]
        self._home_acc = np.array([C.POSE_HOME[n] for n in C.ARTICULACIONES_ACCION])
        home = m.key("home").id
        self._key_qpos = m.key_qpos[home].copy()
        self._key_ctrl = m.key_ctrl[home].copy()
        assert np.allclose(self._key_ctrl[self._act], self._home_acc), "la pose home del modelo y del contrato difieren"
        # Valores originales que las asimetrias modifican por episodio.
        self._gain0 = m.actuator_gainprm[:, 0].copy()
        self._bias0 = m.actuator_biasprm[:, :3].copy()
        self._ipos0 = m.body_ipos[self._torso].copy()
        self._grav0 = m.opt.gravity.copy()
        self._act_pierna = {lado: [m.actuator(n).id for n in nombres] for lado, nombres in PIERNAS_ACT.items()}

        self.action_space = spaces.Box(-1.0, 1.0, shape=(C.N_ACCION,), dtype=np.float32)
        self.observation_space = spaces.Box(-np.inf, np.inf, shape=(C.DIM_OBSERVACION,), dtype=np.float32)
        self._fromto = np.zeros(6)
        self._pies_arr = np.array(self._pies)
        self._lado = np.zeros(m.ngeom, dtype=np.int8)
        self._lado[list(self._pierna_l)] = 1
        self._lado[list(self._pierna_r)] = 2
        sx, sy = m.geom_size[self._pies[0]][:2]
        assert np.allclose(m.geom_size[self._pies[1]][:2], (sx, sy))
        self._esq_local = np.array([[sx, sy, 0], [sx, -sy, 0], [-sx, sy, 0], [-sx, -sy, 0]])
        self._fuerza = np.zeros(6)
        self.camara = C.EstadoCamara()

    # ------------------------------------------------------------------ API Gymnasium

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        rng = self.np_random
        m, d, r = self.model, self.data, self.rect_cfg
        mujoco.mj_resetDataKeyframe(m, d, m.key("home").id)

        # Colocacion: +-10 cm y +-8 grados como maximo, normal con sigma 2 cm y 2 grados.
        y0 = float(np.clip(rng.normal(0, r["colocacion_sigma_m"]), -r["colocacion_max_m"], r["colocacion_max_m"]))
        yaw0 = math.radians(float(np.clip(rng.normal(0, r["colocacion_sigma_grados"]),
                                          -r["colocacion_max_grados"], r["colocacion_max_grados"])))
        # options (evaluacion): colocacion y vx_cmd fijos, p. ej. los mismos del benchmark de 3 carriles.
        options = options or {}
        y0, yaw0 = float(options.get("y0", y0)), float(options.get("yaw0", yaw0))
        d.qpos[1] = y0
        d.qpos[3:7] = (math.cos(yaw0 / 2), 0.0, 0.0, math.sin(yaw0 / 2))
        d.qpos[7:] += rng.uniform(-0.01, 0.01, m.nq - 7)

        self._sortear_friccion(rng)
        self._sortear_asimetrias(rng)
        self._sortear_camara(rng)
        # Episodio entero sin camara (solo si se pide: con 0 no se consume el generador y v01 queda igual).
        self._vision_ep = self.vision and not (self.sin_vision_prob > 0 and rng.random() < self.sin_vision_prob)
        self.vx_cmd = _u(rng, self.vx_rango)
        self._t_cambio_vx = _u(rng, (3.0, 20.0)) if rng.random() < self.vx_cambio_prob else None
        if "vx_cmd" in options:
            self.vx_cmd, self._t_cambio_vx = float(options["vx_cmd"]), None
        self._prox_empujon = _u(rng, r["empujon_cada_s"]) if self.perturbaciones else None
        self._fin_empujon = -1.0
        self._sesgo_imu = 0.0
        self.t = -QUIETO_S                     # tiempo desde que arranca la marcha (negativo = de pie)
        self._prev_action = np.zeros(C.N_ACCION)
        self._meta = False
        self.tiempo_meta = None
        self._hist = []                        # (t, d, psi) reales para el retardo de la camara
        self._psi_de_pie = []                  # psi medidos por la camara antes de arrancar (paso 58c)
        self.camara = C.EstadoCamara()
        mujoco.mj_forward(m, d)

        # De pie 0.5 s en la pose home: la camara toma sus primeras fotos.
        d.ctrl[:] = self._key_ctrl
        d.ctrl[self._act] = self._home_acc + self._cal
        self._medir()
        while self.t < -1e-9:
            mujoco.mj_step(m, d, nstep=self.frame_skip)
            self._medir()
            self._avanzar_tiempo()
        # Rumbo objetivo de la IMU. Paso 58c (E50): la direccion del CARRIL medida por la camara de pie; antes era el
        # rumbo con que arranco el robot, y si arrancaba torcido la IMU le pedia mantener el angulo equivocado.
        if self.rumbo_objetivo == "carril":
            self._rumbo_objetivo = C.rumbo_objetivo_inicial(self._rumbo_imu(), self._psi_de_pie)
        else:
            self._rumbo_objetivo = self._rumbo_imu()
        return self._obs(), self._info()

    def step(self, action):
        a = np.clip(np.asarray(action, dtype=np.float64), -1.0, 1.0)
        obj = C.accion_a_objetivos(a)
        self.data.ctrl[self._act] = np.array([obj[n] for n in C.ARTICULACIONES_ACCION]) + self._cal
        self._aplicar_empujon()
        mujoco.mj_step(self.model, self.data, nstep=self.frame_skip)
        self._medir()
        self._avanzar_tiempo()
        if self._t_cambio_vx is not None and self.t >= self._t_cambio_vx:
            self.vx_cmd, self._t_cambio_vx = _u(self.np_random, self.vx_rango), None

        falta = self.falta()
        terminos = self.terminos_recompensa(a, falta)
        self._prev_action[:] = a
        obs = self._obs()
        if falta == "inestabilidad_numerica":
            obs = np.nan_to_num(obs, nan=0.0, posinf=0.0, neginf=0.0)
        info = self._info()
        info.update(falta=falta, terminos=terminos)
        return obs, float(sum(terminos.values())), falta is not None, False, info

    def render(self):
        if self._renderer is None:
            w, h = self.render_size
            self._renderer = mujoco.Renderer(self.model, h, w)
        self._renderer.update_scene(self.data, camera="track")
        return self._renderer.render()

    def close(self):
        if self._renderer is not None:
            self._renderer.close()
            self._renderer = None

    # ------------------------------------------------------------------ Sorteos por episodio

    def _sortear_friccion(self, rng):
        if self.friction_fixed is not None:
            mu_l = mu_r = self.friction_fixed
        else:
            mu = _u(rng, self.friction_range)
            delta = _u(rng, (-self.friction_asym, self.friction_asym))
            mu_l, mu_r = max(FRICTION_MIN, mu + delta / 2), max(FRICTION_MIN, mu - delta / 2)
        # MuJoCo combina con el MAYOR coeficiente: todo en el menor y cada pie en el suyo (como NaoWalkEnv).
        self.model.geom_friction[:, 0] = min(mu_l, mu_r)
        self.model.geom_friction[self._pies[0], 0] = mu_l
        self.model.geom_friction[self._pies[1], 0] = mu_r
        self.friccion = (float(mu_l), float(mu_r))

    def _sortear_asimetrias(self, rng):
        m, r = self.model, self.rect_cfg
        m.actuator_gainprm[:, 0] = self._gain0
        m.actuator_biasprm[:, :3] = self._bias0
        m.body_ipos[self._torso] = self._ipos0
        m.opt.gravity[:] = self._grav0
        self._cal = np.zeros(C.N_ACCION)
        self.data.xfrc_applied[:] = 0.0
        if not self.perturbaciones:
            return
        for ids in self._act_pierna.values():
            f = _u(rng, (1 - r["ganancia_pierna"], 1 + r["ganancia_pierna"]))
            m.actuator_gainprm[ids, 0] = self._gain0[ids] * f
            m.actuator_biasprm[ids, 1] = self._bias0[ids, 1] * f
        cal = math.radians(r["calibracion_grados"])
        self._cal = rng.uniform(-cal, cal, C.N_ACCION)
        m.body_ipos[self._torso, :2] = self._ipos0[:2] + rng.uniform(-r["centro_masa_m"], r["centro_masa_m"], 2)
        inc = math.radians(r["inclinacion_suelo_grados"])
        ax, ay = rng.uniform(-inc, inc, 2)
        m.opt.gravity[:] = (G * math.sin(ay), -G * math.sin(ax), -G * math.cos(ax) * math.cos(ay))

    def _sortear_camara(self, rng):
        c = self.cam_cfg
        self._cam = {
            "sigma_d": _u(rng, c["sigma_d_m"]), "sigma_psi": math.radians(_u(rng, c["sigma_psi_grados"])),
            "retardo": _u(rng, c["retardo_s"]), "perdidas": _u(rng, c["perdidas"]), "malas": _u(rng, c["malas"]),
        }
        self._prox_foto = -QUIETO_S + _u(rng, (0.0, C.PERIODO_CAMARA_S))
        self._apagon = None
        if self.perturbaciones and rng.random() < c["apagon_prob"]:
            ini = _u(rng, c.get("apagon_inicio_s", (0.5, 20.0)))
            self._apagon = (ini, ini + _u(rng, c["apagon_s"]))

    # ------------------------------------------------------------------ Tiempo, camara e IMU

    def _avanzar_tiempo(self):
        self.t += self.dt
        if self.perturbaciones:
            self._sesgo_imu += self.np_random.normal(0, self.rect_cfg["deriva_imu_rad_por_raiz_s"] * math.sqrt(self.dt))
        d_real, psi_real = self.d_psi_reales()
        self._hist.append((self.t, d_real, psi_real))
        if len(self._hist) > 20:
            self._hist.pop(0)
        while self.t >= self._prox_foto - 1e-9:
            self._foto(self._prox_foto)
            self._prox_foto += C.PERIODO_CAMARA_S

    def _foto(self, t_foto):
        """Una foto de la camara simulada: medicion de un instante pasado (retardo) con ruido."""
        if not self._vision_ep:
            return
        rng, c = self.np_random, self._cam
        if self.camara_perfecta:
            _, dv, pv = self._hist[-1]
            self.camara.nueva_medicion(t_foto, dv, pv, True)
            if t_foto < 0:
                self._psi_de_pie.append(pv)
            return
        if self._apagon and self._apagon[0] <= t_foto <= self._apagon[1]:
            return
        if rng.random() < c["perdidas"]:
            return
        t_img = t_foto - c["retardo"]
        _, dv, pv = min(self._hist, key=lambda h: abs(h[0] - t_img))
        dm = dv + rng.normal(0, c["sigma_d"])
        pm = pv + rng.normal(0, c["sigma_psi"])
        if rng.random() < c["malas"]:
            dm += _u(rng, (-self.cam_cfg["mala_max_m"], self.cam_cfg["mala_max_m"]))
        self.camara.nueva_medicion(t_foto, dm, pm, True)
        if t_foto < 0:
            self._psi_de_pie.append(pm)        # de pie: sirve para fijar la direccion del carril (paso 58c)

    def _rumbo_imu(self):
        rumbo = C.rumbo_desde_cuaternion(self.data.sensor("torso_quat").data)
        if self.perturbaciones:
            rumbo += self._sesgo_imu + self.np_random.normal(0, self.rect_cfg["ruido_imu_rad"])
        return rumbo

    def _aplicar_empujon(self):
        if self._prox_empujon is None:
            return
        r, rng = self.rect_cfg, self.np_random
        if self.t >= self._prox_empujon:
            f, tq = r["empujon_fuerza_n"], r["empujon_torque_nm"]
            self.data.xfrc_applied[self._torso] = (_u(rng, (-f, f)), _u(rng, (-f, f)), 0, 0, 0, _u(rng, (-tq, tq)))
            self._fin_empujon = self.t + _u(rng, r["empujon_dur_s"])
            self._prox_empujon = self.t + _u(rng, r["empujon_cada_s"])
        elif self.t >= self._fin_empujon:
            self.data.xfrc_applied[self._torso] = 0.0

    # ------------------------------------------------------------------ Medidas reales (solo recompensa y metricas)

    def d_psi_reales(self):
        """d = y del punto entre los pies (+ = izquierda del centro); psi = rumbo del torso (+ = girado a la izquierda)."""
        pl, pr = self.data.site_xpos[self._pie_sitios[0]], self.data.site_xpos[self._pie_sitios[1]]
        d = 0.5 * (pl[1] + pr[1])
        psi = C.rumbo_desde_cuaternion(self.data.xquat[self._torso])
        return float(d), float(psi)

    def _medir(self):
        """Una sola pasada por los contactos y los pies tras cada paso de fisica; el resto de metodos lee de aqui."""
        m, d = self.model, self.data
        n = d.ncon
        g1, g2 = d.contact.geom1[:n], d.contact.geom2[:n]
        kg = np.zeros(2)
        suelo_otro = None
        en_suelo = np.flatnonzero((g1 == self._floor) | (g2 == self._floor))
        for i in en_suelo:
            otro = int(g2[i] if g1[i] == self._floor else g1[i])
            if otro == self._pies[0] or otro == self._pies[1]:
                mujoco.mj_contactForce(m, d, int(i), self._fuerza)
                kg[0 if otro == self._pies[0] else 1] += self._fuerza[0] / G
            elif suelo_otro is None:
                suelo_otro = otro
        choque = bool(np.any(self._lado[g1] * self._lado[g2] == 2))   # 1 = pierna izquierda, 2 = derecha
        # Esquinas de las dos suelas (cajas): centro + R @ (+-sx, +-sy, 0).
        R = d.geom_xmat[self._pies_arr].reshape(2, 3, 3)
        esq = d.geom_xpos[self._pies_arr][:, None, :] + np.einsum("pij,kj->pki", R, self._esq_local)
        self._med = {
            "kg": kg, "suelo_otro": suelo_otro, "choque_piernas": choque,
            "margenes": tuple(MEDIO_CARRIL_M - np.max(np.abs(esq[:, :, 1]), axis=1)),
            "x_frente": float(np.max(esq[:, :, 0])),
        }

    def margenes(self):
        """Distancia de cada pie (su esquina mas externa) al borde interior de la linea mas cercana [m]."""
        return self._med["margenes"]

    def x_frente(self):
        return self._med["x_frente"]

    def choque_piernas(self):
        return self._med["choque_piernas"]

    def contactos_y_fsr(self):
        """(contacto izq, contacto der) y (kg izq, kg der) de la fuerza normal pie-suelo (lo que mediria el FSR)."""
        kg = self._med["kg"]
        return (kg > 0.05).astype(float), kg

    def inclinacion_grados(self):
        return float(np.degrees(np.arccos(np.clip(self.data.xmat[self._torso][8], -1.0, 1.0))))

    # ------------------------------------------------------------------ Observacion, faltas y recompensa

    def _obs(self):
        d = self.data
        R = d.xmat[self._torso].reshape(3, 3)
        gravedad = R.T @ np.array([0.0, 0.0, -1.0])
        giro = d.sensor("gyro").data.copy()
        qj = d.qpos[self._qadr] - self._cal
        dq = d.qvel[self._vadr].copy()
        if self.perturbaciones:
            rng, r = self.np_random, self.rect_cfg
            giro += rng.normal(0, r["ruido_giro_rad_s"], 3)
            qj = qj + rng.normal(0, r["ruido_articular_rad"], C.N_ACCION)
        error_rumbo = C._recortar(C.envolver_angulo(self._rumbo_objetivo - self._rumbo_imu()),
                                  -C.LIMITE_ERROR_RUMBO, C.LIMITE_ERROR_RUMBO)
        _, kg = self.contactos_y_fsr()
        carga = np.clip(kg / C.MASA_ROBOT_KG, 0.0, 2.0)
        return np.concatenate([
            gravedad, giro * C.ESCALA_GIRO, [error_rumbo], self.camara.observacion(self.t),
            qj - self._home_acc, dq * C.ESCALA_VEL_ARTICULAR, self._prev_action, carga,
            C.reloj_marcha(max(self.t, 0.0), self.gait_period), [self.vx_cmd],
        ]).astype(np.float32)

    def falta(self):
        """'salida_carril', una caida ('altura', 'inclinacion', 'contacto_<geom>', 'inestabilidad_numerica') o None."""
        d = self.data
        if d.warning[mujoco.mjtWarning.mjWARN_BADQACC].number > 0 or not np.all(np.isfinite(d.qpos)):
            return "inestabilidad_numerica"
        if min(self.margenes()) < 0.0:
            return "salida_carril"
        if d.qpos[2] < V6.ALTURA_CAIDA_M:
            return "altura"
        if self.inclinacion_grados() > V6.INCLINACION_CAIDA_GRADOS:
            return "inclinacion"
        if self._med["suelo_otro"] is not None:
            return "contacto_" + self.model.geom(self._med["suelo_otro"]).name
        return None

    def terminos_recompensa(self, a, falta):
        w, d = self.pesos, self.data
        vx, vy = float(d.qvel[0]), float(d.qvel[1])
        R = d.xmat[self._torso].reshape(3, 3)
        wz = float((R @ d.qvel[3:6])[2])
        gravedad = R.T @ np.array([0.0, 0.0, -1.0])
        d_real, psi_real = self.d_psi_reales()
        barrera = sum(((MARGEN_BARRERA_M - mg) / MARGEN_BARRERA_M) ** 2 for mg in self.margenes()
                      if mg < MARGEN_BARRERA_M)
        contactos, _ = self.contactos_y_fsr()
        fase = (max(self.t, 0.0) / self.gait_period) % 1.0
        meta = 0.0
        if not self._meta and self.x_frente() >= LARGO_CARRERA_M:
            self._meta, self.tiempo_meta, meta = True, self.t, 1.0
        torque = d.actuator_force[self._act]
        crudo = {
            "seguimiento_vx": math.exp(-(((vx - self.vx_cmd) / SIGMA_VX) ** 2)),
            "meta": meta,
            "rumbo": math.exp(-((psi_real / SIGMA_PSI) ** 2)),
            "centrado": d_real ** 2,
            "barrera_margen": barrera,
            "vel_lateral": vy ** 2,
            "vel_giro": wz ** 2,
            "salida_carril": float(falta == "salida_carril"),
            "choque_robot": 0.0,           # sin robots vecinos en el entrenamiento (se mide en la seleccion)
            "caida": float(falta is not None and falta != "salida_carril"),
            "patron_marcha": gait_pattern_reward(contactos, fase, self.stance_fraction),
            "vivo": 1.0,
            "inclinacion": float(gravedad[0] ** 2 + gravedad[1] ** 2),
            "altura": (float(d.qpos[2]) - V6.ALTURA_OBJETIVO_M) ** 2,
            "choque_piernas": float(self.choque_piernas()),
            "cambio_accion": float(np.sum((a - self._prev_action) ** 2)),
            "torque": float(np.sum(torque ** 2)),
        }
        return {k: w[k] * v for k, v in crudo.items()}

    def _info(self):
        d_real, psi_real = self.d_psi_reales()
        return {"t": self.t, "x": float(self.data.qpos[0]), "d": d_real, "psi": psi_real, "vx_cmd": self.vx_cmd,
                "friccion": self.friccion, "meta": self._meta, "tiempo_meta": self.tiempo_meta,
                "margen_min": min(self.margenes())}
