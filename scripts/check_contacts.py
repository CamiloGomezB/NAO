"""Prueba de contacto pie-suelo: suelta al NAO en la pose "home" y mide la calidad del apoyo.

Mide penetracion (en reposo y maxima), rebote, deslizamiento de los pies y que solo los pies
toquen el suelo. Falla (exit code 1) si algun criterio no se cumple.

Uso:
    uv run python scripts/check_contacts.py
"""

import sys

import mujoco
import numpy as np

from view_model import load_model

DURATION_S = 3.0
DROP_HEIGHTS_M = (0.0, 0.03)

# Criterios de aceptacion
MAX_REST_PENETRATION_MM = 2.0
MAX_IMPACT_PENETRATION_MM = 10.0
MAX_BOUNCE_MM = 5.0
MAX_SLIP_MM = 2.0
MIN_CONTACTS_PER_FOOT = 3


def drop_test(drop: float) -> dict:
    model, data = load_model("free")
    data.qpos[2] += drop
    mujoco.mj_forward(model, data)

    floor = model.geom("floor").id
    feet = {model.geom("left_foot").id: "L", model.geom("right_foot").id: "R"}
    foot_xy0 = {g: data.geom_xpos[g][:2].copy() for g in feet}

    heights, max_pen, rest_pen, others = [], 0.0, 0.0, set()
    n_contacts = {"L": 0, "R": 0}
    for _ in range(int(DURATION_S / model.opt.timestep)):
        mujoco.mj_step(model, data)
        heights.append(data.qpos[2])
        n_contacts = {"L": 0, "R": 0}
        rest_pen = 0.0
        for c in data.contact[: data.ncon]:
            if floor not in (c.geom1, c.geom2):
                continue
            other = c.geom2 if c.geom1 == floor else c.geom1
            if other in feet:
                n_contacts[feet[other]] += 1
                max_pen = min(max_pen, c.dist)
                rest_pen = min(rest_pen, c.dist)
            else:
                others.add(model.geom(other).name)

    heights = np.array(heights)
    i_min = int(np.argmin(heights))
    return {
        "drop_cm": drop * 100,
        "rest_pen_mm": -rest_pen * 1000,
        "max_pen_mm": -max_pen * 1000,
        "bounce_mm": (heights[i_min:].max() - heights[-1]) * 1000,
        "slip_mm": max(np.linalg.norm(data.geom_xpos[g][:2] - foot_xy0[g]) * 1000 for g in feet),
        "contacts": n_contacts,
        "others": sorted(others),
        "tilt_deg": np.degrees(2 * np.arccos(min(1.0, abs(data.qpos[3])))),
        "final_z": heights[-1],
    }


def main() -> int:
    ok = True
    for drop in DROP_HEIGHTS_M:
        r = drop_test(drop)
        checks = {
            f"penetracion en reposo {r['rest_pen_mm']:.2f} mm < {MAX_REST_PENETRATION_MM}":
                r["rest_pen_mm"] < MAX_REST_PENETRATION_MM,
            f"penetracion maxima {r['max_pen_mm']:.2f} mm < {MAX_IMPACT_PENETRATION_MM}":
                r["max_pen_mm"] < MAX_IMPACT_PENETRATION_MM,
            f"rebote {r['bounce_mm']:.2f} mm < {MAX_BOUNCE_MM}": r["bounce_mm"] < MAX_BOUNCE_MM,
            f"deslizamiento {r['slip_mm']:.3f} mm < {MAX_SLIP_MM}": r["slip_mm"] < MAX_SLIP_MM,
            f"contactos por pie {r['contacts']} >= {MIN_CONTACTS_PER_FOOT}":
                min(r["contacts"].values()) >= MIN_CONTACTS_PER_FOOT,
            f"solo los pies tocan el suelo (otros: {r['others'] or 'ninguno'})": not r["others"],
        }
        print(f"\nCaida desde +{r['drop_cm']:.0f} cm ({DURATION_S:.0f} s): "
              f"torso final z={r['final_z']:.4f} m, inclinacion {r['tilt_deg']:.1f} grados")
        for desc, passed in checks.items():
            print(f"  [{'OK' if passed else 'FALLA'}] {desc}")
            ok &= passed

    print("\nRESULTADO:", "OK, el contacto pie-suelo es correcto." if ok else "FALLA, revisar contactos.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
