"""Riesgo fisico de la caminata para los motores del NAO V6 (analisis del 2026-10-13).

Registra en cada paso de fisica (2 ms) par, velocidad y posicion de cada articulacion de las piernas y los hombros, y la
fuerza normal de cada pie, para: rl_v1.0, rl_v1.1, la replica de B-Human y la de NAOqi. Mismo modelo V6 y mismos servos.
Compara con los motores reales del NAO V6 (par continuo, par de parada, velocidad maxima, curva par-velocidad).
Lo usa el dashboard (scripts/dashboard.py, pestana Motores). El informe en PDF esta en results/riesgo_motores/.

Uso (tarda ~10 min):
    uv run python scripts/riesgo_motores.py            # escribe results/riesgo_motores/riesgo.json
"""
import json
import math
import sys
from pathlib import Path

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "demo"))

JUNTAS = ["LHipYawPitch", "LHipRoll", "LHipPitch", "LKneePitch", "LAnklePitch", "LAnkleRoll",
          "RHipRoll", "RHipPitch", "RKneePitch", "RAnklePitch", "RAnkleRoll", "LShoulderPitch", "RShoulderPitch"]
# Motor real del NAO V6 por articulacion (hoja tecnica: tipo 1 con reductora 201.3; tipo 5 con 130.85).
# Valores en la articulacion = motor x reductora, SIN la eficiencia del engranaje (cotas superiores).
TIPO1 = dict(motor="tipo 1, reductora 201.3", parada=11.97, continuo=2.47, w0=math.radians(238.45))
TIPO5 = dict(motor="tipo 5 (22NT Z20), reductora 130.85", parada=0.065 * 130.85, continuo=0.0178 * 130.85,
             w0=8700 * 2 * math.pi / 60 / 130.85)
SPEC = {}
for j in JUNTAS:
    base = j[1:]
    SPEC[j] = TIPO5 if base in ("HipPitch", "KneePitch", "AnklePitch") else TIPO1 if base in (
        "HipYawPitch", "HipRoll", "AnkleRoll") else None
LIMITE_SIM = 5.0
PESO_N = 5.35975 * 9.81


class Registro:
    def __init__(self):
        self.reset()

    def reset(self):
        self.tau, self.w, self.q, self.grf, self.choque = [], [], [], [], []
        self.ids = None

    def preparar(self, m):
        self.m = m
        self.act = [m.actuator(j).id for j in JUNTAS]
        jid = [m.joint(j).id for j in JUNTAS]
        self.dof = [m.jnt_dofadr[i] for i in jid]
        self.qadr = [m.jnt_qposadr[i] for i in jid]
        self.rng = np.array([m.jnt_range[i] for i in jid])
        self.piso = m.geom("floor").id
        self.pies = (m.geom("left_foot").id, m.geom("right_foot").id)
        self.izq = {m.geom(n).id for n in ("LThigh", "LTibia", "left_foot")}
        self.der = {m.geom(n).id for n in ("RThigh", "RTibia", "right_foot")}
        self.f6 = np.zeros(6)
        self.ids = id(m)

    def __call__(self, m, d):
        try:
            if self.ids != id(m):
                self.preparar(m)
            self._registrar(m, d)
        except Exception:      # modelo a medio compilar u otro modelo: no se registra
            pass

    def _registrar(self, m, d):
        self.tau.append(d.actuator_force[self.act].copy())
        self.w.append(d.qvel[self.dof].copy())
        self.q.append(d.qpos[self.qadr].copy())
        g = [0.0, 0.0]
        ch = False
        for i in range(d.ncon):
            c = d.contact[i]
            a, b = c.geom1, c.geom2
            if self.piso in (a, b):
                for k, p in enumerate(self.pies):
                    if p in (a, b):
                        mujoco.mj_contactForce(m, d, i, self.f6)
                        g[k] += self.f6[0]
            elif (a in self.izq and b in self.der) or (a in self.der and b in self.izq):
                ch = True
        self.grf.append(g)
        self.choque.append(ch)


REG = Registro()


def metricas(nombre, tiempo, avance):
    tau, w, q = np.array(REG.tau), np.array(REG.w), np.array(REG.q)
    grf = np.array(REG.grf)
    dt = 0.002
    filas = {}
    for k, j in enumerate(JUNTAS):
        t, v = tau[:, k], w[:, k]
        s = SPEC[j]
        cerca = np.minimum(q[:, k] - REG.rng[k, 0], REG.rng[k, 1] - q[:, k]) < math.radians(3)
        f = {"tau_rms": float(np.sqrt(np.mean(t ** 2))), "tau_p99": float(np.percentile(np.abs(t), 99)),
             "tau_max": float(np.max(np.abs(t))), "pct_en_limite_sim": float(100 * np.mean(np.abs(t) >= LIMITE_SIM - 1e-3)),
             "w_max": float(np.max(np.abs(v))), "w_p99": float(np.percentile(np.abs(v), 99)),
             "pct_cerca_tope": float(100 * np.mean(cerca)),
             "potencia_media": float(np.mean(np.abs(t * v)))}
        if s:
            # Envolvente par-velocidad del motor real (motor de CC: tau_max = parada * (1 - |w|/w0)), solo motorizando.
            motoriza = t * v > 0
            env = s["parada"] * np.clip(1 - np.abs(v) / s["w0"], 0, None)
            f.update(pct_sobre_continuo=float(100 * np.mean(np.abs(t) > s["continuo"])),
                     rms_vs_continuo=float(f["tau_rms"] / s["continuo"]),
                     pct_fuera_envolvente=float(100 * np.mean(motoriza & (np.abs(t) > env))),
                     pct_w_sobre_w0=float(100 * np.mean(np.abs(v) > s["w0"])),
                     w_max_vs_w0=float(f["w_max"] / s["w0"]))
        filas[j] = f
    gt = grf.sum(1)
    res = {"caminata": nombre, "t": tiempo, "avance": avance, "muestras": len(tau),
           "grf_pico_sobre_peso": float(np.max(grf) / PESO_N), "grf_p99_sobre_peso": float(np.percentile(grf.max(1), 99) / PESO_N),
           "pct_choque_piernas": float(100 * np.mean(REG.choque)),
           "energia_mecanica_J": float(np.sum(np.abs(tau * w)) * dt),
           "articulaciones": filas}
    res["energia_por_m"] = res["energia_mecanica_J"] / max(avance, 0.05)
    return res


def correr_rl(modelo, vx, semilla, mu):
    import eval_carrera
    model, vn, kw, _ = eval_carrera.cargar(Path(modelo))
    REG.reset()
    f = eval_carrera.correr(model, vn, kw, mu, semilla, True, vx, False)
    return f


def correr_clasica(nombre, semilla, mu):
    from demo.caminatas.benchmark import correr_clasica as cc
    REG.reset()
    return cc(nombre, mu, semilla, True)


_MJ_STEP = mujoco.mj_step


def _paso_registrado(m, d, nstep=1):
    """Igual que mujoco.mj_step, pero de a un paso de 2 ms, registrando despues de cada uno."""
    for _ in range(nstep):
        _MJ_STEP(m, d)
        REG(m, d)


def main():
    mujoco.mj_step = _paso_registrado
    casos = [("rl_v1.0 (vx 0.40)", lambda s: correr_rl(ROOT / "policies/rl_v1.0/model.zip", 0.40, s, 0.8)),
             ("rl_v1.0 (vx 0.45)", lambda s: correr_rl(ROOT / "policies/rl_v1.0/model.zip", 0.45, s, 0.8)),
             ("rl_v1.1 (vx 0.45)", lambda s: correr_rl(ROOT / "policies/rl_v1.1/model.zip", 0.45, s, 0.8)),
             ("rl_v1.1 (vx 0.50)", lambda s: correr_rl(ROOT / "policies/rl_v1.1/model.zip", 0.50, s, 0.8)),
             ("B-Human (0.30)", lambda s: correr_clasica("bhuman", s, 0.8)),
             ("NAOqi (0.12)", lambda s: correr_clasica("naoqi", s, 0.8))]
    salida = []
    for nombre, fn in casos:
        for s in (1000, 1001, 1002):
            f = fn(s)
            r = metricas(nombre, f["t"], f["avance"])
            r.update(semilla=s, resultado=f["resultado"])
            salida.append(r)
            print(nombre, s, f["resultado"], round(f["t"], 1), "s", flush=True)
    mujoco.mj_step = _MJ_STEP
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "results" / "riesgo_motores" / "riesgo.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"spec": {j: SPEC[j] for j in JUNTAS}, "limite_sim": LIMITE_SIM, "corridas": salida}, indent=1),
                   encoding="utf-8")
    print("ok", out)


if __name__ == "__main__":
    main()
