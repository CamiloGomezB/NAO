"""Barrido corto de la fase M2 (pasos 62f y 62g del PLAN): ajuste fino de rl_v1.1 con el castigo al esfuerzo de los
motores, para sacar rl_v1.2 con todas las articulaciones <= 80 % del par continuo del motor real.

Cada agente:
  1. toma la config de policies/rl_v1.1 (sus pesos, friccion, camara y PPO) y le agrega solo:
     - el castigo esfuerzo_motor con SU peso y SU modo ("media": sum_j max(0, r_j - u) / u con r_j de una media
       movil de 1 s; "instante": sum_j max(0, x_j - u^2) con x_j = (par/continuo)^2 de los ultimos 24 ms);
     - umbral_esfuerzo u = 0.75 (margen sobre el limite del 80 %);
  2. sigue entrenando desde policies/rl_v1.1 (`src.train --continuar`) en runs/esfuerzo_<nombre>_NNN;
  3. evalua CADA checkpoint con la bateria completa de la ronda 2 (44 corridas, vision y perturbaciones, vx_cmd 0.45)
     y elige el mejor con el filtro duro de barrido.puntaje: caida, salida o una articulacion > 80 % = falta;
  4. guarda results/barridos/<nombre>/agente_NNN/{config.yaml, entrenamiento.log, resultado.json} y la tabla.
Es REANUDABLE. Antes evalua la base (rl_v1.1) con la misma bateria, como referencia.

Uso:
    uv run python scripts/barrido_esfuerzo.py --nombre esfuerzo_prueba --agentes 1.0 --pasos 1000000 --checkpoints 1
    uv run python scripts/barrido_esfuerzo.py --nombre esfuerzo_v12 --agentes 0.5:instante 1.0:media 0.3:instante 0.8:instante \
        --pasos 4000000 --checkpoints 4
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import barrido  # noqa: E402
from ronda_siguiente import evaluar_completa  # noqa: E402

PY = sys.executable
BASE = ROOT / "policies" / "rl_v1.1"
UMBRAL = 0.75


def resumen_esfuerzo(filas: list) -> dict:
    """Peor corrida y media por articulacion del par RMS / par continuo (en %)."""
    juntas = list(filas[0]["esfuerzo"])
    media = {j: round(100 * float(np.mean([f["esfuerzo"][j] for f in filas])), 1) for j in juntas}
    maximo = {j: round(100 * max(f["esfuerzo"][j] for f in filas), 1) for j in juntas}
    return {"media_pct": media, "max_pct": maximo, "peor_pct": max(maximo.values()),
            "peor_articulacion": max(maximo, key=maximo.get),
            "corridas_sobre_80": sum(f["esfuerzo_max"] > barrido.LIMITE_ESFUERZO for f in filas)}


def evaluar_benchmark(modelo: Path, vx: float) -> dict:
    """Bateria del benchmark de 3 carriles (con vision, SIN perturbaciones, mu 0.4-1.2 x 5 semillas, colocacion del
    benchmark). Fase M3 (E59): en CADA corrida, meta, todas las articulaciones <= 80 % y desvio maximo <= 10 cm."""
    import eval_carrera
    model, vn, env_kwargs, _ = eval_carrera.cargar(modelo)
    fs = []
    for mu in (0.4, 0.6, 0.8, 1.0, 1.2):
        for s in range(1000, 1005):
            f = eval_carrera.correr(model, vn, env_kwargs, mu, s, True, vx, False)
            f.pop("traza", None)
            fs.append(f)
    malas = [f for f in fs if f["resultado"] != "META" or f["esfuerzo_max"] > barrido.LIMITE_ESFUERZO
             or f["desvio_max"] > barrido.LIMITE_DESVIO_M]
    return {"pasa": not malas, "malas": len(malas), "desvio_max_cm": 100 * max(f["desvio_max"] for f in fs),
            "desvio_medio_cm": 100 * float(np.mean([f["desvio_max"] for f in fs])),
            "esfuerzo_max_pct": 100 * max(f["esfuerzo_max"] for f in fs), "t_medio": t_medio(fs), "corridas": fs}


def escribir_tabla(carpeta: Path) -> None:
    res = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(carpeta.glob("agente_*/resultado.json"))]
    res.sort(key=lambda r: (not r["puntaje"]["pasa_filtro"], r["puntaje"]["faltas"], r["puntaje"]["puntaje"] or 1e9))
    L = [f"# Barrido de esfuerzo `{carpeta.name}` (fase M2)", "",
         "Ajuste fino de `rl_v1.1` con el castigo `esfuerzo_motor`. Bateria completa (44 corridas). Filtro duro: caida, "
         "salida o una articulacion con par RMS > 80 % del par continuo = falta; desde la fase M3, ademas, desvio "
         "maximo medio de las salidas normales <= 10 cm y, en la bateria del benchmark (sin perturbaciones), cada "
         "corrida con meta, <= 80 % y desvio <= 10 cm. Puntaje = tiempo medio + 1 sigma.", ""]
    for base in sorted(carpeta.glob("base_*.json")):
        b = json.loads(base.read_text(encoding="utf-8"))
        L += [f"**Base `{base.stem[5:]}`:** faltas {b['puntaje']['faltas']}/44 (con el filtro del 80 %), esfuerzo maximo "
              f"{b['esfuerzo']['peor_pct']:.0f} % ({b['esfuerzo']['peor_articulacion']}), tiempo medio "
              f"{b['t_medio']:.2f} s.", ""]
    L += ["| # | Agente | Peso (modo) | Checkpoint | Pasa | Faltas | Sobre 80 % | Puntaje [s] | t medio [s] | Peor esfuerzo |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for k, r in enumerate(res, 1):
        p, e = r["puntaje"], r["esfuerzo"]
        L.append(f"| {k} | {r['agente']} | {r['peso_esfuerzo']} ({r.get('modo_esfuerzo', 'media')}) | {r['pasos_elegidos'] / 1e6:g}M | "
                 f"{'si' if p['pasa_filtro'] else 'no'} | {p['faltas']} | {e['corridas_sobre_80']} | "
                 f"{p['puntaje']:.2f} | {p['t_medio']:.2f} | " if p["pasa_filtro"] else
                 f"| {k} | {r['agente']} | {r['peso_esfuerzo']} ({r.get('modo_esfuerzo', 'media')}) | {r['pasos_elegidos'] / 1e6:g}M | no | "
                 f"{p['faltas']} | {e['corridas_sobre_80']} | — | {r['t_medio']:.2f} | ")
        L[-1] += f"{e['peor_pct']:.0f} % ({e['peor_articulacion']}) |"
    L += ["", "Checkpoints de cada agente (faltas, corridas sobre 80 %, peor esfuerzo, desvio medio de las salidas "
          "normales, tiempo medio; y si se corrio, la bateria del benchmark):", ""]
    for r in res:
        def celda(c):
            s = (f"{c['pasos'] / 1e6:g}M: {c['puntaje']['faltas']} faltas, {c['sobre_80']} sobre 80 %, "
                 f"{c['peor_pct']:.0f} %, ")
            if "desvio_medio_normal_cm" in c["puntaje"]:
                s += f"desvio {c['puntaje']['desvio_medio_normal_cm']:.1f} cm, "
            s += f"{c['t_medio']:.2f} s"
            if c.get("benchmark"):
                b = c["benchmark"]
                s += (f" [benchmark: {'pasa' if b['pasa'] else 'no'}, {b['malas']} malas, desvio max "
                      f"{b['desvio_max_cm']:.1f} cm, {b['esfuerzo_max_pct']:.0f} %, {b['t_medio']:.2f} s]")
            return s
        extra = ", ".join(f"{k} {v}" for k, v in r.get("pesos_extra", {}).items())
        L.append(f"- `{r['agente']}` (esfuerzo {r['peso_esfuerzo']}{', ' + extra if extra else ''}): "
                 + "; ".join(celda(c) for c in r["checkpoints"]))
    (carpeta / "tabla.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def t_medio(filas):
    ts = [f["t"] for f in filas if f["resultado"] == "META"]
    return float(np.mean(ts)) if ts else float("nan")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nombre", required=True)
    ap.add_argument("--agentes", nargs="+", required=True,
                    help="uno por agente: magnitud[:modo[:termino=peso,...]] del castigo, p. ej. 1.0:media "
                         "0.5:instante:centrado=-5; el peso de esfuerzo es -magnitud (sin signo: argparse toma "
                         "'-0.3:instante' por una opcion, E57); los demas terminos llevan su signo")
    ap.add_argument("--pasos", type=int, default=3_000_000)
    ap.add_argument("--checkpoints", type=int, default=3, help="cuantos checkpoints evaluar por agente")
    ap.add_argument("--n-envs", type=int, default=16)
    ap.add_argument("--eval-vx", type=float, default=0.45)
    ap.add_argument("--base", type=Path, default=BASE,
                    help="politica de partida: carpeta de policies/ (default rl_v1.1) o checkpoint .zip de un run "
                         "(paso 62g2: seguir al mejor agente; su config sale de runs/<run>/config.yaml)")
    a = ap.parse_args()
    base = a.base if a.base.is_absolute() else ROOT / a.base
    es_zip = base.suffix == ".zip"
    modelo_base = base if es_zip else base / "model.zip"
    cfg_path = base.parents[1] / "config.yaml" if es_zip else base / "config.yaml"
    nombre_base = "rl_v1.1" if base == BASE else "continua"

    carpeta = ROOT / "results" / "barridos" / a.nombre
    carpeta.mkdir(parents=True, exist_ok=True)
    barrido.no_suspender()
    (carpeta / "barrido.yaml").write_text(yaml.safe_dump(vars(a) | {"base": base.relative_to(ROOT).as_posix(),
                                                                      "umbral_esfuerzo": UMBRAL}, sort_keys=False),
                                          encoding="utf-8")
    base_json = carpeta / f"base_{nombre_base}.json"
    if not base_json.exists():
        print(f"base {nombre_base}: bateria completa", flush=True)
        fs = evaluar_completa(modelo_base, a.eval_vx)
        base_json.write_text(json.dumps({"puntaje": barrido.puntaje(fs), "esfuerzo": resumen_esfuerzo(fs),
                                         "t_medio": t_medio(fs), "corridas": fs}, indent=1), encoding="utf-8")
    cfg_base = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))

    for i, spec in enumerate(a.agentes):
        partes = spec.split(":")
        w, modo = -abs(float(partes[0])), (partes[1] if len(partes) > 1 and partes[1] else "media")
        extra = {}
        for kv in (partes[2].split(",") if len(partes) > 2 else []):
            k, v = kv.split("=")
            extra[k.strip()] = float(v)
        ag = f"agente_{i:03d}"
        dir_ag = carpeta / ag
        if (dir_ag / "resultado.json").exists():
            print(f"{ag}: ya evaluado, se salta")
            continue
        dir_ag.mkdir(exist_ok=True)
        cfg = json.loads(json.dumps(cfg_base))
        cfg["experiment"] = f"esfuerzo_{a.nombre}"
        cfg["seed"] = int(cfg_base["seed"]) + i + (1000 if es_zip else 0)
        cfg["total_timesteps"] = a.pasos
        cfg["n_envs"] = a.n_envs
        cfg["checkpoint_every"] = max(a.pasos // a.checkpoints, 1)
        cfg["eval"] = {"every": max(a.pasos // a.checkpoints, 1), "n_episodes": 3}
        cfg["env"]["pesos"]["esfuerzo_motor"] = float(w)
        cfg["env"]["umbral_esfuerzo"] = UMBRAL
        cfg["env"]["modo_esfuerzo"] = modo
        cfg["env"]["pesos"].update(extra)     # fase M3: p. ej. centrado mas fuerte
        (dir_ag / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")
        run = f"esfuerzo_{a.nombre}_{i:03d}"
        modelo = ROOT / "runs" / run / "final_model.zip"
        ck_dir = ROOT / "runs" / run / "checkpoints"
        t0 = time.time()
        valido = modelo.exists() and modelo.stat().st_size > 0 and any(ck_dir.glob("model_*_steps.zip"))
        if not valido:
            if (ROOT / "runs" / run).exists():
                shutil.rmtree(ROOT / "runs" / run)
            print(f"{ag}: entrenando {a.pasos:,} pasos con esfuerzo_motor = {w} ({modo}) {extra or ''}", flush=True)
            r = subprocess.run([PY, "-m", "src.train", "--config", str(dir_ag / "config.yaml"), "--run-name", run,
                                "--continuar", str(base)], cwd=ROOT, capture_output=True, text=True)
            (dir_ag / "entrenamiento.log").write_text(r.stdout + r.stderr, encoding="utf-8")
            if r.returncode != 0 or not modelo.exists():
                print(f"{ag}: ERROR al entrenar (ver {dir_ag.relative_to(ROOT)}/entrenamiento.log)")
                return 1
        cks = sorted(ck_dir.glob("model_*_steps.zip"), key=lambda f: int(f.stem.split("_")[1])) or [modelo]
        evals = []
        for ck in cks:
            fs = evaluar_completa(ck, a.eval_vx)
            p, e = barrido.puntaje(fs), resumen_esfuerzo(fs)
            pasos = int(ck.stem.split("_")[1]) if ck != modelo else a.pasos
            # Fase M3: el benchmark (sin perturbaciones) solo se corre si la bateria completa pasa (ahorra tiempo).
            bench = evaluar_benchmark(ck, a.eval_vx) if p["pasa_filtro"] else None
            evals.append((pasos, ck, fs, p, e, bench))
            print(f"   {ag} {ck.stem}: faltas={p['faltas']} sobre80={e['corridas_sobre_80']} "
                  f"peor={e['peor_pct']:.0f}% ({e['peor_articulacion']}) desvio={p['desvio_medio_normal_cm']:.1f}cm "
                  f"t={t_medio(fs):.2f} s" + ("" if bench is None else
                  f" | benchmark {'PASA' if bench['pasa'] else 'no'}: malas={bench['malas']} "
                  f"desvio max={bench['desvio_max_cm']:.1f}cm peor={bench['esfuerzo_max_pct']:.0f}% "
                  f"t={bench['t_medio']:.2f} s"), flush=True)
        # El mejor: pasa la bateria completa Y el benchmark (fase M3) y tiene menor puntaje; si ninguno pasa, el de
        # menos faltas, mas recto y con menor esfuerzo.
        ok = lambda x: x[3]["pasa_filtro"] and x[5] is not None and x[5]["pasa"]  # noqa: E731
        clave = lambda x: (not ok(x), x[3]["faltas"], x[3]["puntaje"] or 1e9,  # noqa: E731
                           x[3].get("desvio_medio_normal_cm", 0), x[4]["peor_pct"])
        pasos_el, ck_el, filas, p, e, bench_el = min(evals, key=clave)
        p = {**p, "pasa_filtro": ok((pasos_el, ck_el, filas, p, e, bench_el))}
        res = {"agente": ag, "run": run, "peso_esfuerzo": w, "modo_esfuerzo": modo, "umbral_esfuerzo": UMBRAL,
               "checkpoint_elegido": ck_el.relative_to(ROOT).as_posix(), "pasos_elegidos": pasos_el,
               "pesos_extra": extra,
               "checkpoints": [{"pasos": x[0], "puntaje": x[3], "sobre_80": x[4]["corridas_sobre_80"],
                                "peor_pct": x[4]["peor_pct"], "t_medio": t_medio(x[2]),
                                "benchmark": None if x[5] is None else {k: v for k, v in x[5].items() if k != "corridas"}}
                               for x in evals],
               "benchmark": bench_el,
               "pasos": a.pasos, "continua_de": base.relative_to(ROOT).as_posix(), "eval_vx": a.eval_vx,
               "bateria": "completa (44 corridas)", "puntaje": p, "esfuerzo": e, "t_medio": t_medio(filas),
               "corridas": filas, "seg": round(time.time() - t0, 1)}
        (dir_ag / "resultado.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
        print(f"{ag}: {'PASA' if p['pasa_filtro'] else 'descartado'} ({ck_el.stem}) faltas={p['faltas']} "
              f"peor={e['peor_pct']:.0f}% puntaje={p['puntaje']} ({res['seg']:.0f} s)", flush=True)
        escribir_tabla(carpeta)
    escribir_tabla(carpeta)
    print(f"Tabla: {(carpeta / 'tabla.md').relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
