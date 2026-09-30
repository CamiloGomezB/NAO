"""Graba episodios de NaoWalkEnv en video (render offscreen), sin politica entrenada.

Politicas de prueba:
    zero     accion cero: el robot se queda de pie
    random   acciones aleatorias: el robot se cae

Uso (desde la raiz del repo):
    uv run python scripts/render_episode.py --policy zero --seconds 5
    uv run python scripts/render_episode.py --policy random --episodes 3
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import gymnasium as gym  # noqa: E402
import numpy as np  # noqa: E402

import src.envs  # noqa: E402, F401  (registra NaoWalk-v0)
from src.utils.video import annotate, write_video  # noqa: E402

FREEZE_S = 0.6  # segundos que se congela la imagen al terminar un episodio


def run_human(args) -> int:
    """Muestra los episodios en tiempo real en el visor de MuJoCo."""
    env = gym.make("NaoWalk-v0", render_mode="human")
    rng = np.random.default_rng(args.seed)
    for ep in range(args.episodes):
        env.reset(seed=args.seed + ep)
        for _ in range(int(args.seconds / env.unwrapped.dt)):
            action = np.zeros(env.action_space.shape) if args.policy == "zero" else rng.uniform(-1, 1, env.action_space.shape)
            _, _, terminated, truncated, info = env.step(action)
            if terminated or truncated:
                break
        print(f"episodio {ep + 1}: {'cayo: ' + info['fall_reason'] if terminated else 'sin caer'}")
    env.close()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--policy", choices=("zero", "random"), default="random")
    parser.add_argument("--episodes", type=int, default=3)
    parser.add_argument("--seconds", type=float, default=20.0, help="duracion maxima por episodio")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--human", action="store_true", help="ver en vivo en el visor 3D (no graba video)")
    args = parser.parse_args()

    if args.human:
        return run_human(args)

    env = gym.make("NaoWalk-v0", render_mode="rgb_array")
    base = env.unwrapped
    fps = base.metadata["render_fps"]
    rng = np.random.default_rng(args.seed)
    frames = []

    for ep in range(args.episodes):
        env.reset(seed=args.seed + ep)
        x0, ret, t = base.data.qpos[0], 0.0, 0.0
        max_steps = int(args.seconds / base.dt)
        for _ in range(max_steps):
            action = np.zeros(env.action_space.shape) if args.policy == "zero" else rng.uniform(-1, 1, env.action_space.shape)
            _, reward, terminated, truncated, info = env.step(action)
            ret, t = ret + reward, t + base.dt
            status = f"CAYO ({info['fall_reason']})" if terminated else "de pie"
            lines = [
                f"politica: {args.policy} | episodio {ep + 1}/{args.episodes} | t = {t:4.1f} s | {status}",
                f"avance {base.data.qpos[0] - x0:+.2f} m | vx {base.data.qvel[0]:+.2f} m/s | "
                f"recompensa acumulada {ret:+.1f}",
            ]
            frames.append(annotate(env.render(), lines))
            if terminated or truncated:
                break
        frames.extend([frames[-1]] * int(FREEZE_S * fps))
        print(f"episodio {ep + 1}: {t:.2f} s, avance {base.data.qpos[0] - x0:+.3f} m, retorno {ret:+.1f}, "
              f"{'cayo: ' + info['fall_reason'] if terminated else 'sin caer'}")

    out = args.out or ROOT / "videos" / f"episodio_{args.policy}.mp4"
    write_video(frames, out, fps)
    env.close()
    print(f"Video: {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out} "
          f"({len(frames)} frames, {len(frames) / fps:.1f} s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
