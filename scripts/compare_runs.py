"""Compara variantes: evalua el mejor modelo de cada run con las mismas semillas y genera una tabla.

Uso (desde la raiz del repo):
    uv run python scripts/compare_runs.py
    uv run python scripts/compare_runs.py --runs ppo_base_5M ppo_natural_5M --episodes 20
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABELS = {
    "ppo_base_5M": "Base",
    "ppo_natural_5M": "V1 natural",
    "ppo_brazos_5M": "V2 brazos",
}
COLUMNS = [  # (clave, encabezado, formato)
    ("distancia_m", "Distancia [m]", "{:.2f}"),
    ("velocidad_media_ms", "Velocidad [m/s]", "{:.3f}"),
    ("duracion_s", "Duración [s]", "{:.1f}"),
    ("desviacion_lateral_m", "Desv. lateral [m]", "{:+.2f}"),
    ("inclinacion_max_deg", "Inclinación máx. [°]", "{:.1f}"),
    ("doble_apoyo_pct", "Doble apoyo [%]", "{:.1f}"),
    ("altura_pie_izq_cm", "Pie izq. [cm]", "{:.1f}"),
    ("altura_pie_der_cm", "Pie der. [cm]", "{:.1f}"),
    ("esfuerzo_medio", "Esfuerzo Σ τ²", "{:.2f}"),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--runs", nargs="+", default=list(LABELS))
    parser.add_argument("--episodes", type=int, default=20)
    parser.add_argument("--seed", type=int, default=1000)
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "comparison.md")
    args = parser.parse_args()

    reports = {}
    for run in args.runs:
        model = ROOT / "runs" / run / "best_model.zip"
        if not model.exists():
            print(f"(se omite {run}: no existe {model.relative_to(ROOT).as_posix()})")
            continue
        out_json = ROOT / "runs" / run / f"eval_{args.episodes}ep.json"
        print(f"Evaluando {run} ({args.episodes} episodios)...", flush=True)
        subprocess.run([sys.executable, "-m", "src.evaluate", "--model", str(model), "--episodes",
                        str(args.episodes), "--seed", str(args.seed), "--json", str(out_json)],
                       cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
        reports[run] = json.loads(out_json.read_text(encoding="utf-8"))

    if not reports:
        print("ERROR: ningun run evaluado.")
        return 1

    header = ["Variante", "Caídas"] + [c[1] for c in COLUMNS]
    lines = [
        f"# Comparación de variantes ({args.episodes} episodios, semillas {args.seed}–{args.seed + args.episodes - 1}, "
        "acciones deterministas)",
        "",
        "Valores: media ± desviación estándar sobre los episodios. Cada episodio dura como máximo 20 s.",
        "",
        "| " + " | ".join(header) + " |",
        "|" + "|".join(["---"] * len(header)) + "|",
    ]
    for run, rep in reports.items():
        summary = rep["resumen"]
        cells = [f"**{LABELS.get(run, run)}** (`{run}`)", f"{summary['tasa_caidas'] * 100:.0f} %"]
        for key, _, fmt in COLUMNS:
            cells.append(f"{fmt.format(summary[key]['media'])} ± {fmt.format(summary[key]['desv']).lstrip('+')}")
        lines.append("| " + " | ".join(cells) + " |")
    lines += [
        "",
        "Configuraciones: `configs/ppo.yaml` (Base), `configs/ppo_natural.yaml` (V1), `configs/ppo_brazos.yaml` (V2).",
        "Regenerar: `uv run python scripts/compare_runs.py`.",
    ]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n" + "\n".join(lines[4:4 + 2 + len(reports)]))
    print(f"\nTabla: {args.out.as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
