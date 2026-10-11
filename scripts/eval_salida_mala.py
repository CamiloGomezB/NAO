"""Bateria de SALIDAS MALAS (paso 58c del PLAN, registro de errores E50).

Coloca al robot corrido y girado en la salida, en una rejilla de casos, y mide si llega a la meta sin faltas. Sirve
para confirmar que la camara lo corrige "sin importar la situacion" de arranque. Usa scripts/eval_carrera.py (mismas
metricas, misma meta) con la colocacion fija de cada celda.

Rejilla por defecto: corrimiento y0 en {0, +-10, +-15} cm x rumbo en {0, +-8, +-15, +-25} grados, 2 semillas por celda,
con y sin vision, mu 0.8, vx_cmd 0.40. Positivos: y + = robot a la izquierda; rumbo + = girado a la izquierda.

Uso:
    uv run python scripts/eval_salida_mala.py --modelo policies/carrera_v02/model.zip
    uv run python scripts/eval_salida_mala.py --modelo policies/carrera_v02/model.zip --rumbo-objetivo arranque
    uv run python scripts/eval_salida_mala.py --modelo ... --perturbaciones --mu 0.4 0.8 1.2
Escribe results/carrera/<run>/salida_mala_<modelo>_<rumbo>[_pert].{json,md}.
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
sys.path.insert(0, str(ROOT / "scripts"))

import eval_carrera  # noqa: E402
from src.evaluate import rel  # noqa: E402

YS_CM = (0, 10, -10, 15, -15)
RUMBOS_GRADOS = (0, 8, -8, 15, -15, 25, -25)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--modelo", type=Path, required=True)
    ap.add_argument("--vx", type=float, default=0.40)
    ap.add_argument("--mu", type=float, nargs="+", default=[0.8])
    ap.add_argument("--semillas", type=int, default=2)
    ap.add_argument("--perturbaciones", action="store_true")
    ap.add_argument("--rumbo-objetivo", choices=("carril", "arranque"), default=None)
    ap.add_argument("--salida", type=Path, default=None)
    a = ap.parse_args()

    model, vn, env_kwargs, _ = eval_carrera.cargar(a.modelo)
    modo = a.rumbo_objetivo or env_kwargs.get("rumbo_objetivo", "carril")
    t0 = time.time()
    filas = []
    for vision in (True, False):
        for y in YS_CM:
            for rumbo in RUMBOS_GRADOS:
                for mu in a.mu:
                    for s in range(1000, 1000 + a.semillas):
                        f = eval_carrera.correr(model, vn, env_kwargs, mu, s, vision, a.vx, a.perturbaciones,
                                                rumbo_objetivo=a.rumbo_objetivo,
                                                colocacion=(y / 100.0, math.radians(rumbo)))
                        f.pop("traza", None)
                        f.update(y0_cm=y, rumbo0_grados=rumbo)
                        filas.append(f)
        print(f"   vision={'si' if vision else 'no'}: {sum(f['resultado'] == 'META' for f in filas if f['vision'] == vision)}"
              f"/{sum(f['vision'] == vision for f in filas)} metas", flush=True)

    nombre = a.modelo.parent.name if a.modelo.parent.name != "checkpoints" else a.modelo.parent.parent.name
    salida = a.salida or ROOT / "results" / "carrera" / nombre
    salida.mkdir(parents=True, exist_ok=True)
    tag = f"salida_mala_{a.modelo.stem}_{modo}{'_pert' if a.perturbaciones else ''}"
    meta = {"modelo": rel(a.modelo), "rumbo_objetivo": modo, "vx_cmd": a.vx, "mu": a.mu, "semillas": a.semillas,
            "perturbaciones": a.perturbaciones, "ys_cm": YS_CM, "rumbos_grados": RUMBOS_GRADOS,
            "seg": round(time.time() - t0, 1)}
    (salida / f"{tag}.json").write_text(json.dumps({"meta": meta, "corridas": filas}, indent=1), encoding="utf-8")

    L = [f"# Salidas malas: `{rel(a.modelo)}`", "",
         f"`scripts/eval_salida_mala.py`. Rumbo objetivo de la IMU: **{modo}**. vx_cmd {a.vx}, mu {a.mu}, "
         f"{a.semillas} semillas por celda, perturbaciones {'si' if a.perturbaciones else 'no'}. Cada celda: metas / "
         "corridas y tiempo medio. y + = robot a la izquierda; rumbo + = girado a la izquierda.", ""]
    for vision in (True, False):
        fs = [f for f in filas if f["vision"] == vision]
        L += [f"## {'Con' if vision else 'Sin'} vision — {sum(f['resultado'] == 'META' for f in fs)}/{len(fs)} metas, "
              f"{sum(f['resultado'] == 'CAIDA' for f in fs)} caidas, {sum(f['resultado'] == 'SALIO DEL CARRIL' for f in fs)} "
              "salidas", "", "| y0 \\ rumbo0 | " + " | ".join(f"{r:+d}°" for r in RUMBOS_GRADOS) + " |",
              "|---|" + "---|" * len(RUMBOS_GRADOS)]
        for y in YS_CM:
            celdas = []
            for r in RUMBOS_GRADOS:
                c = [f for f in fs if f["y0_cm"] == y and f["rumbo0_grados"] == r]
                m = [f for f in c if f["resultado"] == "META"]
                celdas.append(f"{len(m)}/{len(c)}" + (f" {np.mean([f['t'] for f in m]):.1f} s" if m else ""))
            L.append(f"| {y:+d} cm | " + " | ".join(celdas) + " |")
        L.append("")
    (salida / f"{tag}.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Escrito {rel(salida / (tag + '.md'))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
