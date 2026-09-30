"""Inspecciona las observaciones de NaoWalkEnv.

1. Muestra cada componente con el robot de pie (accion cero).
2. Verifica signos y marcos de referencia con estados preparados a mano.
3. Mide la escala de cada componente en episodios con acciones aleatorias.

Uso (desde la raiz del repo):
    uv run python scripts/inspect_obs.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import mujoco  # noqa: E402
import numpy as np  # noqa: E402

from src.envs.nao_walk_env import OBS_LAYOUT, NaoWalkEnv, obs_slices  # noqa: E402

SLICES = obs_slices()


def fmt(v: np.ndarray) -> str:
    return np.array2string(np.asarray(v), precision=3, suppress_small=True, max_line_width=200)


def check(desc: str, passed: bool) -> bool:
    print(f"  [{'OK' if passed else 'FALLA'}] {desc}")
    return passed


def prepared_obs(env: NaoWalkEnv, qpos_root=None, qvel_root=None, steps: int = 0) -> np.ndarray:
    """Observacion tras preparar la raiz del robot (y opcionalmente avanzar con accion cero)."""
    env.reset(seed=0)
    d = env.unwrapped.data
    if qpos_root is not None:
        d.qpos[: len(qpos_root)] = qpos_root
    if qvel_root is not None:
        d.qvel[: len(qvel_root)] = qvel_root
    mujoco.mj_forward(env.model, d)
    obs = env.unwrapped._get_obs()
    for _ in range(steps):
        obs, *_ = env.step(np.zeros(env.action_space.shape))
    return obs


def main() -> int:
    env = NaoWalkEnv()
    ok = True

    print(f"1. Observacion con el robot de pie (accion cero, 1 s) - dimension {env.observation_space.shape[0]}")
    obs = prepared_obs(env, steps=50)
    for name, _ in OBS_LAYOUT:
        print(f"  {name:<20} {fmt(obs[SLICES[name]])}")

    print("\n2. Verificacion de signos y marcos de referencia")
    home = env._home_qpos
    g = obs[SLICES["gravedad_proyectada"]]
    ok &= check(f"de pie: gravedad ~ (0, 0, -1) -> {fmt(g)}", g[2] < -0.99)
    ok &= check("de pie: ambos pies en contacto", np.all(obs[SLICES["contacto_pies"]] == 1))

    theta = np.radians(10)  # torso inclinado 10 grados hacia adelante (giro +y)
    quat = [np.cos(theta / 2), 0, np.sin(theta / 2), 0]
    g = prepared_obs(env, qpos_root=[0, 0, home[2] + 0.1, *quat])[SLICES["gravedad_proyectada"]]
    ok &= check(f"inclinado 10 grados adelante: gravedad x = sin(10) = +0.174 -> {g[0]:+.3f}",
                abs(g[0] - np.sin(theta)) < 1e-3)

    upright = [0, 0, home[2] + 0.1, 1, 0, 0, 0]
    lin = prepared_obs(env, qpos_root=upright, qvel_root=[0.5, 0, 0, 0, 0, 0])[SLICES["vel_lineal_torso"]] / 2.0
    ok &= check(f"avanzando a 0.5 m/s en x: vel lineal x = {lin[0]:+.3f} m/s", abs(lin[0] - 0.5) < 1e-3)
    ang = prepared_obs(env, qpos_root=upright, qvel_root=[0, 0, 0, 0, 0, 1.0])[SLICES["vel_angular_torso"]] / 0.25
    ok &= check(f"girando 1 rad/s a la izquierda: vel angular z = {ang[2]:+.3f} rad/s", abs(ang[2] - 1.0) < 1e-3)

    c = prepared_obs(env, qpos_root=[0, 0, home[2] + 0.05])[SLICES["contacto_pies"]]
    ok &= check(f"levantado 5 cm: sin contacto en los pies -> {fmt(c)}", np.all(c == 0))

    ph = prepared_obs(env, steps=15)[SLICES["fase_marcha"]]  # 15 pasos * 20 ms = 0.3 s = media fase
    ok &= check(f"fase tras 0.3 s (medio ciclo de 0.6 s): (sin, cos) ~ (0, -1) -> {fmt(ph)}",
                abs(ph[0]) < 1e-6 and abs(ph[1] + 1) < 1e-6)

    print("\n3. Escala en 5 episodios con acciones aleatorias (hasta 200 pasos)")
    rng = np.random.default_rng(0)
    samples = []
    for ep in range(5):
        env.reset(seed=ep)
        for _ in range(200):
            o, *_ = env.step(rng.uniform(-1, 1, env.action_space.shape))
            samples.append(o)
    samples = np.array(samples)
    ok &= check("sin NaN ni infinitos", bool(np.all(np.isfinite(samples))))
    print(f"  {'componente':<20}{'|max|':>8}{'media |x|':>11}")
    for name, _ in OBS_LAYOUT:
        part = np.abs(samples[:, SLICES[name]])
        print(f"  {name:<20}{part.max():>8.2f}{part.mean():>11.2f}")

    print("\nRESULTADO:", "OK, las observaciones son correctas." if ok else "FALLA, revisar observaciones.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
