"""Perfiles de velocidad de los motores de rodillas y tobillos (2026-10-15).

Registra la velocidad angular de cada articulacion en cada paso de fisica (2 ms), con el mismo mecanismo que
scripts/riesgo_motores.py, para rl_v1.2.1, la replica de B-Human y rl_v1.1 (mu 0.8, semilla 1000, con vision, sin
perturbaciones; el RL a vx_cmd 0.45). Dibuja 2 s de marcha estable (de 4 a 6 s desde que empieza el registro) de
LKneePitch, RKneePitch, LAnklePitch y RAnklePitch, con la velocidad maxima del motor real (sin carga, 6.96 rad/s).

Uso:
    uv run python scripts/perfiles_velocidad.py      # results/esfuerzo_motores/perfiles_velocidad.{png,json}
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import riesgo_motores as RM  # noqa: E402

JUNTAS = ["LKneePitch", "RKneePitch", "LAnklePitch", "RAnklePitch"]
W0 = RM.TIPO5["w0"]                      # velocidad sin carga del motor tipo 5 en la articulacion [rad/s]
VENTANA = (4.0, 6.0)                     # s desde que empieza el registro
DT = 0.002
# Paleta de referencia validada (scripts/validate_palette.js de la guia de visualizacion): orden fijo de categorias.
CAMINATAS = [
    ("rl_v1.2.1", "RL v1.2.1", "#2a78d6", lambda: RM.correr_rl(ROOT / "policies/rl_v1.2.1/model.zip", 0.45, 1000, 0.8)),
    ("bhuman", "B-Human", "#eb6834", lambda: RM.correr_clasica("bhuman", 1000, 0.8)),
    ("rl_v1.1", "RL v1.1", "#1baf7a", lambda: RM.correr_rl(ROOT / "policies/rl_v1.1/model.zip", 0.45, 1000, 0.8)),
]
TINTA, TINTA2, REJILLA, CRITICO, FONDO = "#0b0b0b", "#52514e", "#e8e7e2", "#d03b3b", "#fcfcfb"


def registrar():
    import mujoco
    mujoco.mj_step = RM._paso_registrado
    datos = {}
    for clave, nombre, _, correr in CAMINATAS:
        f = correr()
        w = np.array(RM.REG.w)[:, [RM.JUNTAS.index(j) for j in JUNTAS]]
        a, b = int(VENTANA[0] / DT), int(VENTANA[1] / DT)
        datos[clave] = {
            "nombre": nombre, "resultado": f["resultado"], "t_meta_s": round(float(f["t"]), 2),
            "resumen": {j: {"p99_abs": round(float(np.percentile(np.abs(w[:, k]), 99)), 2),
                            "max_abs": round(float(np.max(np.abs(w[:, k]))), 2),
                            "pct_sobre_w0": round(float(100 * np.mean(np.abs(w[:, k]) > W0)), 2)}
                        for k, j in enumerate(JUNTAS)},
            "ventana": {j: np.round(w[a:b, k], 3).tolist() for k, j in enumerate(JUNTAS)},
        }
        print(nombre, f["resultado"], round(f["t"], 2), "s", flush=True)
    mujoco.mj_step = RM._MJ_STEP
    return datos


def dibujar(datos, salida):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": REJILLA,
                         "axes.labelcolor": TINTA2, "xtick.color": TINTA2, "ytick.color": TINTA2})
    fig, axs = plt.subplots(2, 2, figsize=(13, 7.4), sharex=True, sharey=True, facecolor=FONDO)
    t = np.arange(int((VENTANA[1] - VENTANA[0]) / DT)) * DT + VENTANA[0]
    lim = 1.15 * max(max(np.max(np.abs(v)) for v in d["ventana"].values()) for d in datos.values())
    for ax, j in zip(axs.flat, JUNTAS):
        ax.set_facecolor(FONDO)
        ax.grid(True, color=REJILLA, linewidth=0.8)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for signo in (1, -1):
            ax.axhline(signo * W0, color=CRITICO, linestyle=(0, (4, 3)), linewidth=1.3)
        ax.text(VENTANA[1], W0 + 0.25, "máx. del motor ±%.2f rad/s" % W0, color=TINTA2, ha="right", va="bottom", fontsize=8.5)
        for clave, nombre, color, _ in CAMINATAS:
            ax.plot(t, datos[clave]["ventana"][j], color=color, linewidth=1.6, label=nombre)
        ax.set_title(j, loc="left", color=TINTA, fontsize=11, fontweight="bold")
        ax.set_ylim(-lim - 4.2, lim)            # abajo queda espacio para el recuadro de numeros
        lineas = ["%s: p99 %.1f · %.1f %% sobre el máx." % (datos[c]["nombre"], datos[c]["resumen"][j]["p99_abs"],
                                                           datos[c]["resumen"][j]["pct_sobre_w0"]) for c, *_ in CAMINATAS]
        ax.text(0.01, 0.03, "\n".join(lineas), transform=ax.transAxes, fontsize=8, color=TINTA2, va="bottom",
                bbox=dict(facecolor=FONDO, edgecolor=REJILLA, boxstyle="round,pad=0.3"))
    for ax in axs[1]:
        ax.set_xlabel("tiempo desde el inicio del registro [s]")
    for ax in axs[:, 0]:
        ax.set_ylabel("velocidad articular [rad/s]")
    h, l = axs[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper right", ncol=3, frameon=False, fontsize=10, bbox_to_anchor=(0.985, 0.985))
    fig.suptitle("Perfiles de velocidad de rodillas y tobillos (2 s de marcha estable)", x=0.01, ha="left",
                 fontsize=14, fontweight="bold", color=TINTA)
    fig.text(0.01, 0.925, "μ 0.8, semilla 1000, con visión; RL a vx_cmd 0.45. Línea roja: velocidad máxima del motor real "
             "(sin carga); por encima, el motor no puede seguir la orden. p99 en rad/s, de toda la corrida.",
             fontsize=9, color=TINTA2)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(salida, dpi=130, facecolor=FONDO)


def main():
    out = ROOT / "results" / "esfuerzo_motores"
    out.mkdir(parents=True, exist_ok=True)
    datos = registrar()
    (out / "perfiles_velocidad.json").write_text(json.dumps({"w0_rad_s": W0, "dt_s": DT, "ventana_s": VENTANA,
                                                             "caminatas": datos}), encoding="utf-8")
    dibujar(datos, out / "perfiles_velocidad.png")
    for c, *_ in CAMINATAS:
        print(datos[c]["nombre"], {j: datos[c]["resumen"][j] for j in JUNTAS})
    print("ok", out / "perfiles_velocidad.png")


if __name__ == "__main__":
    main()
