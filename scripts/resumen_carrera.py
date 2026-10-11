"""Junta todas las evaluaciones de carrera (results/carrera/*/eval_*.json) en una tabla: results/carrera/resumen.md.

Por cada evaluacion (modelo, vx_cmd, con o sin perturbaciones) y cada condicion de vision da metas, caidas, salidas,
tiempo medio a la meta, desvio maximo medio y si pasa el filtro duro de la seccion 11.4 (0 faltas). Incluye la fila
de B-Human del benchmark de 3 carriles como referencia.

Uso:
    uv run python scripts/resumen_carrera.py
"""

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def filas_de(ruta: Path):
    d = json.loads(ruta.read_text(encoding="utf-8"))
    meta, corr = d["meta"], d["corridas"]
    for v in (1, 0):
        cs = [c for c in corr if c["vision"] == v]
        if not cs:
            continue
        metas = [c for c in cs if c["resultado"] == "META"]
        yield {
            "modelo": meta["modelo"], "vx": meta["vx_cmd"], "pert": meta["perturbaciones"], "vision": v, "n": len(cs),
            "metas": len(metas), "caidas": sum(c["resultado"] == "CAIDA" for c in cs),
            "salidas": sum(c["resultado"] == "SALIO DEL CARRIL" for c in cs),
            "t": float(np.mean([c["t"] for c in metas])) if metas else None,
            "t_std": float(np.std([c["t"] for c in metas])) if metas else None,
            "desvio": 100 * float(np.mean([c["desvio_max"] for c in cs])),
        }


def main() -> int:
    filas = []
    for p in sorted((ROOT / "results" / "carrera").glob("*/**/eval_*.json")):
        filas += list(filas_de(p))
    filas.sort(key=lambda f: (f["vision"] == 0, f["pert"], -f["vx"], f["modelo"]))
    b = json.loads((ROOT / "results" / "benchmark" / "benchmark.json").read_text(encoding="utf-8"))
    bh = [r for r in b["resumen"] if r["caminata"] == "bhuman"]
    L = ["# Resumen de las evaluaciones de carrera", "",
         "Generado por `scripts/resumen_carrera.py` a partir de `results/carrera/*/eval_*.json` (`scripts/eval_carrera.py`).",
         "Batería: μ 0.4–1.2, colocación del benchmark (semillas 1000…). **Pasa** = 0 caídas y 0 salidas (sección 11.4).",
         "", "**Referencia, B-Human (benchmark de 3 carriles, sin perturbaciones):** con visión "
         f"{sum(r['metas'] for r in bh if r['vision'])}/{sum(r['n'] for r in bh if r['vision'])} metas en "
         f"{min(r['t_meta_medio'] for r in bh if r['vision']):.1f}–{max(r['t_meta_medio'] for r in bh if r['vision']):.1f} s; "
         f"sin visión {sum(r['metas'] for r in bh if not r['vision'])}/{sum(r['n'] for r in bh if not r['vision'])} metas.",
         "", "| Visión | Perturb. | vx_cmd | Modelo | Metas | Caídas | Salidas | Pasa | Tiempo a meta [s] | Desvío máx. medio [cm] |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for f in filas:
        t = "—" if f["t"] is None else f"{f['t']:.2f} ± {f['t_std']:.2f}"
        L.append(f"| {'sí' if f['vision'] else 'no'} | {'sí' if f['pert'] else 'no'} | {f['vx']:.2f} | `{f['modelo']}` | "
                 f"{f['metas']}/{f['n']} | {f['caidas']} | {f['salidas']} | "
                 f"{'**sí**' if f['caidas'] + f['salidas'] == 0 else 'no'} | {t} | {f['desvio']:.1f} |")
    salida = ROOT / "results" / "carrera" / "resumen.md"
    salida.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
