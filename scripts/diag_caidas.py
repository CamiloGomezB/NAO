"""Diagnostico de caidas al pausar/reanudar y del choque entre piernas en el V6 (paso 45 del PLAN).

(a) Reproduce SIN VISOR la logica de pausa de scripts/demo_interactive.py con pausas al azar y cuenta las caidas.
    Modos de pausa:
      - demo:            igual que la demo (espera 2 s de marcha y doble apoyo, congela la ultima accion). El reloj
                         de marcha del entorno SIGUE corriendo durante la pausa, como en la demo.
      - demo_reloj_fijo: igual, pero el reloj de marcha se detiene durante la pausa (hipotesis: el reloj desfasado
                         al reanudar es lo que tumba al robot).
      - inmediata:       congela la ultima accion en cuanto se pide, sin esperar doble apoyo.
      - pose_home:       la pausa manda la accion 0 (pose de pie), como la primera version de la demo.
    Por caida se guarda el motivo, si fue durante la pausa o tras reanudar, la articulacion con mayor error de
    seguimiento y si hubo choque entre piernas en el ultimo segundo.
(b) Distancia minima entre las piernas y pasos con choque (geometrias de muslo, tibia y pie izquierdos contra los
    derechos) con: acciones aleatorias, la politica del sprint caminando de corrido y una politica entrenada desde cero
    en el V6 (--desde-cero).

Uso:
    uv run python scripts/diag_caidas.py
    uv run python scripts/diag_caidas.py --desde-cero runs/diag45_desde_cero_2M/final_model.zip
Escribe results/diagnostico_45.json y results/diagnostico_45.md.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import gymnasium as gym  # noqa: E402
import mujoco  # noqa: E402
import yaml  # noqa: E402
from stable_baselines3 import PPO  # noqa: E402
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize  # noqa: E402

import src.envs  # noqa: E402, F401
from src.evaluate import find_config, find_vecnormalize  # noqa: E402

ENV_ID = "NaoWalk-v0"
MIN_WALK_S = 2.0                      # como la demo
EPISODIO_S = 30.0
CAMINA_S, PAUSA_S = (2.0, 5.0), (0.5, 3.0)   # tramos al azar de marcha y de pausa
VENTANA_REANUDAR_S = 3.0              # una caida hasta 3 s despues de reanudar cuenta como "al reanudar"
PIERNA_L = ("LThigh", "LTibia", "left_foot")
PIERNA_R = ("RThigh", "RTibia", "right_foot")
MODOS = ("demo", "demo_reloj_fijo", "inmediata", "pose_home")


class Politica:
    def __init__(self, ruta: Path):
        cfg = find_config(ruta)
        self.env_kwargs = yaml.safe_load(cfg.read_text(encoding="utf-8"))["env"] if cfg else {}
        self.vecnorm = VecNormalize.load(str(find_vecnormalize(ruta)),
                                         DummyVecEnv([lambda: gym.make(ENV_ID, **self.env_kwargs)]))
        self.vecnorm.training = False
        self.model = PPO.load(ruta, device="cpu")

    def __call__(self, obs):
        return self.model.predict(self.vecnorm.normalize_obs(obs), deterministic=True)[0]


class Piernas:
    """Contactos y distancia minima entre las geometrias de la pierna izquierda y la derecha."""

    def __init__(self, model):
        self.m = model
        self.pares = [(model.geom(a).id, model.geom(b).id) for a in PIERNA_L for b in PIERNA_R]
        self.izq = {model.geom(n).id for n in PIERNA_L}
        self.der = {model.geom(n).id for n in PIERNA_R}
        self.fromto = np.zeros(6)

    def choque(self, data) -> bool:
        for c in data.contact[: data.ncon]:
            if (c.geom1 in self.izq and c.geom2 in self.der) or (c.geom1 in self.der and c.geom2 in self.izq):
                return True
        return False

    def distancia(self, data) -> float:
        return min(mujoco.mj_geomDistance(self.m, data, a, b, 0.2, self.fromto) for a, b in self.pares)


def peor_articulacion(env) -> str:
    """Articulacion controlada con mayor |objetivo - angulo| (servo que no alcanza su objetivo)."""
    err = np.abs(env.data.ctrl[env._act_ids] - env.data.qpos[env._qpos_ids])
    i = int(np.argmax(err))
    return f"{env.controlled_actuators[i]} ({np.degrees(err[i]):.0f} grados)"


def episodio_pausas(pol: Politica, modo: str, semilla: int) -> dict:
    env = gym.make(ENV_ID, **pol.env_kwargs).unwrapped
    piernas = Piernas(env.model)
    rng = np.random.default_rng(semilla)
    obs, _ = env.reset(seed=semilla)
    n = int(EPISODIO_S / env.dt)
    estado, fin_tramo = "camina", rng.uniform(*CAMINA_S)
    pasos_camina, congelada, reloj = 0, None, None
    pausas, t_reanudo, choques_recientes = 0, -1e9, []
    res = {"pausas": 0, "caida": None}
    for k in range(n):
        t = k * env.dt
        if estado in ("camina", "parando"):
            accion = pol(obs)
            pasos_camina += 1
            if estado == "camina" and t >= fin_tramo:
                estado = "parando"
            listo = estado == "parando" and (
                modo in ("inmediata", "pose_home")
                or (pasos_camina * env.dt >= MIN_WALK_S and env.foot_contacts().all()))
            if listo:
                estado, fin_tramo, pausas = "pausa", t + rng.uniform(*PAUSA_S), pausas + 1
                congelada = np.zeros_like(accion) if modo == "pose_home" else accion.copy()
                reloj = env._step_count
        elif estado == "pausa":
            accion = congelada
            if t >= fin_tramo:
                estado, fin_tramo, pasos_camina, t_reanudo = "camina", t + rng.uniform(*CAMINA_S), 0, t
                if modo == "demo_reloj_fijo":
                    env._step_count = reloj
        obs, _, term, _, info = env.step(accion)
        if modo == "demo_reloj_fijo" and estado == "pausa":
            env._step_count = reloj          # el reloj no avanza durante la pausa
        choques_recientes.append(piernas.choque(env.data))
        choques_recientes = choques_recientes[-int(1.0 / env.dt):]
        if term:
            momento = ("en_pausa" if estado == "pausa"
                       else "al_reanudar" if t - t_reanudo <= VENTANA_REANUDAR_S else "caminando")
            res["caida"] = {"t_s": round(t, 2), "motivo": info["fall_reason"], "momento": momento,
                            "articulacion": peor_articulacion(env), "choque_piernas_1s": any(choques_recientes)}
            break
    res["pausas"] = pausas
    env.close()
    return res


def piernas_con(fuente: str, accion_fn, kwargs: dict, semillas, duracion_s: float, env_id: str = ENV_ID) -> dict:
    env = gym.make(env_id, **kwargs).unwrapped
    piernas = Piernas(env.model)
    dmin, pasos, con_choque, caidas = np.inf, 0, 0, 0
    for s in semillas:
        obs, _ = env.reset(seed=s)
        rng = np.random.default_rng(s)
        for _ in range(int(duracion_s / env.dt)):
            obs, _, term, _, _ = env.step(accion_fn(obs, rng, env))
            pasos += 1
            con_choque += piernas.choque(env.data)
            dmin = min(dmin, piernas.distancia(env.data))
            if term:
                caidas += 1
                break
    env.close()
    return {"fuente": fuente, "episodios": len(semillas), "pasos": pasos, "caidas": caidas,
            "pasos_con_choque": con_choque, "pct_pasos_con_choque": round(100 * con_choque / pasos, 3),
            "distancia_min_cm": round(100 * dmin, 2)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--modelo", type=Path, default=ROOT / "checkpoints" / "best_model.zip")
    ap.add_argument("--desde-cero", type=Path, default=None, help="politica entrenada desde cero en el V6")
    ap.add_argument("--episodios", type=int, default=30)
    args = ap.parse_args()
    semillas = list(range(1000, 1000 + args.episodios))

    pol = Politica(args.modelo)
    print(f"(a) Pausas al azar, {args.episodios} episodios de {EPISODIO_S:.0f} s por modo, politica {args.modelo.name}")
    pausas = {}
    for modo in MODOS:
        eps = [episodio_pausas(pol, modo, s) for s in semillas]
        caidas = [e["caida"] for e in eps if e["caida"]]
        n_pausas = sum(e["pausas"] for e in eps)
        pausas[modo] = {
            "episodios": len(eps), "pausas": n_pausas, "caidas": len(caidas),
            "pct_episodios_con_caida": round(100 * len(caidas) / len(eps), 1),
            "caidas_por_momento": dict(Counter(c["momento"] for c in caidas)),
            "caidas_por_motivo": dict(Counter(c["motivo"] for c in caidas)),
            "articulaciones": dict(Counter(c["articulacion"].split(" ")[0] for c in caidas)),
            "con_choque_piernas": sum(c["choque_piernas_1s"] for c in caidas),
            "detalle": caidas,
        }
        p = pausas[modo]
        print(f"   {modo:16s} pausas {n_pausas:4d} | caidas {p['caidas']:3d} ({p['pct_episodios_con_caida']}% de "
              f"episodios) | momento {p['caidas_por_momento']} | motivo {p['caidas_por_motivo']} | "
              f"articulacion {p['articulaciones']} | con choque de piernas {p['con_choque_piernas']}")

    print("(b) Distancia entre piernas y choques")
    act_dim = gym.make(ENV_ID, **pol.env_kwargs).action_space.shape[0]
    piernas = [
        piernas_con("acciones aleatorias uniformes", lambda o, r, e: r.uniform(-1, 1, act_dim),
                    pol.env_kwargs, semillas[:20], 10.0),
        piernas_con("acciones aleatorias uniformes, contrato v1 con presupuesto lateral (NaoRace-v0)",
                    lambda o, r, e: r.uniform(-1, 1, 13), {}, semillas[:20], 10.0, env_id="NaoRace-v0"),
        piernas_con(f"politica del sprint ({args.modelo.name}) de corrido", lambda o, r, e: pol(o),
                    pol.env_kwargs, semillas[:10], 20.0),
    ]
    if args.desde_cero:
        pc = Politica(args.desde_cero)
        piernas.append(piernas_con(f"politica desde cero en el V6 ({args.desde_cero.parent.name})",
                                   lambda o, r, e: pc(o), pc.env_kwargs, semillas[:10], 20.0))
    for p in piernas:
        print(f"   {p['fuente']}: {p['pasos']} pasos, {p['caidas']} caidas, choque en {p['pasos_con_choque']} pasos "
              f"({p['pct_pasos_con_choque']}%), distancia minima {p['distancia_min_cm']} cm")

    salida = {"modelo": str(args.modelo.relative_to(ROOT)), "semillas": [semillas[0], semillas[-1]],
              "pausas": pausas, "piernas": piernas}
    (ROOT / "results" / "diagnostico_45.json").write_text(json.dumps(salida, indent=2, ensure_ascii=False),
                                                          encoding="utf-8")
    lineas = ["# Diagnóstico del paso 45: caídas al pausar/reanudar y choque entre piernas (V6)", "",
              f"Generado por `scripts/diag_caidas.py`. Política: `{salida['modelo']}`. Semillas {semillas[0]}–"
              f"{semillas[-1]}. Datos completos en `diagnostico_45.json`.", "",
              "## (a) Pausas al azar", "",
              "| Modo | Episodios | Pausas | Episodios con caída | Momento | Motivo | Articulación | Con choque de piernas |",
              "|---|---|---|---|---|---|---|---|"]
    for modo, p in pausas.items():
        lineas.append(f"| {modo} | {p['episodios']} | {p['pausas']} | {p['caidas']} ({p['pct_episodios_con_caida']} %) | "
                      f"{p['caidas_por_momento'] or '—'} | {p['caidas_por_motivo'] or '—'} | "
                      f"{p['articulaciones'] or '—'} | {p['con_choque_piernas']} |")
    lineas += ["", "## (b) Piernas", "", "| Fuente | Pasos | Caídas | Pasos con choque | Distancia mínima |",
               "|---|---|---|---|---|"]
    for p in piernas:
        lineas.append(f"| {p['fuente']} | {p['pasos']} | {p['caidas']} | {p['pasos_con_choque']} "
                      f"({p['pct_pasos_con_choque']} %) | {p['distancia_min_cm']} cm |")
    (ROOT / "results" / "diagnostico_45.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print("Escrito results/diagnostico_45.json y results/diagnostico_45.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
