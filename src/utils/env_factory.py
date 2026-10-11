"""Creacion de entornos vectorizados (varios NAO en paralelo) para Stable-Baselines3."""

from typing import Callable

import gymnasium as gym
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv, VecEnv

ENV_ID = "NaoWalk-v0"


def make_env(rank: int, seed: int, env_kwargs: dict | None = None, env_id: str = ENV_ID) -> Callable[[], gym.Env]:
    """Devuelve una funcion que crea un entorno con semilla propia (seed + rank)."""

    def _init() -> gym.Env:
        import src.envs  # noqa: F401  (registra NaoWalk-v0 tambien en los subprocesos)

        env = gym.make(env_id, **(env_kwargs or {}))
        env = Monitor(env)  # registra retorno y duracion de cada episodio
        env.reset(seed=seed + rank)
        env.action_space.seed(seed + rank)
        return env

    return _init


def make_vec_env(n_envs: int, seed: int, env_kwargs: dict | None = None, subprocess: bool = True,
                 env_id: str = ENV_ID) -> VecEnv:
    """n_envs entornos; con subprocess=True cada uno corre en su propio proceso (usa varios nucleos)."""
    fns = [make_env(i, seed, env_kwargs, env_id) for i in range(n_envs)]
    if subprocess and n_envs > 1:
        return SubprocVecEnv(fns, start_method="spawn")
    return DummyVecEnv(fns)
