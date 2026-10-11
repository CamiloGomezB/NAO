"""Exporta TODAS las curvas de TensorBoard de un run a results/ (runs/ no se versiona) y dibuja las principales.

Escribe results/carrera/<run>/curvas_entrenamiento.csv (formato largo: etiqueta, paso, valor, tiempo) y
results/carrera/<run>/curvas_entrenamiento.png (terminos de recompensa, faltas, metas, largo de episodio y PPO).

Uso:
    uv run python scripts/exportar_curvas.py --run carrera_v01
"""

import argparse
import csv
import glob
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    a = ap.parse_args()
    from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
    eventos = sorted(glob.glob(str(ROOT / "runs" / a.run / "tb" / "**" / "events.*"), recursive=True))
    if not eventos:
        print(f"ERROR: no hay eventos de TensorBoard en runs/{a.run}/tb")
        return 1
    datos = {}
    for f in eventos:
        ea = EventAccumulator(f, size_guidance={"scalars": 0})
        ea.Reload()
        for tag in ea.Tags()["scalars"]:
            datos.setdefault(tag, []).extend((e.step, e.value, e.wall_time) for e in ea.Scalars(tag))
    salida = ROOT / "results" / "carrera" / a.run
    salida.mkdir(parents=True, exist_ok=True)
    with open(salida / "curvas_entrenamiento.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["etiqueta", "paso", "valor", "tiempo_unix"])
        for tag in sorted(datos):
            for paso, valor, t in sorted(datos[tag]):
                w.writerow([tag, paso, f"{valor:.6g}", f"{t:.1f}"])
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    def serie(tag, suav=5):
        s = sorted(datos.get(tag, []))
        if not s:
            return np.array([]), np.array([])
        x, y = np.array([p for p, _, _ in s]) / 1e6, np.array([v for _, v, _ in s])
        if len(y) > suav:
            y = np.convolve(y, np.ones(suav) / suav, mode="same")
        return x, y

    fig, ax = plt.subplots(2, 2, figsize=(14, 9))
    for tag in sorted(t for t in datos if t.startswith("reward_terms/")):
        x, y = serie(tag)
        ax[0, 0].plot(x, y, label=tag.split("/")[1], lw=1.2)
    ax[0, 0].set_title("Aporte por paso de cada termino de recompensa (ya multiplicado por su peso)")
    ax[0, 0].axhline(0, color="k", lw=0.5)
    ax[0, 0].legend(fontsize=7, ncol=3)
    for tag, nombre in (("episodes/fall_rate", "episodios con falta (caida o salida)"),
                        ("episodes/fall_salida_carril", "episodios con salida de carril"),
                        ("episodes/meta_rate", "episodios que llegan a la meta")):
        x, y = serie(tag)
        ax[0, 1].plot(x, y, label=nombre)
    ax[0, 1].set_title("Faltas y metas (fraccion de episodios por rollout)")
    ax[0, 1].legend(fontsize=8)
    x, y = serie("rollout/ep_len_mean", 1)
    ax[1, 0].plot(x, y * 0.024, label="largo medio del episodio [s] (max 30)")
    x, y = serie("rollout/ep_rew_mean", 1)
    ax2 = ax[1, 0].twinx()
    ax2.plot(x, y, color="C3", label="retorno medio")
    ax[1, 0].set_title("Episodios")
    ax[1, 0].legend(loc="upper left", fontsize=8)
    ax2.legend(loc="lower right", fontsize=8)
    for tag in ("train/std", "train/approx_kl", "train/clip_fraction", "train/explained_variance"):
        x, y = serie(tag, 1)
        ax[1, 1].plot(x, y, label=tag.split("/")[1])
    ax[1, 1].set_title("PPO")
    ax[1, 1].legend(fontsize=8)
    for a_ in ax.flat:
        a_.set_xlabel("millones de pasos (de este run)")
    fig.suptitle(f"Entrenamiento {a.run}")
    fig.tight_layout()
    fig.savefig(salida / "curvas_entrenamiento.png", dpi=100)
    print(f"{len(datos)} curvas, {sum(len(v) for v in datos.values())} puntos -> {salida.relative_to(ROOT).as_posix()}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
