"""Carga el modelo NAO e imprime un resumen para verificarlo.

Uso:
    uv run python scripts/inspect_model.py
"""

from pathlib import Path

import mujoco
import numpy as np

SCENE_PATH = Path(__file__).resolve().parents[1] / "assets" / "nao" / "scene.xml"
EXPECTED_MASS_KG = 5.305  # NAO H25 V5 (modelo original)


def main() -> None:
    model = mujoco.MjModel.from_xml_path(str(SCENE_PATH))
    data = mujoco.MjData(model)

    print(f"Modelo: {SCENE_PATH.name} | MuJoCo {mujoco.__version__}")
    print(f"timestep={model.opt.timestep}s  nq={model.nq}  nv={model.nv}  nu={model.nu}  nbody={model.nbody}")

    print("\nArticulaciones (convencion Aldebaran):")
    print(f"  {'nombre':<16}{'eje':<24}{'rango [rad]':<22}{'actuador'}")
    actuated = {model.actuator_trnid[i, 0] for i in range(model.nu)}
    for j in range(model.njnt):
        if model.jnt_type[j] == mujoco.mjtJoint.mjJNT_FREE:
            continue
        name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, j)
        axis = np.array2string(model.jnt_axis[j], precision=3, suppress_small=True)
        lo, hi = model.jnt_range[j]
        act = "si" if j in actuated else "no (acoplado)"
        print(f"  {name:<16}{axis:<24}[{lo:+.3f}, {hi:+.3f}]    {act}")

    print("\nActuadores (servo de posicion):")
    for i in range(model.nu):
        name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_ACTUATOR, i)
        kp = model.actuator_gainprm[i, 0]
        kv = -model.actuator_biasprm[i, 2]
        fmax = model.actuator_forcerange[i, 1]
        print(f"  {name:<16}kp={kp:<5g} kv={kv:<5g} torque max={fmax:.3f} Nm")

    total_mass = mujoco.mj_getTotalmass(model)
    print(f"\nMasa total: {total_mass:.3f} kg (esperada ~{EXPECTED_MASS_KG} kg)")

    # Geometria en la pose "home"
    mujoco.mj_resetDataKeyframe(model, data, model.key("home").id)
    mujoco.mj_forward(model, data)
    soles = [data.site(s).xpos[2] for s in ("left_foot", "right_foot")]
    head = data.geom("head")
    head_top = head.xpos[2] + model.geom("head").size[0]
    print(f"Pose home: altura torso={data.body('torso').xpos[2]:.4f} m, "
          f"suela izq={soles[0]*1000:+.1f} mm, suela der={soles[1]*1000:+.1f} mm, "
          f"punta cabeza={head_top:.3f} m")
    print(f"Contactos iniciales: {data.ncon}")

    ctrl = model.key("home").ctrl
    lo, hi = model.actuator_ctrlrange.T
    assert np.all((ctrl >= lo) & (ctrl <= hi)), "ctrl de 'home' fuera de rango"
    assert abs(total_mass - EXPECTED_MASS_KG) < 0.01, "masa total inesperada"
    print("\nOK: el modelo carga y pasa las verificaciones basicas.")


if __name__ == "__main__":
    main()
