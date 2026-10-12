"""Orden de comportamientos de la recompensa de carrera (criterio del paso 55 del PLAN).

Con la recompensa REAL del entorno (configs/carrera/pesos.yaml) y una politica que camina (--modelo; default la
recomendada, policies/carrera_v03),
en un episodio de 30 s con vx_cmd = 0.5 se comparan:
  A. rapido y limpio: la politica corre a lo que se le pide;
  B. lento y limpio: la politica ve vx_cmd = 0.15 (camina a ~0.15 m/s) pero la recompensa sigue pidiendo 0.5;
  C(t). rapido y se sale en el instante t: lo que acumula A hasta t + el castigo de salida_carril (el episodio
        termina ahi). Se usa la trayectoria de A porque forzar una salida real no es confiable: un empujon de 25 N
        la tumba y una d sesgada 30 cm no la saca (bitacora 2026-10-11).
Criterio del PLAN: C(t) < B para toda salida ANTES de la meta (salirse siempre es peor que ir lento) y A > B.
Informa tambien el retorno DESCONTADO (gamma 0.99) y el peso minimo de salida_carril que haria cumplir el orden.
Termina con RESULTADO: OK o FALLA y escribe results/carrera/orden_recompensa_<politica>.json.

Uso:
    uv run python scripts/check_recompensa_carrera.py
"""

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import eval_carrera  # noqa: E402
from src.envs.nao_race_env import NaoRaceEnv, cargar_pesos  # noqa: E402

GAMMA = 0.99


def episodio(model, vn, kw, semilla, vx_obs=None):
    env = NaoRaceEnv(**{**kw, "friction": 0.8, "perturbaciones": False, "vx_cambio_prob": 0.0})
    obs, _ = env.reset(seed=semilla, options={"y0": 0.0, "yaw0": 0.0, "vx_cmd": 0.5})
    rs, xs, t_meta, term, k = [], [], None, False, 0
    while not term and k < 1250:
        o = obs.copy()
        if vx_obs is not None:
            o[-1] = vx_obs                       # la politica cree que le piden vx_obs
        a, _ = model.predict(vn.normalize_obs(o), deterministic=True)
        obs, r, term, _, info = env.step(a)
        rs.append(r)
        xs.append(info["x"])
        if t_meta is None and info["meta"]:
            t_meta = info["tiempo_meta"]
        k += 1
    rs = np.array(rs)
    return {"rs": rs, "x": np.array(xs), "falta": info["falta"], "t_meta": t_meta, "dt": env.dt,
            "retorno": float(rs.sum()), "retorno_descontado": float(np.sum(GAMMA ** np.arange(len(rs)) * rs))}


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--modelo", type=Path, default=ROOT / "policies" / "carrera_v03" / "model.zip",
                    help="politica que camina (default: la recomendada). El umbral depende de la politica")
    a = ap.parse_args()
    model, vn, kw, _ = eval_carrera.cargar(a.modelo)
    w_salida = cargar_pesos()["salida_carril"]
    A = episodio(model, vn, kw, 1000)
    B = episodio(model, vn, kw, 1000, vx_obs=0.15)
    print(f"A rapido y limpio: retorno {A['retorno']:8.1f} (descontado {A['retorno_descontado']:6.1f}), "
          f"{A['x'][-1]:.1f} m en 30 s, meta a los {A['t_meta']:.1f} s, falta {A['falta']}")
    print(f"B lento y limpio:  retorno {B['retorno']:8.1f} (descontado {B['retorno_descontado']:6.1f}), "
          f"{B['x'][-1]:.1f} m en 30 s, meta {B['t_meta']}, falta {B['falta']}")
    dt = A["dt"]
    k_meta = int(round(A["t_meta"] / dt))
    acum = np.cumsum(A["rs"])
    acum_d = np.cumsum(GAMMA ** np.arange(len(A["rs"])) * A["rs"])
    filas, malas, malas_d = [], [], []
    for ts in np.arange(1.0, A["t_meta"] + 1e-9, 1.0).tolist() + [A["t_meta"] - dt]:
        k = int(round(ts / dt))
        c = float(acum[k - 1] + w_salida)
        cd = float(acum_d[k - 1] + GAMMA ** k * w_salida)
        filas.append({"t_salida": ts, "x": float(A["x"][k - 1]), "retorno": c, "retorno_descontado": cd})
        if c >= B["retorno"]:
            malas.append(round(ts, 2))
        if cd >= B["retorno_descontado"]:
            malas_d.append(round(ts, 2))
        print(f"C sale a los {ts:5.2f} s ({A['x'][k - 1]:.1f} m): retorno {c:8.1f} (descontado {cd:6.1f})  "
              f"{'peor que B: OK' if c < B['retorno'] else 'MEJOR QUE IR LENTO'}")
    w_min = float(acum[k_meta - 1] - B["retorno"])
    ok_ab = A["falta"] is None and B["falta"] is None and A["retorno"] > B["retorno"]
    print(f"   {'OK   ' if ok_ab else 'FALLA'} rapido y limpio ({A['retorno']:.0f}) > lento y limpio ({B['retorno']:.0f})")
    print(f"   {'OK   ' if not malas else 'FALLA'} salirse antes de la meta siempre es peor que ir lento (sin descontar)"
          f"{'' if not malas else f': falla para salidas en {malas} s'}")
    print(f"   (info) peso de salida_carril actual {w_salida:.0f}; para cumplir sin descontar hace falta menos de "
          f"{-w_min:.0f}")
    print(f"   (info) con descuento 0.99, salirse en {malas_d} s vale mas que ir lento: lo cubre el filtro duro de la "
          "seleccion (seccion 11.4)")
    (ROOT / "results" / "carrera" / f"orden_recompensa_{a.modelo.parent.name}.json").write_text(json.dumps({
        "politica": str(a.modelo), "rumbo_objetivo": kw.get("rumbo_objetivo", "carril"), "peso_salida_carril": w_salida, "gamma": GAMMA,
        "A_rapido_limpio": {k: A[k] for k in ("retorno", "retorno_descontado", "t_meta", "falta")},
        "B_lento_limpio": {k: B[k] for k in ("retorno", "retorno_descontado", "t_meta", "falta")},
        "C_salida": filas, "salidas_mejores_que_lento": malas, "salidas_mejores_que_lento_descontado": malas_d,
        "peso_salida_minimo_sin_descuento": -w_min}, indent=1), encoding="utf-8")
    ok = ok_ab and not malas
    print(f"\nRESULTADO: {'OK' if ok else 'FALLA'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
