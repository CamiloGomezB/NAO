"""Convierte un video .mp4 en un GIF liviano para el README (recorte, menos cuadros, menor tamano).

Uso (desde la raiz del repo):
    uv run python scripts/make_gif.py --video media/demo.mp4 --out media/demo.gif
"""

import argparse
import sys
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--video", type=Path, default=Path("media/demo.mp4"))
    parser.add_argument("--out", type=Path, default=Path("media/demo.gif"))
    parser.add_argument("--seconds", type=float, default=8.0, help="duracion del GIF desde el inicio")
    parser.add_argument("--every", type=int, default=4, help="usar 1 de cada N cuadros")
    parser.add_argument("--width", type=int, default=400)
    args = parser.parse_args()

    reader = imageio.get_reader(args.video)
    fps = reader.get_meta_data()["fps"]
    n_frames = int(args.seconds * fps)
    frames = []
    for i, frame in enumerate(reader):
        if i >= n_frames:
            break
        if i % args.every == 0:
            img = Image.fromarray(frame)
            height = round(img.height * args.width / img.width)
            frames.append(np.asarray(img.resize((args.width, height), Image.LANCZOS)))
    reader.close()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    imageio.mimsave(args.out, frames, duration=1000 * args.every / fps, loop=0)
    size_mb = args.out.stat().st_size / 2**20
    print(f"GIF: {args.out.as_posix()} ({len(frames)} cuadros, {args.seconds:.0f} s, {size_mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
