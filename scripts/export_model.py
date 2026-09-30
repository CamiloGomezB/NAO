"""Copia el modelo elegido de runs/ a checkpoints/ (lo que se sube al repositorio).

Genera checkpoints/best_model.zip, best_model_vecnormalize.pkl y best_model_config.yaml, con los
nombres que src/evaluate.py detecta automaticamente.

Uso (desde la raiz del repo):
    uv run python scripts/export_model.py --run ppo_base_5M
"""

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", required=True, help="carpeta dentro de runs/")
    parser.add_argument("--which", choices=("best", "final"), default="best")
    args = parser.parse_args()

    run_dir = ROOT / "runs" / args.run
    files = {
        run_dir / f"{args.which}_model.zip": "best_model.zip",
        run_dir / f"{args.which}_vecnormalize.pkl": "best_model_vecnormalize.pkl",
        run_dir / "config.yaml": "best_model_config.yaml",
        run_dir / "metadata.yaml": "best_model_metadata.yaml",
    }
    missing = [str(src) for src in files if not src.exists()]
    if missing:
        print(f"ERROR: faltan archivos: {missing}")
        return 1
    out = ROOT / "checkpoints"
    out.mkdir(exist_ok=True)
    for src, name in files.items():
        shutil.copy2(src, out / name)
        print(f"  {src.relative_to(ROOT).as_posix()} -> checkpoints/{name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
