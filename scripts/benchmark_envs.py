"""Benchmark de velocidad: simulacion en paralelo y entrenamiento PPO con distintos numeros de entornos.

Uso (desde la raiz del repo):
    uv run python scripts/benchmark_envs.py
    uv run python scripts/benchmark_envs.py --envs 8 12 --ppo-envs 12
"""

import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
import psutil  # noqa: E402
import torch  # noqa: E402
from stable_baselines3 import PPO  # noqa: E402

from src.utils.env_factory import make_vec_env  # noqa: E402

SIM_SECONDS = 6.0
PPO_ROLLOUTS = 3
PPO_N_STEPS = 256  # pasos por entorno en cada rollout (provisional; se fija en el Paso 18)
TORCH_THREADS = 4  # mas hilos compiten con los procesos de simulacion (medido: 4 > 8)


def children_memory_mb() -> float:
    proc = psutil.Process(os.getpid())
    procs = [proc, *proc.children(recursive=True)]
    return sum(p.memory_info().rss for p in procs if p.is_running()) / 2**20


def bench_sim(n_envs: int) -> tuple[float, float]:
    """Pasos de entorno por segundo (total) con acciones aleatorias, y memoria usada."""
    venv = make_vec_env(n_envs, seed=0, subprocess=n_envs > 1)
    venv.reset()
    rng = np.random.default_rng(0)
    actions = lambda: rng.uniform(-1, 1, (n_envs, venv.action_space.shape[0]))  # noqa: E731
    for _ in range(50):  # calentamiento
        venv.step(actions())
    steps, t0 = 0, time.perf_counter()
    while time.perf_counter() - t0 < SIM_SECONDS:
        venv.step(actions())
        steps += n_envs
    rate = steps / (time.perf_counter() - t0)
    mem = children_memory_mb()
    venv.close()
    return rate, mem


def bench_ppo(n_envs: int) -> float:
    """Pasos de entrenamiento PPO por segundo (simulacion + actualizacion de la red)."""
    venv = make_vec_env(n_envs, seed=0)
    model = PPO("MlpPolicy", venv, n_steps=PPO_N_STEPS, batch_size=1024, n_epochs=5,
                policy_kwargs={"net_arch": [256, 256]}, device="cpu", verbose=0, seed=0)
    model.learn(total_timesteps=2 * n_envs * PPO_N_STEPS)  # calentamiento (2 rollouts)
    t0 = time.perf_counter()
    model.learn(total_timesteps=PPO_ROLLOUTS * n_envs * PPO_N_STEPS, reset_num_timesteps=False)
    rate = PPO_ROLLOUTS * n_envs * PPO_N_STEPS / (time.perf_counter() - t0)
    venv.close()
    return rate


def fmt_time(steps: float, rate: float) -> str:
    minutes = steps / rate / 60
    return f"{minutes:.0f} min" if minutes < 90 else f"{minutes / 60:.1f} h"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--envs", type=int, nargs="+", default=[1, 4, 8, 12, 16])
    parser.add_argument("--ppo-envs", type=int, nargs="+", default=[8, 12, 16])
    parser.add_argument("--torch-threads", type=int, default=TORCH_THREADS)
    parser.add_argument("--skip-sim", action="store_true", help="solo medir el entrenamiento PPO")
    args = parser.parse_args()
    torch.set_num_threads(args.torch_threads)
    if args.skip_sim:
        args.envs = []

    print(f"CPU: {psutil.cpu_count(logical=False)} nucleos / {psutil.cpu_count()} hilos | "
          f"RAM {psutil.virtual_memory().total / 2**30:.1f} GB | torch hilos: {torch.get_num_threads()}")

    print(f"\n1. Simulacion pura (acciones aleatorias, {SIM_SECONDS:.0f} s por configuracion)")
    print(f"  {'entornos':>8}{'pasos/s':>10}{'aceleracion':>13}{'memoria':>10}")
    base = None
    for n in args.envs:
        rate, mem = bench_sim(n)
        base = base or rate
        print(f"  {n:>8}{rate:>10.0f}{rate / base:>12.1f}x{mem:>8.0f} MB", flush=True)

    print(f"\n2. Entrenamiento PPO (red 256x256, {PPO_N_STEPS} pasos/entorno por rollout)")
    print(f"  {'entornos':>8}{'pasos/s':>10}{'10M pasos':>12}{'30M pasos':>12}")
    best = (0, 0.0)
    for n in args.ppo_envs:
        rate = bench_ppo(n)
        best = max(best, (n, rate), key=lambda x: x[1])
        print(f"  {n:>8}{rate:>10.0f}{fmt_time(10e6, rate):>12}{fmt_time(30e6, rate):>12}", flush=True)

    print(f"\nRECOMENDACION: {best[0]} entornos ({best[1]:.0f} pasos/s de entrenamiento)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
