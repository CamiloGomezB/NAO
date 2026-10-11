"""Guarda una politica de un run en policies/<nombre>/ para compartirla en el repo (paso 42 del PLAN).

Copia el modelo, su normalizacion, la config y los metadatos con nombres fijos, que detectan solos
src/evaluate.py y src/train.py --continuar, y escribe un README con su origen. runs/ no se sube al repo: lo que se quiera
conservar o compartir se guarda aqui.

Uso (desde la raiz del repo):
    uv run python scripts/guardar_politica.py --run carrera_v01 --nombre carrera_v01
    uv run python scripts/guardar_politica.py --run carrera_v01 --nombre carrera_v01 --cual final --nota "8 h, mu aleatoria"
Despues:
    uv run python -m src.evaluate --model policies/carrera_v01/model.zip --episodes 20
    uv run python -m src.train --config <config> --continuar policies/carrera_v01 --run-name carrera_v02
"""

import argparse
import datetime as dt
import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True, help="carpeta dentro de runs/")
    ap.add_argument("--nombre", required=True, help="carpeta dentro de policies/ (p. ej. carrera_v01)")
    ap.add_argument("--cual", default="best",
                    help="best (mejor de la evaluacion), final, o los pasos de un checkpoint (p. ej. 25000000)")
    ap.add_argument("--nota", default="", help="texto libre para el README (que se entreno, por que)")
    ap.add_argument("--sobrescribir", action="store_true")
    a = ap.parse_args()

    run = ROOT / "runs" / a.run
    if a.cual in ("best", "final"):
        zip_, pkl = run / f"{a.cual}_model.zip", run / f"{a.cual}_vecnormalize.pkl"
    else:                                   # checkpoint de CheckpointCallback (train.py)
        zip_ = run / "checkpoints" / f"model_{int(a.cual)}_steps.zip"
        pkl = run / "checkpoints" / f"model_vecnormalize_{int(a.cual)}_steps.pkl"
    archivos = {
        zip_: "model.zip",
        pkl: "model_vecnormalize.pkl",
        run / "config.yaml": "config.yaml",
        run / "metadata.yaml": "metadata.yaml",
    }
    faltan = [str(p.relative_to(ROOT)) for p in archivos if not p.exists()]
    if faltan:
        print(f"ERROR: faltan archivos: {faltan}")
        return 1
    destino = ROOT / "policies" / a.nombre
    if destino.exists() and not a.sobrescribir:
        print(f"ERROR: {destino.relative_to(ROOT)} ya existe (usa --sobrescribir)")
        return 1
    destino.mkdir(parents=True, exist_ok=True)
    for origen, nombre in archivos.items():
        shutil.copy2(origen, destino / nombre)
    cfg = yaml.safe_load((run / "config.yaml").read_text(encoding="utf-8"))
    meta = yaml.safe_load((run / "metadata.yaml").read_text(encoding="utf-8"))
    (destino / "README.md").write_text(
        f"# Politica `{a.nombre}`\n\n"
        f"- Guardada: {dt.datetime.now():%Y-%m-%d %H:%M} desde `{zip_.relative_to(ROOT).as_posix()}`.\n"
        f"- Entorno: `{cfg.get('env_id', 'NaoWalk-v0')}`; experimento `{cfg.get('experiment')}`; semilla {cfg.get('seed')}.\n"
        f"- Commit del codigo al entrenar: `{meta.get('git_commit')}`; comando: `{meta.get('comando')}`.\n"
        f"- Continua de: `{meta.get('continua_de')}`.\n"
        f"- Nota: {a.nota or '(sin nota)'}\n\n"
        "Evaluar: `uv run python -m src.evaluate --model policies/" + a.nombre + "/model.zip --episodes 20`\n"
        "Seguir entrenando: `uv run python -m src.train --config <config> --continuar policies/" + a.nombre + "`\n",
        encoding="utf-8")
    for f in sorted(destino.iterdir()):
        print(f"  policies/{a.nombre}/{f.name}  ({f.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
