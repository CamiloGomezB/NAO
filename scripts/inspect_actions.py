"""Inspecciona el espacio de acciones de NaoWalkEnv.

1. Rango de angulos objetivo por articulacion (accion -1 y +1) frente a los limites del NAO.
2. Accion cero: el robot se mantiene de pie.
3. Cada dimension de la accion mueve su articulacion, en la direccion correcta.
4. Linea base: que pasa con acciones aleatorias (sin politica).

Uso (desde la raiz del repo):
    uv run python scripts/inspect_actions.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

from src.envs.nao_walk_env import LEG_ACTUATORS, N_ACT, NaoWalkEnv  # noqa: E402

FALL_HEIGHT_M = 0.22
FALL_TILT_DEG = 45.0


def check(desc: str, passed: bool) -> bool:
    print(f"  [{'OK' if passed else 'FALLA'}] {desc}")
    return passed


def tilt_deg(env: NaoWalkEnv) -> float:
    return float(np.degrees(np.arccos(np.clip(env.data.xmat[env._torso_id][8], -1, 1))))


def fallen(env: NaoWalkEnv) -> bool:
    return env.data.qpos[2] < FALL_HEIGHT_M or tilt_deg(env) > FALL_TILT_DEG


def main() -> int:
    env = NaoWalkEnv()
    ok = True

    print("1. Angulo objetivo por articulacion [rad] (accion -1 / 0 / +1) y limites del NAO")
    lo_t, home_t, hi_t = (env.action_to_targets(np.full(N_ACT, a)) for a in (-1.0, 0.0, 1.0))
    within = True
    print(f"  {'articulacion':<14}{'-1':>8}{'0':>8}{'+1':>8}   limites")
    for i, name in enumerate(LEG_ACTUATORS):
        lo, hi = env.model.actuator_ctrlrange[env._act_ids[i]]
        inside = lo <= min(lo_t[i], hi_t[i]) and max(lo_t[i], hi_t[i]) <= hi
        within &= inside
        print(f"  {name:<14}{lo_t[i]:>+8.2f}{home_t[i]:>+8.2f}{hi_t[i]:>+8.2f}   [{lo:+.2f}, {hi:+.2f}]"
              f"{'' if inside else '  <- se recorta'}")
    ok &= check("todos los objetivos dentro de los limites articulares", within)

    print("\n2. Accion cero durante 5 s")
    env.reset(seed=0)
    for _ in range(250):
        env.step(np.zeros(N_ACT))
    ok &= check(f"sigue de pie: altura {env.data.qpos[2]:.3f} m, inclinacion {tilt_deg(env):.1f} grados",
                not fallen(env) and tilt_deg(env) < 10)

    print("\n3. Cada dimension de la accion, mantenida en +1 y en -1 durante 0.3 s")
    print(f"  {'articulacion':<14}{'escala':>7}{'mov. con +1':>13}{'mov. con -1':>13}")
    mapping_ok = True
    for i, name in enumerate(LEG_ACTUATORS):
        moves = []
        for sign in (1.0, -1.0):
            env.reset(seed=0)
            q0 = env.data.qpos[env._qpos_ids[i]]
            action = np.zeros(N_ACT)
            action[i] = sign
            for _ in range(15):
                env.step(action)
            moves.append(env.data.qpos[env._qpos_ids[i]] - q0)
        scale = env._action_scales[i]
        # Direccion correcta y al menos 50% del recorrido pedido (el peso del robot resiste algo).
        good = moves[0] > 0.5 * scale and moves[1] < -0.5 * scale
        mapping_ok &= good
        print(f"  {name:<14}{scale:>7.2f}{moves[0]:>+13.2f}{moves[1]:>+13.2f}{'' if good else '  <- revisar'}")
    ok &= check("cada accion mueve su articulacion en la direccion pedida", mapping_ok)

    print("\n4. Linea base: acciones aleatorias uniformes (20 episodios de hasta 10 s)")
    rng = np.random.default_rng(0)
    fall_times = []
    for ep in range(20):
        env.reset(seed=ep)
        t_fall = None
        for k in range(500):
            env.step(rng.uniform(-1, 1, N_ACT))
            if fallen(env):
                t_fall = (k + 1) * env.dt
                break
        fall_times.append(t_fall)
    falls = [t for t in fall_times if t is not None]
    print(f"  caidas: {len(falls)}/20" + (f", tiempo medio hasta caer {np.mean(falls):.2f} s" if falls else ""))
    print("  (referencia para comparar con la politica entrenada)")

    print("\nRESULTADO:", "OK, el espacio de acciones es correcto." if ok else "FALLA, revisar acciones.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
