"""Verifica la deteccion de caida (terminacion del episodio) de NaoWalkEnv.

1. De pie con accion cero: no termina; el episodio se trunca a los 20 s.
2. Agachado profundo (rodillas al maximo): no es una caida.
3. Empujones fuertes en 4 direcciones: termina, y con que motivo.
4. Acciones aleatorias: motivos de caida y estado del robot al detectarla.

Uso (desde la raiz del repo):
    uv run python scripts/inspect_termination.py
"""

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import gymnasium as gym  # noqa: E402
import numpy as np  # noqa: E402

import src.envs  # noqa: E402, F401  (registra NaoWalk-v0)
from src.envs.nao_walk_env import LEG_ACTUATORS, N_ACT  # noqa: E402

PUSH_N, PUSH_S = 60.0, 0.1
PUSHES = {"adelante": (1, 0), "atras": (-1, 0), "izquierda": (0, 1), "derecha": (0, -1)}


def check(desc: str, passed: bool) -> bool:
    print(f"  [{'OK' if passed else 'FALLA'}] {desc}")
    return passed


def crouch_action() -> np.ndarray:
    """Rodilla +1 (1.3 rad) compensada con cadera y tobillo para mantener el torso vertical."""
    targets = {"HipPitch": -0.65, "KneePitch": 1.3, "AnklePitch": -0.65}
    home = {"HipPitch": -0.4, "KneePitch": 0.8, "AnklePitch": -0.4}
    scales = {"HipPitch": 0.5, "KneePitch": 0.5, "AnklePitch": 0.4}
    action = np.zeros(N_ACT)
    for i, name in enumerate(LEG_ACTUATORS):
        joint = name[1:]
        if joint in targets:
            action[i] = (targets[joint] - home[joint]) / scales[joint]
    return action


def main() -> int:
    env = gym.make("NaoWalk-v0")
    base = env.unwrapped
    ok = True

    print("1. De pie con accion cero hasta el limite de tiempo")
    env.reset(seed=0)
    steps, terminated, truncated = 0, False, False
    while not (terminated or truncated):
        _, _, terminated, truncated, info = env.step(np.zeros(N_ACT))
        steps += 1
    ok &= check(f"{steps} pasos ({steps * base.dt:.0f} s): terminado={terminated}, truncado={truncated}",
                truncated and not terminated and steps == 1000)
    ok &= check("info incluye 'fall_reason' (None si no cayo)", "fall_reason" in info and info["fall_reason"] is None)

    print("\n2. Agachado profundo durante 5 s")
    env.reset(seed=0)
    min_h, reason = 1.0, None
    for _ in range(250):
        _, _, terminated, _, info = env.step(crouch_action())
        min_h = min(min_h, base.data.qpos[2])
        if terminated:
            reason = info["fall_reason"]
            break
    ok &= check(f"no se considera caida: altura minima {min_h:.3f} m (umbral {base.fall_height}), "
                f"inclinacion {base.torso_tilt_deg():.1f} grados", reason is None)

    print(f"\n3. Empujon de {PUSH_N:.0f} N durante {PUSH_S} s al torso")
    for name, (dx, dy) in PUSHES.items():
        env.reset(seed=0)
        reason, t = None, None
        for k in range(250):
            push = base.dt * k < PUSH_S
            base.data.xfrc_applied[base._torso_id, :3] = (dx * PUSH_N, dy * PUSH_N, 0) if push else 0
            _, _, terminated, _, info = env.step(np.zeros(N_ACT))
            if terminated:
                reason, t = info["fall_reason"], (k + 1) * base.dt
                break
        base.data.xfrc_applied[:] = 0
        ok &= check(f"{name:<10} -> termina a los {t:.2f} s por '{reason}'" if reason else f"{name:<10} -> NO termino",
                    reason is not None)

    print("\n4. Acciones aleatorias (50 episodios)")
    rng = np.random.default_rng(0)
    reasons, lengths, heights, tilts = Counter(), [], [], []
    for ep in range(50):
        env.reset(seed=ep)
        for k in range(1000):
            _, _, terminated, truncated, info = env.step(rng.uniform(-1, 1, N_ACT))
            if terminated or truncated:
                break
        lengths.append((k + 1) * base.dt)
        if terminated:
            reasons[info["fall_reason"]] += 1
            heights.append(base.data.qpos[2])
            tilts.append(base.torso_tilt_deg())
    print(f"  duracion media del episodio: {np.mean(lengths):.2f} s")
    print(f"  motivos: {dict(reasons.most_common())}")
    if heights:
        print(f"  al detectar la caida: altura media {np.mean(heights):.3f} m, inclinacion media {np.mean(tilts):.0f} grados")
    ok &= check("sin inestabilidad numerica", "inestabilidad_numerica" not in reasons)

    print("\nRESULTADO:", "OK, la deteccion de caida es correcta." if ok else "FALLA, revisar terminacion.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
