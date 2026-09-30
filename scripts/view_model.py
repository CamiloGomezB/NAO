"""Abre el NAO en el visor 3D de MuJoCo.

Modos:
    suspended  El torso queda fijo en el aire (los servos mantienen la pose "home").
    free       El robot se suelta sobre el suelo con los servos en "home".

Uso:
    uv run python scripts/view_model.py --mode suspended
    uv run python scripts/view_model.py --mode free
    uv run python scripts/view_model.py --mode free --drop 5 --slowmo 10

Teclas:
    Espacio     pausa / reanuda
    Backspace   reinicia (vuelve a soltar el robot)
"""

import argparse
import time
from pathlib import Path

import mujoco
import mujoco.viewer

SCENE_PATH = Path(__file__).resolve().parents[1] / "assets" / "nao" / "scene.xml"
SUSPEND_HEIGHT = 0.30  # metros extra sobre la pose home
FRAME_DT = 1 / 60  # segundos reales entre refrescos del visor

KEY_SPACE = 32
KEY_BACKSPACE = 259


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


def reset(model: mujoco.MjModel, data: mujoco.MjData, drop: float) -> None:
    mujoco.mj_resetDataKeyframe(model, data, model.key("home").id)
    data.qpos[2] += drop
    mujoco.mj_forward(model, data)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mode", choices=("suspended", "free"), default="suspended")
    parser.add_argument("--drop", type=float, default=0.0, help="altura extra de caida en cm (modo free)")
    parser.add_argument("--slowmo", type=float, default=1.0, help="factor de camara lenta (10 = 10x mas lento)")
    args = parser.parse_args()

    model, data = load_model(args.mode)
    drop = args.drop / 100 if args.mode == "free" else 0.0
    reset(model, data, drop)

    state = {"paused": False, "reset": False}

    def on_key(keycode: int) -> None:
        if keycode == KEY_SPACE:
            state["paused"] = not state["paused"]
            print("Pausa" if state["paused"] else "Reanuda")
        elif keycode == KEY_BACKSPACE:
            state["reset"] = True

    print(f"Modo: {args.mode} | caida: {args.drop} cm | camara lenta: {args.slowmo}x")
    print("Espacio: pausa/reanuda | Backspace: reiniciar | cerrar la ventana para terminar")

    steps_per_frame = max(1, round(FRAME_DT / args.slowmo / model.opt.timestep))
    with mujoco.viewer.launch_passive(model, data, key_callback=on_key) as viewer:
        viewer.cam.lookat[:] = [0, 0, 0.3 + (SUSPEND_HEIGHT if args.mode == "suspended" else 0)]
        viewer.cam.distance = 1.2
        viewer.cam.azimuth = 150
        viewer.cam.elevation = -15
        while viewer.is_running():
            frame_start = time.perf_counter()
            if state["reset"]:
                reset(model, data, drop)
                state["reset"] = False
            if not state["paused"]:
                for _ in range(steps_per_frame):
                    mujoco.mj_step(model, data)
            viewer.sync()
            remaining = FRAME_DT - (time.perf_counter() - frame_start)
            if remaining > 0:
                time.sleep(remaining)


if __name__ == "__main__":
    main()
