"""Abre el NAO en el visor 3D de MuJoCo.

Modos:
    suspended  El torso queda fijo en el aire (los servos mantienen la pose "home").
    free       El robot se suelta sobre el suelo con los servos en "home".

Uso:
    uv run python scripts/view_model.py --mode suspended
    uv run python scripts/view_model.py --mode free
"""

import argparse
import time
from pathlib import Path

import mujoco
import mujoco.viewer

SCENE_PATH = Path(__file__).resolve().parents[1] / "assets" / "nao" / "scene.xml"
SUSPEND_HEIGHT = 0.30  # metros extra sobre la pose home


def load_model(mode: str) -> tuple[mujoco.MjModel, mujoco.MjData]:
    """Compila la escena y deja el robot en la pose "home"."""
    spec = mujoco.MjSpec.from_file(str(SCENE_PATH))
    if mode == "suspended":
        # Soldar el torso al mundo en su pose inicial: las extremidades cuelgan con su peso real.
        key = spec.key("home")
        qpos = list(key.qpos)
        qpos[2] += SUSPEND_HEIGHT
        key.qpos = qpos
        spec.body("torso").pos = qpos[:3]
        # data = [ancla(3), pose relativa(7), torquescale]; pose relativa en cero = usar la pose inicial.
        spec.add_equality(name="suspension", type=mujoco.mjtEq.mjEQ_WELD,
                          objtype=mujoco.mjtObj.mjOBJ_BODY, name1="torso",
                          data=[0.0] * 10 + [1.0])
    model = spec.compile()
    data = mujoco.MjData(model)
    mujoco.mj_resetDataKeyframe(model, data, model.key("home").id)
    mujoco.mj_forward(model, data)
    return model, data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mode", choices=("suspended", "free"), default="suspended")
    args = parser.parse_args()

    model, data = load_model(args.mode)

    print(f"Modo: {args.mode}. Cierra la ventana para terminar.")
    print("Tip: Tab oculta/muestra el panel izquierdo; en 'Rendering' puedes activar 'Joint' para ver los ejes.")

    with mujoco.viewer.launch_passive(model, data) as viewer:
        viewer.cam.lookat[:] = [0, 0, 0.3 + (SUSPEND_HEIGHT if args.mode == "suspended" else 0)]
        viewer.cam.distance = 1.2
        viewer.cam.azimuth = 150
        viewer.cam.elevation = -15
        while viewer.is_running():
            step_start = time.perf_counter()
            mujoco.mj_step(model, data)
            viewer.sync()
            remaining = model.opt.timestep - (time.perf_counter() - step_start)
            if remaining > 0:
                time.sleep(remaining)


if __name__ == "__main__":
    main()
