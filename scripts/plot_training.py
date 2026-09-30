"""Grafica las curvas de entrenamiento de varios runs (leidas de TensorBoard) en una sola figura.

Uso (desde la raiz del repo):
    uv run python scripts/plot_training.py
    uv run python scripts/plot_training.py --runs ppo_base_5M ppo_natural_5M --out results/training_curves.png
"""

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DT = 0.02  # s por paso de control (ep_len_mean esta en pasos)

# Paleta categorica validada (orden fijo: azul, naranja, aqua) y tintas de texto.
SERIES_COLORS = ["#2a78d6", "#eb6834", "#1baf7a"]
SURFACE, TEXT, TEXT_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e0"

DEFAULT_RUNS = {
    "ppo_base_5M": "Base (configs/ppo.yaml)",
    "ppo_natural_5M": "V1 natural (ppo_natural.yaml)",
    "ppo_brazos_5M": "V2 brazos (ppo_brazos.yaml)",
}
PANELS = [
    ("rollout/ep_rew_mean", "Retorno medio por episodio", 1.0, 450, "quieto de pie"),
    ("rollout/ep_len_mean", "Duracion media del episodio [s]", DT, 20, "maximo (20 s)"),
    ("reward_terms/velocidad_avance", "Termino de velocidad de avance (1 = objetivo)", 1.0, None, None),
    ("episodes/fall_rate", "Tasa de caidas por episodio", 1.0, None, None),
]


def load_scalars(run: str) -> dict[str, tuple[list, list]]:
    files = sorted((ROOT / "runs" / run / "tb").glob("PPO_*/events.out.tfevents.*"))
    if not files:
        return {}
    acc = EventAccumulator(str(files[-1]), size_guidance={"scalars": 0})
    acc.Reload()
    data = {}
    for tag, *_ in PANELS:
        if tag in acc.Tags()["scalars"]:
            events = acc.Scalars(tag)
            data[tag] = ([e.step / 1e6 for e in events], [e.value for e in events])
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--runs", nargs="+", default=list(DEFAULT_RUNS))
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "training_curves.png")
    args = parser.parse_args()

    runs = {run: load_scalars(run) for run in args.runs}
    runs = {run: data for run, data in runs.items() if data}
    if not runs:
        print("ERROR: no se encontraron logs de TensorBoard para esos runs.")
        return 1

    plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": TEXT_2,
                         "xtick.color": TEXT_2, "ytick.color": TEXT_2, "text.color": TEXT})
    fig, axes = plt.subplots(2, 2, figsize=(12, 7.5), facecolor=SURFACE)
    for ax, (tag, title, scale, ref, ref_label) in zip(axes.flat, PANELS):
        ax.set_facecolor(SURFACE)
        ax.grid(True, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for (run, data), color in zip(runs.items(), SERIES_COLORS):
            if tag in data:
                steps, values = data[tag]
                ax.plot(steps, [v * scale for v in values], color=color, linewidth=2,
                        label=DEFAULT_RUNS.get(run, run))
        if ref is not None:
            ax.axhline(ref, color=TEXT_2, linewidth=1, linestyle="--")
            ax.annotate(ref_label, xy=(0.99, ref), xycoords=("axes fraction", "data"), ha="right",
                        va="bottom", fontsize=9, color=TEXT_2)
        ax.set_title(title, loc="left", fontsize=11, color=TEXT, pad=8)
        ax.set_xlabel("Pasos de entrenamiento [millones]")

    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.suptitle("Entrenamiento PPO del NAO: curvas por variante", x=0.01, y=0.99, ha="left",
                 fontsize=13, fontweight="bold", color=TEXT)
    fig.legend(handles, labels, loc="upper left", ncol=len(labels), frameon=False,
               bbox_to_anchor=(0.005, 0.955), fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.91))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=130, facecolor=SURFACE)
    shown = args.out.resolve().relative_to(ROOT) if args.out.resolve().is_relative_to(ROOT) else args.out
    print(f"Grafica: {Path(shown).as_posix()} ({', '.join(runs)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
