"""Analiza un barrido de agentes: que pesos y rangos tienen los que pasan el filtro y los mejores (pasos 61-62).

Lee results/barridos/<nombre>/agente_*/resultado.json y escribe results/barridos/<nombre>/analisis.md con:
  1. resumen: cuantos pasan el filtro duro, puntajes, comparacion con la base;
  2. por cada parametro sorteado (14 pesos, friccion, vx_max, ruido de camara): media en los que pasan contra los
     descartados, media en los 20 mejores, y correlacion de Spearman con el puntaje entre los que pasan;
  3. por que se descartan (tipo de falta y en que prueba: normal o salida torcida);
  4. los 20 mejores con su configuracion (la lista para la ronda 2).

Uso:
    uv run python scripts/analizar_barrido.py --nombre ronda1
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def rangos_spearman(x, y):
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    if np.std(rx) == 0 or np.std(ry) == 0:
        return float("nan")
    return float(np.corrcoef(rx, ry)[0, 1])


def parametros(s: dict) -> dict:
    p = {f"peso:{k}": v for k, v in s["pesos"].items() if k != "choque_robot"}
    p.update({"friccion_min": s["friction_range"][0], "friccion_max": s["friction_range"][1], "vx_max": s["vx_max"],
              "sigma_d_max_cm": 100 * s["sigma_d_max_m"], "sigma_psi_max_grados": s["sigma_psi_max_grados"]})
    return p


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nombre", required=True)
    ap.add_argument("--mejores", type=int, default=20)
    a = ap.parse_args()
    carpeta = ROOT / "results" / "barridos" / a.nombre
    res = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(carpeta.glob("agente_*/resultado.json"))]
    if not res:
        print("ERROR: no hay agentes evaluados")
        return 1
    base_p = carpeta / "base_carrera_v03.json"
    base = json.loads(base_p.read_text(encoding="utf-8"))["puntaje"] if base_p.exists() else None
    pasan = sorted([r for r in res if r["puntaje"]["pasa_filtro"]], key=lambda r: r["puntaje"]["puntaje"])
    descartados = [r for r in res if not r["puntaje"]["pasa_filtro"]]
    mejores = pasan[: a.mejores]
    L = [f"# Análisis del barrido `{a.nombre}`", "",
         f"Generado por `scripts/analizar_barrido.py` con {len(res)} agentes evaluados.", "",
         "## 1. Resumen", "",
         f"- **Pasan el filtro duro** (0 caídas, 0 salidas en la batería corta): **{len(pasan)}/{len(res)}**.",
         f"- Descartados: {len(descartados)}."]
    if pasan:
        ps = [r["puntaje"]["puntaje"] for r in pasan]
        L.append(f"- Puntaje (tiempo medio + 1σ) de los que pasan: mejor {min(ps):.2f} s, mediana {np.median(ps):.2f} s, "
                 f"peor {max(ps):.2f} s.")
    if base:
        mejor_base = sum(r["puntaje"]["puntaje"] < base["puntaje"] for r in pasan)
        L.append(f"- **Base `carrera_v03`** con la misma batería: puntaje {base['puntaje']:.2f} s. "
                 f"**{mejor_base}** agentes la superan.")
    L += ["", "## 2. Parámetros: pasan contra descartados, y correlación con el puntaje", "",
          "Spearman entre los que pasan: negativo = el parámetro más alto da **mejor** puntaje (menos tiempo).", "",
          f"| Parámetro | Media, pasan ({len(pasan)}) | Media, descartados ({len(descartados)}) | "
          f"Media, {len(mejores)} mejores | Spearman con el puntaje |", "|---|---|---|---|---|"]
    claves = list(parametros(res[0]["sorteo"]).keys())
    for k in claves:
        vp = [parametros(r["sorteo"])[k] for r in pasan]
        vd = [parametros(r["sorteo"])[k] for r in descartados]
        vm = [parametros(r["sorteo"])[k] for r in mejores]
        rho = rangos_spearman(vp, [r["puntaje"]["puntaje"] for r in pasan]) if len(pasan) > 3 else float("nan")
        f = lambda v: f"{np.mean(v):.3g}" if v else "—"  # noqa: E731
        L.append(f"| {k} | {f(vp)} | {f(vd)} | {f(vm)} | {rho:+.2f} |")
    L += ["", "## 3. Por qué se descartan", ""]
    motivos = Counter()
    for r in descartados:
        for c in r["corridas"]:
            if c["resultado"] != "META":
                motivos[(c.get("tipo", "normal"), c["resultado"])] += 1
    L += ["| Prueba | Falta | Corridas |", "|---|---|---|"]
    L += [f"| {t} | {f} | {n} |" for (t, f), n in motivos.most_common()]
    L += ["", f"## 4. Los {len(mejores)} mejores (pasan a la ronda 2)", "",
          "| # | Agente | Puntaje [s] | t medio [s] | Desvío máx. [cm] | vx_max | Fricción | salida | caída | centrado | "
          "barrera | rumbo | seguim. vx | vel_giro | cambio_acc |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(mejores, 1):
        p, s, w = r["puntaje"], r["sorteo"], r["sorteo"]["pesos"]
        L.append(f"| {i} | {r['agente']} | {p['puntaje']:.2f} | {p['t_medio']:.2f} | {p['desvio_max_cm']:.1f} | "
                 f"{s['vx_max']} | {s['friction_range']} | {w['salida_carril']:.0f} | {w['caida']:.0f} | "
                 f"{w['centrado']:.2f} | {w['barrera_margen']:.1f} | {w['rumbo']:.2f} | {w['seguimiento_vx']:.2f} | "
                 f"{w['vel_giro']:.2f} | {w['cambio_accion']:.3f} |")
    (carpeta / "analisis.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (carpeta / "mejores.json").write_text(json.dumps([r["agente"] for r in mejores], indent=1), encoding="utf-8")
    print("\n".join(L[:12]))
    print(f"Escrito {(carpeta / 'analisis.md').relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
