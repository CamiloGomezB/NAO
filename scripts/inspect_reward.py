"""Verifica la funcion de recompensa de NaoWalkEnv.

1. Desglose por termino con el robot de pie.
2. Estados preparados: la recompensa debe ordenar los comportamientos (avanzar > quieto > desviarse...).
3. Termino de patron de marcha con todos los casos de contacto.
4. Retorno de episodio: quieto de pie vs acciones aleatorias.

Uso (desde la raiz del repo):
    uv run python scripts/inspect_reward.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import gymnasium as gym  # noqa: E402
import mujoco  # noqa: E402
import numpy as np  # noqa: E402

import src.envs  # noqa: E402, F401  (registra NaoWalk-v0)
from src.envs.nao_walk_env import N_ACT, NaoWalkEnv, gait_pattern_reward  # noqa: E402


def check(desc: str, passed: bool) -> bool:
    print(f"  [{'OK' if passed else 'FALLA'}] {desc}")
    return passed


def standing_env() -> NaoWalkEnv:
    """Entorno con el robot asentado de pie (1 s con accion cero)."""
    env = NaoWalkEnv(reset_noise=0.0)
    env.reset(seed=0)
    for _ in range(50):
        env.step(np.zeros(N_ACT))
    return env


def reward_with(qvel_root=None, tilt_deg: float = 0.0, action=None, fallen: bool = False) -> dict:
    """Terminos de recompensa del robot de pie con la raiz modificada a mano."""
    env = standing_env()
    d = env.data
    if qvel_root is not None:
        d.qvel[:6] = qvel_root
    if tilt_deg:
        half = np.radians(tilt_deg) / 2
        d.qpos[3:7] = [np.cos(half), 0, np.sin(half), 0]
    mujoco.mj_forward(env.model, d)
    return env.reward_terms(np.zeros(N_ACT) if action is None else action, fallen)


def main() -> int:
    ok = True

    print("1. Desglose con el robot quieto de pie (por paso)")
    terms = reward_with()
    for name, value in terms.items():
        print(f"  {name:<17}{value:>+8.4f}")
    stand = sum(terms.values())
    print(f"  {'TOTAL':<17}{stand:>+8.4f}")

    print("\n2. Estados preparados (recompensa por paso)")
    cases = {
        "avanza a 0.15 m/s (objetivo)": reward_with(qvel_root=[0.15, 0, 0, 0, 0, 0]),
        "avanza a 0.08 m/s": reward_with(qvel_root=[0.08, 0, 0, 0, 0, 0]),
        "quieto de pie": terms,
        "avanza 0.15 pero se desvia 0.15 m/s de lado": reward_with(qvel_root=[0.15, 0.15, 0, 0, 0, 0]),
        "avanza 0.15 pero gira 1 rad/s": reward_with(qvel_root=[0.15, 0, 0, 0, 0, 1.0]),
        "avanza 0.15 inclinado 25 grados": reward_with(qvel_root=[0.15, 0, 0, 0, 0, 0], tilt_deg=25),
        "corre a 0.5 m/s (demasiado rapido)": reward_with(qvel_root=[0.5, 0, 0, 0, 0, 0]),
        "cae": reward_with(fallen=True),
    }
    totals = {name: sum(t.values()) for name, t in cases.items()}
    for name, total in totals.items():
        print(f"  {name:<46}{total:>+8.3f}")
    t = totals
    ok &= check("avanzar al objetivo > avanzar lento > quieto",
                t["avanza a 0.15 m/s (objetivo)"] > t["avanza a 0.08 m/s"] > t["quieto de pie"])
    ok &= check("desviarse, girar o inclinarse reduce la recompensa de avanzar",
                all(t[k] < t["avanza a 0.15 m/s (objetivo)"] for k in
                    ("avanza 0.15 pero se desvia 0.15 m/s de lado", "avanza 0.15 pero gira 1 rad/s",
                     "avanza 0.15 inclinado 25 grados")))
    ok &= check("ir demasiado rapido no paga mas que el objetivo",
                t["corre a 0.5 m/s (demasiado rapido)"] < t["avanza a 0.15 m/s (objetivo)"])
    ok &= check("caer es lo peor", t["cae"] == min(t.values()) and t["cae"] < 0)

    jerky = reward_with(action=np.ones(N_ACT))["cambio_accion"]  # de a=0 a a=1 en un paso
    ok &= check(f"cambio brusco de accion (0 -> 1 en todas) penaliza: {jerky:+.3f}", jerky < 0)

    print("\n3. Patron de marcha (contactos izq/der vs fase)")
    rows = [((1, 0), 0.25, 1.0), ((0, 1), 0.75, 1.0), ((1, 1), 0.25, 0.5), ((0, 0), 0.25, 0.5),
            ((0, 1), 0.25, 0.0), ((1, 0), 0.75, 0.0)]
    gait_ok = True
    for contacts, phase, expected in rows:
        value = gait_pattern_reward(np.array(contacts, dtype=float), phase)
        gait_ok &= value == expected
        print(f"  contactos {contacts}, fase {phase:.2f} -> {value:.1f} (esperado {expected})")
    ok &= check("patron de marcha correcto en todos los casos", gait_ok)

    print("\n4. Retorno por episodio (suma de recompensas)")
    env = gym.make("NaoWalk-v0")
    env.reset(seed=0)
    ret_stand, steps_stand, done = 0.0, 0, False
    while not done:
        _, r, term, trunc, _ = env.step(np.zeros(N_ACT))
        ret_stand, steps_stand, done = ret_stand + r, steps_stand + 1, term or trunc
    rng = np.random.default_rng(0)
    rets = []
    for ep in range(20):
        env.reset(seed=ep)
        ret, done = 0.0, False
        while not done:
            _, r, term, trunc, _ = env.step(rng.uniform(-1, 1, N_ACT))
            ret, done = ret + r, term or trunc
        rets.append(ret)
    print(f"  quieto de pie ({steps_stand} pasos): {ret_stand:+.1f}")
    print(f"  acciones aleatorias (media de 20):   {np.mean(rets):+.1f}")
    print(f"  caminar al objetivo, estimado ideal:  ~{t['avanza a 0.15 m/s (objetivo)'] * 1000 + 250:+.0f}"
          " (1000 pasos con patron de marcha correcto)")
    ok &= check("quedarse de pie paga mas que moverse al azar", ret_stand > np.mean(rets))

    print("\nRESULTADO:", "OK, la recompensa ordena bien los comportamientos." if ok else "FALLA, revisar recompensa.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
