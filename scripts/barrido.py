"""Lanzador de barridos de agentes de carrera (paso 60 del PLAN; diseno, seccion 11).

Cada agente sortea, con su propia semilla:
  - los pesos de la recompensa, dentro de los "rangos" de configs/carrera/pesos.yaml (choque_robot = 2 x salida);
  - el rango de friccion de entrenamiento: minimo U(0.3, 0.5), maximo U(1.0, 1.3);
  - la velocidad maxima pedida: vx_max U(0.40, 0.60);
  - el ruido de la camara simulada: sigma_d maximo U(3, 6) cm y sigma_psi maximo U(3, 5) grados;
  - la semilla de PPO.
Luego, en cola y de a uno (este PC entrena uno a la vez con 16 entornos):
  1. escribe results/barridos/<nombre>/agente_NNN/config.yaml (config completa de src.train);
  2. entrena con `src.train --continuar <base>` (por defecto policies/rl_v1.0, antes carrera_v03) en runs/barrido_<nombre>_NNN;
  3. evalua con la bateria de scripts/eval_carrera.py (con vision, perturbaciones, 5 fricciones x --eval-semillas);
  4. guarda resultado.json con la config sorteada, los numeros y el puntaje de seleccion (seccion 11.4).
Es REANUDABLE: un agente con resultado.json se salta; uno entrenado sin evaluar solo se evalua.
Al final (y tras cada agente) escribe results/barridos/<nombre>/tabla.md ordenada por puntaje.

Uso:
    uv run python scripts/barrido.py --nombre ronda1 --agentes 100 --pasos 1000000
    uv run python scripts/barrido.py --nombre prueba --agentes 4 --pasos 20000 --n-envs 4 --eval-semillas 1   # prueba
"""

import argparse
import copy
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

BASE_CONFIG = ROOT / "configs" / "carrera_v03.yaml"     # config de la base (desde la ronda 1: carrera_v03)
PESOS = ROOT / "configs" / "carrera" / "pesos.yaml"
PY = sys.executable


def sortear(i: int, semilla_barrido: int) -> dict:
    rng = np.random.default_rng([semilla_barrido, i])
    tabla = yaml.safe_load(PESOS.read_text(encoding="utf-8"))
    pesos = {}
    for k, r in tabla["rangos"].items():
        if isinstance(r, list):
            pesos[k] = round(float(rng.uniform(*r)), 4)
    pesos["choque_robot"] = 2 * pesos["salida_carril"]
    return {
        "pesos": pesos,
        "friction_range": [round(float(rng.uniform(0.3, 0.5)), 3), round(float(rng.uniform(1.0, 1.3)), 3)],
        "vx_max": round(float(rng.uniform(0.40, 0.60)), 3),
        "sigma_d_max_m": round(float(rng.uniform(0.03, 0.06)), 4),
        "sigma_psi_max_grados": round(float(rng.uniform(3.0, 5.0)), 2),
        "seed": int(rng.integers(0, 2**31 - 1)),
    }


def config_agente(s: dict, pasos: int, n_envs: int, nombre: str) -> dict:
    cfg = yaml.safe_load(BASE_CONFIG.read_text(encoding="utf-8"))
    cfg = copy.deepcopy(cfg)
    cfg["experiment"] = f"barrido_{nombre}"
    cfg["seed"] = s["seed"]
    cfg["total_timesteps"] = pasos
    cfg["n_envs"] = n_envs
    cfg["checkpoint_every"] = max(pasos, 1)
    cfg["eval"] = {"every": max(pasos // 2, 1), "n_episodes": 2}
    env = cfg["env"]
    env["pesos"] = s["pesos"]
    env["friction_range"] = s["friction_range"]
    env["vx_rango"] = [0.15, s["vx_max"]]
    # Se MEZCLA con la camara de la base (apagones y perdida de vision de v02/v03): solo cambia el ruido.
    env["camara"] = {**env.get("camara", {}), "sigma_d_m": [0.01, s["sigma_d_max_m"]],
                     "sigma_psi_grados": [1.0, s["sigma_psi_max_grados"]]}
    return cfg


def puntaje(filas: list) -> dict:
    """Seccion 11.4: filtro duro (cualquier choque, salida o caida descarta) y luego media + 1 sigma del tiempo."""
    faltas = sum(f["resultado"] != "META" for f in filas)
    ts = [f["t"] for f in filas if f["resultado"] == "META"]
    desvio = max(f["desvio_max"] for f in filas)
    if faltas:
        return {"pasa_filtro": False, "faltas": faltas, "puntaje": None, "desvio_max_cm": 100 * desvio}
    return {"pasa_filtro": True, "faltas": 0, "puntaje": float(np.mean(ts) + np.std(ts)),
            "t_medio": float(np.mean(ts)), "desvio_max_cm": 100 * desvio}


SALIDAS_MALAS = ((0.10, 15.0), (-0.10, -15.0), (0.0, 25.0), (0.0, -25.0))   # (y0 [m], rumbo0 [grados]), mu 0.6


def evaluar(modelo: Path, semillas: int, vx: float) -> list:
    """Bateria corta, con vision y perturbaciones: 5 fricciones x semillas (colocacion del benchmark) + 4 salidas
    torcidas (paso 58c). Todas cuentan para el filtro duro."""
    import math
    import eval_carrera
    model, vn, env_kwargs, _ = eval_carrera.cargar(modelo)
    filas = []
    for mu in (0.4, 0.6, 0.8, 1.0, 1.2):
        for s in range(1000, 1000 + semillas):
            f = eval_carrera.correr(model, vn, env_kwargs, mu, s, True, vx, True)
            f.pop("traza", None)
            f["tipo"] = "normal"
            filas.append(f)
    for y0, r0 in SALIDAS_MALAS:
        f = eval_carrera.correr(model, vn, env_kwargs, 0.6, 1000, True, vx, True, colocacion=(y0, math.radians(r0)))
        f.pop("traza", None)
        f.update(tipo="salida_mala", y0_cm=100 * y0, rumbo0_grados=r0)
        filas.append(f)
    return filas


def no_suspender():
    """Pide a Windows no suspender el PC mientras corre el barrido (sin cambiar la configuracion; se libera al salir)."""
    import os
    if os.name == "nt":
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)   # ES_CONTINUOUS | ES_SYSTEM_REQUIRED


def escribir_tabla(carpeta: Path) -> None:
    res = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(carpeta.glob("agente_*/resultado.json"))]
    res.sort(key=lambda r: (not r["puntaje"]["pasa_filtro"], r["puntaje"]["puntaje"] or 1e9,
                            r["puntaje"]["desvio_max_cm"]))
    L = [f"# Barrido `{carpeta.name}`", "", f"{len(res)} agentes evaluados. Puntaje (seccion 11.4): filtro duro "
         "(cualquier caida o salida descarta) y luego tiempo medio + 1 sigma; desempate por desvio maximo.", "",
         "| # | Agente | Pasa | Faltas | Puntaje [s] | t medio [s] | Desvio max [cm] | vx_max | Friccion | "
         "salida | caida | centrado | barrera | rumbo | seguimiento_vx |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, r in enumerate(res, 1):
        p, s = r["puntaje"], r["sorteo"]
        w = s["pesos"]
        L.append(f"| {k} | {r['agente']} | {'si' if p['pasa_filtro'] else 'no'} | {p['faltas']} | "
                 f"{p['puntaje']:.2f} | {p['t_medio']:.2f} | " if p["pasa_filtro"] else
                 f"| {k} | {r['agente']} | no | {p['faltas']} | — | — | ")
        L[-1] += (f"{p['desvio_max_cm']:.1f} | {s['vx_max']} | {s['friction_range']} | {w['salida_carril']:.0f} | "
                  f"{w['caida']:.0f} | {w['centrado']:.2f} | {w['barrera_margen']:.1f} | {w['rumbo']:.2f} | "
                  f"{w['seguimiento_vx']:.2f} |")
    (carpeta / "tabla.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nombre", required=True)
    ap.add_argument("--agentes", type=int, default=100)
    ap.add_argument("--pasos", type=int, default=1_000_000)
    ap.add_argument("--base", type=Path, default=ROOT / "policies" / "rl_v1.0")
    ap.add_argument("--n-envs", type=int, default=16)
    ap.add_argument("--semilla", type=int, default=0, help="semilla del sorteo de los agentes")
    ap.add_argument("--eval-semillas", type=int, default=2)
    ap.add_argument("--eval-vx", type=float, default=0.45, help="vx_cmd de la bateria de evaluacion")
    a = ap.parse_args()

    carpeta = ROOT / "results" / "barridos" / a.nombre
    carpeta.mkdir(parents=True, exist_ok=True)
    no_suspender()
    (carpeta / "barrido.yaml").write_text(yaml.safe_dump(vars(a) | {"base": str(a.base)}, sort_keys=False),
                                          encoding="utf-8")
    for i in range(a.agentes):
        ag = f"agente_{i:03d}"
        dir_ag = carpeta / ag
        if (dir_ag / "resultado.json").exists():
            print(f"{ag}: ya evaluado, se salta")
            continue
        dir_ag.mkdir(exist_ok=True)
        s = sortear(i, a.semilla)
        cfg = config_agente(s, a.pasos, a.n_envs, a.nombre)
        (dir_ag / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")
        run = f"barrido_{a.nombre}_{i:03d}"
        modelo = ROOT / "runs" / run / "final_model.zip"
        t0 = time.time()
        if not modelo.exists():
            if (ROOT / "runs" / run).exists():      # entrenamiento interrumpido: se repite desde cero
                import shutil
                shutil.rmtree(ROOT / "runs" / run)
            print(f"{ag}: entrenando {a.pasos:,} pasos (vx_max {s['vx_max']}, friccion {s['friction_range']})", flush=True)
            r = subprocess.run([PY, "-m", "src.train", "--config", str(dir_ag / "config.yaml"), "--run-name", run,
                                "--continuar", str(a.base)], cwd=ROOT, capture_output=True, text=True)
            (dir_ag / "entrenamiento.log").write_text(r.stdout + r.stderr, encoding="utf-8")
            if r.returncode != 0 or not modelo.exists():
                print(f"{ag}: ERROR al entrenar (ver {dir_ag.relative_to(ROOT)}/entrenamiento.log)")
                return 1
        filas = evaluar(modelo, a.eval_semillas, a.eval_vx)
        p = puntaje(filas)
        res = {"agente": ag, "run": run, "sorteo": s, "pasos": a.pasos, "base": str(a.base), "eval_vx": a.eval_vx,
               "puntaje": p, "corridas": filas, "seg": round(time.time() - t0, 1)}
        (dir_ag / "resultado.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
        print(f"{ag}: {'PASA' if p['pasa_filtro'] else 'descartado'} faltas={p['faltas']} "
              f"puntaje={p['puntaje']} ({res['seg']:.0f} s)", flush=True)
        escribir_tabla(carpeta)
    escribir_tabla(carpeta)
    print(f"Tabla: {(carpeta / 'tabla.md').relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
