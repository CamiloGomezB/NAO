"""Valida NaoWalkEnv con los chequeos oficiales de Gymnasium y Stable-Baselines3.

Uso (desde la raiz del repo):
    uv run python scripts/check_env.py
"""

import re
import sys
import time
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import gymnasium as gym  # noqa: E402
import numpy as np  # noqa: E402
from gymnasium.utils.env_checker import check_env as gym_check_env  # noqa: E402
from stable_baselines3.common.env_checker import check_env as sb3_check_env  # noqa: E402

import src.envs  # noqa: E402, F401  (registra NaoWalk-v0)

ANSI_COLOR = re.compile(r"\x1b\[[0-9;]*m")


def main() -> int:
    env = gym.make("NaoWalk-v0")
    base = env.unwrapped
    print(f"Entorno: NaoWalk-v0 | dt de control = {base.dt * 1000:.0f} ms ({1 / base.dt:.0f} Hz)")
    print(f"  observacion: {env.observation_space}")
    print(f"  accion:      {env.action_space}")
    print(f"  max pasos:   {env.spec.max_episode_steps} ({env.spec.max_episode_steps * base.dt:.0f} s)")

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        gym_check_env(gym.make("NaoWalk-v0").unwrapped)
        sb3_check_env(gym.make("NaoWalk-v0").unwrapped, warn=True)
    print(f"\ncheck_env Gymnasium + SB3: OK ({len(caught)} avisos)")
    for w in caught:
        print(f"  aviso: {ANSI_COLOR.sub('', str(w.message))}")
    if caught:
        print("  (limites infinitos en la observacion: normal, igual que en los entornos MuJoCo de Gymnasium)")

    # Reproducibilidad: misma semilla -> misma observacion inicial
    o1, _ = env.reset(seed=123)
    o2, _ = env.reset(seed=123)
    o3, _ = env.reset(seed=7)
    assert np.array_equal(o1, o2) and not np.array_equal(o1, o3), "reset(seed) no es reproducible"
    print("Semillas: reset(seed) reproducible")

    # Recorrido con acciones aleatorias hasta el limite de tiempo
    env.reset(seed=0)
    env.action_space.seed(0)
    t0, steps, truncated = time.perf_counter(), 0, False
    while not truncated:
        obs, reward, terminated, truncated, _ = env.step(env.action_space.sample())
        steps += 1
        assert np.all(np.isfinite(obs)), "observacion con NaN/inf"
        if terminated:
            break
    elapsed = time.perf_counter() - t0
    print(f"Recorrido aleatorio: {steps} pasos en {elapsed:.2f} s ({steps / elapsed:.0f} pasos/s, "
          f"{steps * base.dt / elapsed:.0f}x tiempo real), truncado={truncated}")
    print("\nRESULTADO: OK, el esqueleto de NaoWalkEnv cumple la API de Gymnasium.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
