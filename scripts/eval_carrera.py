"""Evalua una politica de carrera (NaoRace-v0) en el carril de 5 m con la bateria del benchmark de 3 carriles.

Usa lo mismo que demo/caminatas/benchmark.py para que los numeros se puedan comparar con B-Human y NAOqi:
  - colocacion inicial por semilla: benchmark.inicio(semilla) (sigma 2 cm y 2 grados), semillas 1000, 1001, ...;
  - meta = el sitio de un pie (centro de la suela) llega a x = 5 m; se para ahi, como el benchmark;
  - mismas metricas y nombres (resultado, t, avance, vel_media, desvio_max, rumbo_max_deg, ...) y el mismo resumen.
Diferencias, anotadas en la salida:
  - la vision del RL es la camara simulada del entorno (d, psi crudos con ruido, retardo y perdidas), no el control
    de giro de las caminatas clasicas;
  - la salida de carril es la del entorno: una esquina de la suela toca el borde interior de la linea.
Tambien da la prueba de rectitud (paso 58): deriva lateral sin vision y desvio con vision.

Uso:
    uv run python scripts/eval_carrera.py --modelo runs/carrera_v01/checkpoints/model_5000000_steps.zip
    uv run python scripts/eval_carrera.py --modelo policies/carrera_v01/model.zip --mu 0.4 0.6 0.8 1.0 1.2 --semillas 3
    uv run python scripts/eval_carrera.py --modelo ... --perturbaciones      # con asimetrias y empujones (paso 58)
"""

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402
from stable_baselines3 import PPO  # noqa: E402
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize  # noqa: E402

import src.envs  # noqa: E402, F401
from demo.caminatas.benchmark import info_corrida, inicio, resumen  # noqa: E402
from src.envs.nao_race_env import LARGO_CARRERA_M, NaoRaceEnv  # noqa: E402
from src.evaluate import find_config, find_vecnormalize, rel  # noqa: E402

MAX_T = 60.0


def cargar(modelo: Path):
    cfg_path = find_config(modelo)
    env_kwargs = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))["env"] if cfg_path else {}
    vn_path = find_vecnormalize(modelo)
    if vn_path is None:
        raise SystemExit(f"No encuentro la normalizacion de {modelo}")
    vn = VecNormalize.load(str(vn_path), DummyVecEnv([lambda: NaoRaceEnv()]))
    vn.training = False
    return PPO.load(modelo, device="cpu"), vn, env_kwargs, vn_path


def correr(model, vn, env_kwargs, mu, semilla, vision, vx, perturbaciones, grabar=False, rumbo_objetivo=None,
           colocacion=None):
    """rumbo_objetivo: None = el de la config de la politica (o el default del entorno, "carril" desde el paso 58c).
    colocacion: (y0 [m], rumbo0 [rad]) fija; None = la del benchmark para esa semilla."""
    kw = {**env_kwargs, "friction": mu, "vx_cambio_prob": 0.0, "perturbaciones": perturbaciones, "vision": vision}
    if rumbo_objetivo is not None:
        kw["rumbo_objetivo"] = rumbo_objetivo
    env = NaoRaceEnv(**kw)
    d0, psi0 = colocacion if colocacion is not None else inicio(semilla)
    obs, info = env.reset(seed=semilla, options={"y0": d0, "yaw0": psi0, "vx_cmd": vx})
    sitios = env._pie_sitios
    hist, resultado, torque2, t_punta, qs = [], "tiempo agotado", 0.0, None, []
    for _ in range(int(MAX_T / env.dt)):
        a, _ = model.predict(vn.normalize_obs(obs), deterministic=True)
        obs, _, term, _, info = env.step(a)
        d = env.data
        torque2 += float(np.sum(d.actuator_force[env._act] ** 2)) * env.dt
        pl, pr = d.site_xpos[sitios[0]], d.site_xpos[sitios[1]]
        x, y = 0.5 * (pl[0] + pr[0]), 0.5 * (pl[1] + pr[1])
        hist.append((info["t"], x, y, info["psi"], env.inclinacion_grados()))
        if grabar:
            qs.append(d.qpos.copy())
        if t_punta is None and info["meta"]:
            t_punta = info["tiempo_meta"]
        if term:
            resultado = "SALIO DEL CARRIL" if info["falta"] == "salida_carril" else "CAIDA"
            break
        if max(pl[0], pr[0]) >= LARGO_CARRERA_M:
            resultado = "META"
            break
    h = np.array(hist)
    T = h[-1, 0]
    esfuerzo = env.esfuerzo_corrida()          # par RMS / par continuo del motor real (fase M2, limite 80 %)
    extra = {"qpos": np.array(qs), "hist": h} if grabar else {}
    return {**extra, "caminata": "rl_carrera", "mu": mu, "resultado": resultado, "t": float(T), "avance": float(h[-1, 1]),
            "vel_media": float(h[-1, 1] / T), "desvio_max": float(np.max(np.abs(h[:, 2]))),
            "desvio_final": float(h[-1, 2]), "rumbo_max_deg": float(np.degrees(np.max(np.abs(h[:, 3])))),
            "inclinacion_max": float(np.max(h[:, 4])), "torque2_por_m": torque2 / max(0.05, float(h[-1, 1])),
            "t_meta_punta": t_punta, "falta": info["falta"], "semilla": semilla, "vision": int(vision),
            "esfuerzo": {k: round(v, 4) for k, v in esfuerzo.items()}, "esfuerzo_max": max(esfuerzo.values()),
            "esfuerzo_max_articulacion": max(esfuerzo, key=esfuerzo.get),
            "traza": h[::20, :3].round(4).tolist()}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--modelo", type=Path, required=True)
    ap.add_argument("--vx", type=float, default=0.5, help="vx_cmd fijo [m/s] (default 0.5, el maximo entrenado)")
    ap.add_argument("--mu", type=float, nargs="+", default=[0.4, 0.6, 0.8, 1.0, 1.2])
    ap.add_argument("--semillas", type=int, default=2)
    ap.add_argument("--perturbaciones", action="store_true")
    ap.add_argument("--solo-vision", action="store_true")
    ap.add_argument("--salida", type=Path, default=None, help="carpeta de resultados (default results/carrera/<run>)")
    ap.add_argument("--rumbo-objetivo", choices=("carril", "arranque"), default=None,
                    help="rumbo objetivo de la IMU (paso 58c); por defecto el de la config de la politica o 'carril'")
    args = ap.parse_args()

    model, vn, env_kwargs, vn_path = cargar(args.modelo)
    filas = []
    t0 = time.time()
    for vision in ((True,) if args.solo_vision else (False, True)):
        for mu in args.mu:
            for s in range(1000, 1000 + args.semillas):
                f = correr(model, vn, env_kwargs, mu, s, vision, args.vx, args.perturbaciones,
                           rumbo_objetivo=args.rumbo_objetivo)
                filas.append(f)
                print(f"   vision={'si' if vision else 'no'} mu={mu:.1f} semilla={s}: {f['resultado']:16s} "
                      f"t={f['t']:5.1f} s  v={f['vel_media']:.3f} m/s  desvio max {100 * f['desvio_max']:4.1f} cm  "
                      f"rumbo max {f['rumbo_max_deg']:4.1f} grados  esfuerzo max {100 * f['esfuerzo_max']:3.0f} % "
                      f"({f['esfuerzo_max_articulacion']})", flush=True)
    res = resumen(filas)
    meta = info_corrida()
    meta.update(modelo=rel(args.modelo), normalizacion=rel(vn_path), vx_cmd=args.vx,
                rumbo_objetivo=args.rumbo_objetivo or env_kwargs.get("rumbo_objetivo", "carril"),
                perturbaciones=args.perturbaciones, seg=round(time.time() - t0, 1),
                vision_rl="camara simulada de NaoRace-v0 (d, psi crudos con ruido, retardo y perdidas)",
                friccion_entrenamiento_rl="aleatoria [0.4, 1.2]", rl_friccion_aleatorizada=True)
    for k in ("control", "vx_clasicas", "vision_simulada"):     # son de las caminatas clasicas del benchmark
        meta.pop(k, None)
    nombre = args.modelo.parent.name if args.modelo.parent.name != "checkpoints" else args.modelo.parent.parent.name
    salida = args.salida or ROOT / "results" / "carrera" / nombre
    salida.mkdir(parents=True, exist_ok=True)
    tag = (f"{args.modelo.stem}_vx{args.vx:.2f}{'_pert' if args.perturbaciones else ''}"
           f"{'_' + args.rumbo_objetivo if args.rumbo_objetivo else ''}")
    (salida / f"eval_{tag}.json").write_text(json.dumps({"meta": meta, "resumen": res, "corridas": filas}, indent=1),
                                             encoding="utf-8")
    L = [f"# Evaluacion de carrera: `{rel(args.modelo)}`", "",
         f"`scripts/eval_carrera.py`, {meta['fecha']}, commit {meta['commit']}. vx_cmd = {args.vx} m/s, "
         f"perturbaciones {'si' if args.perturbaciones else 'no'}, rumbo objetivo de la IMU '{meta['rumbo_objetivo']}'. "
         "Colocacion y meta como `demo/caminatas/benchmark.py`.",
         "", "| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | "
         "Rumbo max [deg] | Esfuerzo |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in res:
        tm = "—" if r["metas"] == 0 else "%.1f ± %.1f" % (r["t_meta_medio"], r["t_meta_std"])
        L.append("| %s | %.1f | %d/%d | %d | %d | %s | %.3f | %.1f | %.1f | %.0f |" % (
            "si" if r["vision"] else "no", r["mu"], r["metas"], r["n"], r["caidas"], r["salidas"], tm,
            r["vel_media"], r["desvio_max_medio_cm"], r["rumbo_max_medio_deg"], r["torque2_por_m"]))
    metas = [f for f in filas if f["resultado"] == "META"]
    L += ["", f"**Total:** {len(metas)}/{len(filas)} metas, {sum(f['resultado'] == 'CAIDA' for f in filas)} caidas, "
          f"{sum(f['resultado'] == 'SALIO DEL CARRIL' for f in filas)} salidas."]
    if metas:
        L.append(f"Tiempo a meta medio {np.mean([f['t'] for f in metas]):.2f} s (mejor {min(f['t'] for f in metas):.2f} s).")
    peor = max(filas, key=lambda f: f["esfuerzo_max"])
    L.append(f"Esfuerzo de los motores (par RMS / par continuo, limite 80 %): maximo {100 * peor['esfuerzo_max']:.0f} % "
             f"({peor['esfuerzo_max_articulacion']}); corridas sobre el 80 %: "
             f"{sum(f['esfuerzo_max'] > 0.80 for f in filas)}/{len(filas)}.")
    (salida / f"eval_{tag}.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[-2:]))
    print(f"Escrito {rel(salida / f'eval_{tag}.md')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
