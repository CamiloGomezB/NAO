"""Ronda siguiente de un barrido: los mejores de una ronda siguen entrenando y se evaluan con la bateria COMPLETA
(paso 62 del PLAN; diseno, seccion 11.2).

Para cada agente de results/barridos/<anterior>/mejores.json (lo escribe scripts/analizar_barrido.py):
  1. toma SU config de la ronda anterior (sus pesos, friccion, velocidad y ruido de camara) y le cambia solo el
     numero de pasos;
  2. sigue entrenando desde SU modelo final de la ronda anterior (`src.train --continuar runs/barrido_<anterior>_NNN/
     final_model.zip`) en runs/barrido_<nombre>_NNN;
  3. evalua CADA checkpoint (cada pasos/5) con la bateria completa y se queda con el mejor segun la seccion 11.4
     (registro E48 y E54: entrenar mas puede empeorar; se elige por bateria y no el ultimo modelo).
     Bateria completa: con vision y perturbaciones, vx_cmd 0.45,
       - normal: mu 0.4, 0.6, 0.8, 1.0, 1.2 x 4 semillas (colocacion del benchmark) = 20 corridas;
       - salidas torcidas: y0 0/+10/-10 cm x rumbo0 +15/-15/+25/-25 grados x mu 0.4 y 1.0 = 24 corridas;
  4. guarda results/barridos/<nombre>/agente_NNN/{config.yaml, entrenamiento.log, resultado.json} con el mismo formato
     que scripts/barrido.py (asi sirven escribir_tabla y scripts/analizar_barrido.py).
Es REANUDABLE como barrido.py. Pide a Windows no suspender el PC mientras corre.

Uso:
    uv run python scripts/ronda_siguiente.py --anterior ronda1 --nombre ronda2 --pasos 5000000
"""

import argparse
import json
import math
import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import barrido  # noqa: E402

PY = sys.executable
SALIDAS_TORCIDAS = [(y / 100.0, r) for y in (0, 10, -10) for r in (15.0, -15.0, 25.0, -25.0)]


def evaluar_completa(modelo: Path, vx: float) -> list:
    import eval_carrera
    model, vn, env_kwargs, _ = eval_carrera.cargar(modelo)
    filas = []
    for mu in (0.4, 0.6, 0.8, 1.0, 1.2):
        for s in range(1000, 1004):
            f = eval_carrera.correr(model, vn, env_kwargs, mu, s, True, vx, True)
            f.pop("traza", None)
            f["tipo"] = "normal"
            filas.append(f)
    for mu in (0.4, 1.0):
        for y0, r0 in SALIDAS_TORCIDAS:
            f = eval_carrera.correr(model, vn, env_kwargs, mu, 1000, True, vx, True, colocacion=(y0, math.radians(r0)))
            f.pop("traza", None)
            f.update(tipo="salida_mala", y0_cm=100 * y0, rumbo0_grados=r0)
            filas.append(f)
    return filas


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--anterior", required=True)
    ap.add_argument("--nombre", required=True)
    ap.add_argument("--pasos", type=int, default=5_000_000)
    ap.add_argument("--eval-vx", type=float, default=0.45)
    ap.add_argument("--max-agentes", type=int, default=None, help="solo los primeros N (pruebas)")
    a = ap.parse_args()
    previa = ROOT / "results" / "barridos" / a.anterior
    lista = json.loads((previa / "mejores.json").read_text(encoding="utf-8"))[: a.max_agentes]
    carpeta = ROOT / "results" / "barridos" / a.nombre
    carpeta.mkdir(parents=True, exist_ok=True)
    barrido.no_suspender()
    (carpeta / "barrido.yaml").write_text(yaml.safe_dump(vars(a) | {"agentes": lista}, sort_keys=False),
                                          encoding="utf-8")
    for ag in lista:
        dir_ag = carpeta / ag
        if (dir_ag / "resultado.json").exists():
            print(f"{ag}: ya evaluado, se salta")
            continue
        dir_ag.mkdir(exist_ok=True)
        r_prev = json.loads((previa / ag / "resultado.json").read_text(encoding="utf-8"))
        cfg = yaml.safe_load((previa / ag / "config.yaml").read_text(encoding="utf-8"))
        cfg["experiment"] = f"barrido_{a.nombre}"
        cfg["total_timesteps"] = a.pasos
        cfg["checkpoint_every"] = max(a.pasos // 5, 1)
        cfg["eval"] = {"every": max(a.pasos // 5, 1), "n_episodes": 3}
        (dir_ag / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")
        num = ag.split("_")[1]
        run = f"barrido_{a.nombre}_{num}"
        base = ROOT / "runs" / r_prev["run"] / "final_model.zip"
        modelo = ROOT / "runs" / run / "final_model.zip"
        t0 = time.time()
        # Entrenamiento valido = modelo final no vacio y con checkpoints. Un entrenamiento cortado puede dejar un
        # final_model.zip de 0 bytes (registro de errores E54): entonces se borra y se repite.
        ck_dir = ROOT / "runs" / run / "checkpoints"
        valido = modelo.exists() and modelo.stat().st_size > 0 and any(ck_dir.glob("model_*_steps.zip"))
        if not valido:
            if (ROOT / "runs" / run).exists():
                shutil.rmtree(ROOT / "runs" / run)
            print(f"{ag}: entrenando {a.pasos:,} pasos desde {r_prev['run']}", flush=True)
            r = subprocess.run([PY, "-m", "src.train", "--config", str(dir_ag / "config.yaml"), "--run-name", run,
                                "--continuar", str(base)], cwd=ROOT, capture_output=True, text=True)
            (dir_ag / "entrenamiento.log").write_text(r.stdout + r.stderr, encoding="utf-8")
            if r.returncode != 0 or not modelo.exists():
                print(f"{ag}: ERROR al entrenar (ver {dir_ag.relative_to(ROOT)}/entrenamiento.log)")
                return 1
        # Cada checkpoint con la bateria completa; el elegido es el mejor (pasa el filtro y menor puntaje; si
        # ninguno pasa, el de menos faltas).
        cks = sorted((ROOT / "runs" / run / "checkpoints").glob("model_*_steps.zip"),
                     key=lambda f: int(f.stem.split("_")[1]))
        cks = cks or [modelo]
        evals = []
        for ck in cks:
            fs = evaluar_completa(ck, a.eval_vx)
            evals.append((int(ck.stem.split("_")[1]), ck, fs, barrido.puntaje(fs)))
            print(f"   {ag} {evals[-1][0] / 1e6:.0f}M: faltas={evals[-1][3]['faltas']} puntaje={evals[-1][3]['puntaje']}",
                  flush=True)
        clave = lambda e: (not e[3]["pasa_filtro"], e[3]["faltas"], e[3]["puntaje"] or 1e9)  # noqa: E731
        pasos_el, ck_el, filas, p = min(evals, key=clave)
        res = {"agente": ag, "run": run, "checkpoint_elegido": ck_el.relative_to(ROOT).as_posix(),
               "pasos_elegidos": pasos_el,
               "checkpoints": [{"pasos": e[0], "puntaje": e[3]} for e in evals], "sorteo": r_prev["sorteo"], "pasos": a.pasos,
               "pasos_totales_sobre_base": r_prev["pasos"] + a.pasos, "continua_de": r_prev["run"],
               "puntaje_ronda_anterior": r_prev["puntaje"], "eval_vx": a.eval_vx, "bateria": "completa (44 corridas)",
               "puntaje": p, "corridas": filas, "seg": round(time.time() - t0, 1)}
        (dir_ag / "resultado.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
        print(f"{ag}: {'PASA' if p['pasa_filtro'] else 'descartado'} (checkpoint {pasos_el / 1e6:.0f}M) "
              f"faltas={p['faltas']} puntaje={p['puntaje']} ({res['seg']:.0f} s)", flush=True)
        barrido.escribir_tabla(carpeta)
    barrido.escribir_tabla(carpeta)
    print(f"Tabla: {(carpeta / 'tabla.md').relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
