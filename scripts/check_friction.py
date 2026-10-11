"""Prueba de la friccion pie-suelo de NaoWalkEnv (paso 47).

Verifica que:
  1. con friccion fija (friction=mu), el contacto de cada pie con el suelo usa exactamente ese mu;
  2. con friccion aleatoria, mu cae en friction_range, la diferencia entre pies no supera friction_asym y
     cada contacto usa el mu de su pie (MuJoCo combina con el MAYOR de los dos coeficientes);
  3. el sorteo es reproducible con la misma semilla y cambia entre semillas;
  4. el robot quieto con mu bajo (0.4) se mantiene de pie sin resbalar (sin ruido en la pose inicial: con
     ruido, la postura se acomoda ~4.5 mm con cualquier mu, incluso 1.2, y eso no es friccion).
Termina con RESULTADO: OK o FALLA (exit code 1).

Uso:
    uv run python scripts/check_friction.py
"""

import sys
from pathlib import Path

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.envs.nao_walk_env import FRICTION_ASYM, FRICTION_RANGE, NaoWalkEnv  # noqa: E402

N_SEEDS = 200
TOL = 1e-9


def foot_contact_mu(env: NaoWalkEnv) -> dict[int, list[float]]:
    """Friccion de deslizamiento de cada contacto pie-suelo, por pie (0 = izquierdo, 1 = derecho)."""
    mus = {0: [], 1: []}
    for c in env.data.contact[: env.data.ncon]:
        if env._floor_id in (c.geom1, c.geom2):
            for k, foot in enumerate(env._foot_ids):
                if foot in (c.geom1, c.geom2):
                    mus[k].append(float(c.friction[0]))
    return mus


def settle(env: NaoWalkEnv, seconds: float = 0.5) -> None:
    """Deja al robot de pie con accion cero para que aparezcan los contactos."""
    for _ in range(int(seconds / env.dt)):
        env.step(np.zeros(env.action_space.shape))


def main() -> int:
    ok = True

    print("1. Friccion fija")
    for mu in (0.4, 0.8, 1.2):
        env = NaoWalkEnv(friction=mu)
        _, info = env.reset(seed=0)
        settle(env)
        mus = foot_contact_mu(env)
        efectivos = mus[0] + mus[1]
        good = info["friccion"] == (mu, mu) and efectivos and all(abs(m - mu) < TOL for m in efectivos)
        ok &= bool(good)
        print(f"   mu = {mu:.1f}: contactos pie-suelo {len(efectivos)}, mu efectivo "
              f"{min(efectivos):.3f}..{max(efectivos):.3f} -> {'OK' if good else 'FALLA'}")
        env.close()

    print(f"2. Friccion aleatoria (rango {FRICTION_RANGE}, asimetria hasta {FRICTION_ASYM}), {N_SEEDS} semillas")
    env = NaoWalkEnv()
    samples = []
    for seed in range(N_SEEDS):
        _, info = env.reset(seed=seed)
        samples.append(info["friccion"])
    samples = np.array(samples)
    base = samples.mean(axis=1)
    asym = np.abs(samples[:, 0] - samples[:, 1])
    in_range = np.all((base >= FRICTION_RANGE[0] - TOL) & (base <= FRICTION_RANGE[1] + TOL))
    asym_ok = np.all(asym <= FRICTION_ASYM + TOL)
    spread_ok = base.min() < FRICTION_RANGE[0] + 0.1 and base.max() > FRICTION_RANGE[1] - 0.1
    ok &= bool(in_range and asym_ok and spread_ok)
    print(f"   mu medio por episodio: min {base.min():.3f}, media {base.mean():.3f}, max {base.max():.3f} -> "
          f"{'OK' if in_range and spread_ok else 'FALLA'}")
    print(f"   diferencia entre pies: media {asym.mean():.3f}, max {asym.max():.3f} -> {'OK' if asym_ok else 'FALLA'}")

    _, info = env.reset(seed=7)
    settle(env)
    mus = foot_contact_mu(env)
    eff_ok = (mus[0] and mus[1] and all(abs(m - info["friccion"][0]) < TOL for m in mus[0])
              and all(abs(m - info["friccion"][1]) < TOL for m in mus[1]))
    ok &= bool(eff_ok)
    print(f"   semilla 7: mu pedido izq {info['friccion'][0]:.3f} / der {info['friccion'][1]:.3f}; "
          f"efectivo izq {sorted(set(round(m, 3) for m in mus[0]))} / der {sorted(set(round(m, 3) for m in mus[1]))} "
          f"-> {'OK' if eff_ok else 'FALLA'}")

    print("3. Reproducibilidad")
    a = env.reset(seed=123)[1]["friccion"]
    b = env.reset(seed=123)[1]["friccion"]
    c = env.reset(seed=124)[1]["friccion"]
    rep_ok = a == b and a != c
    ok &= rep_ok
    print(f"   semilla 123 dos veces: {a} y {b}; semilla 124: {c} -> {'OK' if rep_ok else 'FALLA'}")
    env.close()

    print("4. De pie con mu = 0.4 (piso resbaloso), sin ruido en la pose inicial")
    env = NaoWalkEnv(friction=0.4, reset_noise=0.0)
    env.reset(seed=0)
    feet0 = np.array([env.data.site(s).xpos[:2].copy() for s in ("left_foot", "right_foot")])
    fallen = None
    for _ in range(int(3.0 / env.dt)):
        _, _, terminated, _, info = env.step(np.zeros(env.action_space.shape))
        if terminated:
            fallen = info["fall_reason"]
            break
    feet1 = np.array([env.data.site(s).xpos[:2] for s in ("left_foot", "right_foot")])
    slip_mm = 1000 * float(np.max(np.linalg.norm(feet1 - feet0, axis=1)))
    stand_ok = fallen is None and slip_mm < 2.0
    ok &= stand_ok
    print(f"   3 s de pie: caida = {fallen}, deslizamiento maximo de los pies {slip_mm:.2f} mm -> "
          f"{'OK' if stand_ok else 'FALLA'}")
    env.close()

    print(f"\nRESULTADO: {'OK' if ok else 'FALLA'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
