"""Prueba de pie: el NAO en la pose "home" con los servos PD fijos (sin politica).

Pruebas:
  1. Nominal:      10 s sin perturbaciones.
  2. Ruido:        20 intentos con ruido aleatorio en la pose inicial (como en el reset del entorno RL).
  3. Empujones:    empujon horizontal de 0.1 s en 4 direcciones, con fuerza creciente.

Criterio de caida: altura del torso < 0.22 m o inclinacion > 45 grados.

Uso:
    uv run python scripts/check_standing.py
"""

import sys

import mujoco
import numpy as np

from view_model import load_model

FALL_HEIGHT_M = 0.22
FALL_TILT_DEG = 45.0
NOMINAL_DURATION_S = 10.0
NOISE_TRIALS = 20
NOISE_RAD = 0.05
NOISE_DURATION_S = 5.0
PUSH_DURATION_S = 0.1
PUSH_FORCES_N = (2, 4, 6, 8, 10, 15, 20)
PUSH_DIRECTIONS = {"adelante": (1, 0), "atras": (-1, 0), "izquierda": (0, 1), "derecha": (0, -1)}

# Criterios de aceptacion
MAX_NOMINAL_TILT_DEG = 5.0
MIN_NOISE_SUCCESS = 0.9


def tilt_deg(data: mujoco.MjData) -> float:
    """Angulo entre el eje vertical del torso y la vertical del mundo."""
    return float(np.degrees(np.arccos(np.clip(data.xmat[1].reshape(3, 3)[2, 2], -1.0, 1.0))))


def fallen(data: mujoco.MjData) -> bool:
    return data.qpos[2] < FALL_HEIGHT_M or tilt_deg(data) > FALL_TILT_DEG


def simulate(model, data, duration, push=None) -> tuple[bool, float, float]:
    """Devuelve (sigue_de_pie, inclinacion_max, tiempo_de_caida)."""
    torso = model.body("torso").id
    max_tilt = 0.0
    for i in range(int(duration / model.opt.timestep)):
        t = i * model.opt.timestep
        data.xfrc_applied[torso, :3] = 0.0
        if push is not None and 1.0 <= t < 1.0 + PUSH_DURATION_S:
            data.xfrc_applied[torso, :3] = push
        mujoco.mj_step(model, data)
        max_tilt = max(max_tilt, tilt_deg(data))
        if fallen(data):
            return False, max_tilt, t
    return True, max_tilt, duration


def main() -> int:
    ok = True

    # 1. Nominal
    model, data = load_model("free")
    z0 = data.qpos[2]
    standing, max_tilt, _ = simulate(model, data, NOMINAL_DURATION_S)
    passed = standing and max_tilt < MAX_NOMINAL_TILT_DEG
    ok &= passed
    print(f"1. Nominal ({NOMINAL_DURATION_S:.0f} s): {'de pie' if standing else 'CAE'}, "
          f"inclinacion max {max_tilt:.1f} grados, altura torso {z0:.4f} -> {data.qpos[2]:.4f} m "
          f"[{'OK' if passed else 'FALLA'}]")

    # 2. Ruido en la pose inicial
    rng = np.random.default_rng(0)
    successes, tilts = 0, []
    for _ in range(NOISE_TRIALS):
        model, data = load_model("free")
        data.qpos[7:] += rng.uniform(-NOISE_RAD, NOISE_RAD, model.nq - 7)
        mujoco.mj_forward(model, data)
        standing, max_tilt, _ = simulate(model, data, NOISE_DURATION_S)
        successes += standing
        tilts.append(max_tilt)
    rate = successes / NOISE_TRIALS
    passed = rate >= MIN_NOISE_SUCCESS
    ok &= passed
    print(f"2. Ruido +-{NOISE_RAD} rad ({NOISE_TRIALS} intentos, {NOISE_DURATION_S:.0f} s): "
          f"{successes}/{NOISE_TRIALS} de pie, inclinacion max media {np.mean(tilts):.1f} grados "
          f"[{'OK' if passed else 'FALLA'}]")

    # 3. Empujones (informativo: sin politica no se espera que resista empujones grandes)
    print(f"3. Empujones de {PUSH_DURATION_S} s al torso (fuerza maxima resistida):")
    for name, (dx, dy) in PUSH_DIRECTIONS.items():
        resisted = 0
        for force in PUSH_FORCES_N:
            model, data = load_model("free")
            standing, _, _ = simulate(model, data, 4.0, push=(dx * force, dy * force, 0.0))
            if not standing:
                break
            resisted = force
        print(f"   {name:<10} {resisted:>3} N  (impulso {resisted * PUSH_DURATION_S:.1f} N*s)")

    print("\nRESULTADO:", "OK, el NAO se mantiene de pie con los servos PD." if ok else "FALLA, revisar pose/ganancias.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
