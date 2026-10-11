from gymnasium.envs.registration import register

from src.envs.nao_race_env import NaoRaceEnv
from src.envs.nao_walk_env import NaoWalkEnv

MAX_EPISODE_STEPS = 1000  # 20 s a 50 Hz
MAX_PASOS_CARRERA = 1250  # 30 s a 24 ms (sin contar los 0.5 s de pie dentro de reset)

register(
    id="NaoWalk-v0",
    entry_point="src.envs.nao_walk_env:NaoWalkEnv",
    max_episode_steps=MAX_EPISODE_STEPS,
)

register(
    id="NaoRace-v0",
    entry_point="src.envs.nao_race_env:NaoRaceEnv",
    max_episode_steps=MAX_PASOS_CARRERA,
)

__all__ = ["NaoWalkEnv", "NaoRaceEnv", "MAX_EPISODE_STEPS", "MAX_PASOS_CARRERA"]
