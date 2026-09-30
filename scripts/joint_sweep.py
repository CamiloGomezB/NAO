"""Barrido articular: mueve cada actuador del NAO (suspendido) por su rango, uno por uno.

Para cada actuador el objetivo va de "home" al limite inferior, luego al superior y vuelve a
"home". Imprime cuanto del recorrido pedido alcanzo cada articulacion (y si la detuvo un choque
con otra parte del cuerpo) y genera un video con vista frontal y lateral, el nombre de la
articulacion, la fase del barrido y el movimiento esperado.

Uso:
    uv run python scripts/joint_sweep.py
    uv run python scripts/joint_sweep.py --no-video
"""

import argparse
import sys
from pathlib import Path

import imageio.v2 as imageio
import mujoco
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from view_model import load_model

VIDEO_PATH = Path(__file__).resolve().parents[1] / "videos" / "joint_sweep.mp4"
RANGE_FRACTION = 0.9  # fraccion del rango articular que se recorre
SEGMENT_S = (0.8, 1.2, 0.8)  # home -> min, min -> max, max -> home
FPS_STEPS = 17  # pasos de simulacion por frame (~29 fps con dt = 2 ms)
VIEW_W, VIEW_H, BANNER_H = 480, 352, 64
MIN_REACH = 0.8  # fraccion minima del recorrido pedido (salvo que la detenga un choque)
PHASES = ("-> hacia el MINIMO (-)", "-> hacia el MAXIMO (+)", "-> vuelve a home")

# Movimiento esperado en la convencion de Aldebaran (signo del angulo -> movimiento).
EXPECTED = {
    "HeadYaw": "+ gira la cabeza hacia su izquierda",
    "HeadPitch": "+ baja la cabeza (mira al suelo)",
    "LHipYawPitch": "abre/cierra AMBAS caderas en diagonal (acopladas)",
    "LHipRoll": "+ separa la pierna izquierda hacia afuera",
    "LHipPitch": "- levanta el muslo izquierdo hacia adelante",
    "LKneePitch": "+ dobla la rodilla izquierda (pie hacia atras)",
    "LAnklePitch": "+ baja la punta del pie izquierdo",
    "LAnkleRoll": "+ levanta el borde exterior del pie izquierdo",
    "RHipRoll": "- separa la pierna derecha hacia afuera",
    "RHipPitch": "- levanta el muslo derecho hacia adelante",
    "RKneePitch": "+ dobla la rodilla derecha (pie hacia atras)",
    "RAnklePitch": "+ baja la punta del pie derecho",
    "RAnkleRoll": "- levanta el borde exterior del pie derecho",
    "LShoulderPitch": "- levanta el brazo izquierdo al frente (1.57 = abajo)",
    "LShoulderRoll": "+ separa el brazo izquierdo hacia afuera",
    "LElbowYaw": "gira el antebrazo izquierdo sobre el eje del brazo",
    "LElbowRoll": "- dobla el codo izquierdo",
    "RShoulderPitch": "- levanta el brazo derecho al frente (1.57 = abajo)",
    "RShoulderRoll": "- separa el brazo derecho hacia afuera",
    "RElbowYaw": "gira el antebrazo derecho sobre el eje del brazo",
    "RElbowRoll": "+ dobla el codo derecho",
}


def smoothstep(x: float) -> float:
    return x * x * (3 - 2 * x)


def target_trajectory(c0: float, lo: float, hi: float, dt: float) -> tuple[np.ndarray, np.ndarray]:
    """Objetivos home -> lo -> hi -> home con interpolacion suave, y el indice de fase de cada paso."""
    points = [c0, lo, hi, c0]
    segs, phases = [], []
    for p, ((a, b), dur) in enumerate(zip(zip(points[:-1], points[1:]), SEGMENT_S)):
        n = int(dur / dt)
        segs.append([a + (b - a) * smoothstep(i / n) for i in range(n)])
        phases.append(np.full(n, p))
    return np.concatenate(segs), np.concatenate(phases)


def self_collisions(model: mujoco.MjModel, data: mujoco.MjData, floor: int) -> set[str]:
    """Pares de geometrias del robot en contacto entre si (excluye el suelo)."""
    pairs = set()
    for c in data.contact[: data.ncon]:
        if floor not in (c.geom1, c.geom2):
            pairs.add("-".join(sorted((model.geom(c.geom1).name, model.geom(c.geom2).name))))
    return pairs


def make_cameras() -> list[mujoco.MjvCamera]:
    cams = []
    for azimuth in (180.0, 90.0):  # frente, lado izquierdo
        cam = mujoco.MjvCamera()
        cam.lookat[:] = [0.0, 0.0, 0.52]
        cam.distance = 1.0
        cam.azimuth = azimuth
        cam.elevation = -8.0
        cams.append(cam)
    return cams


def banner(text_lines: list[str], width: int, font) -> np.ndarray:
    img = Image.new("RGB", (width, BANNER_H), (20, 24, 32))
    draw = ImageDraw.Draw(img)
    for i, line in enumerate(text_lines):
        draw.text((10, 6 + 28 * i), line, fill=(235, 235, 235), font=font)
    return np.asarray(img)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--no-video", action="store_true", help="solo imprimir la tabla, sin generar video")
    args = parser.parse_args()

    model, data = load_model("suspended")
    home_ctrl = model.key("home").ctrl.copy()
    dt = model.opt.timestep

    renderer = writer = font = None
    if not args.no_video:
        VIDEO_PATH.parent.mkdir(parents=True, exist_ok=True)
        renderer = mujoco.Renderer(model, VIEW_H, VIEW_W)
        writer = imageio.get_writer(VIDEO_PATH, fps=1 / (FPS_STEPS * dt), codec="libx264", quality=7)
        font = ImageFont.load_default(size=20)
        cams = make_cameras()

    floor = model.geom("floor").id
    print(f"{'#':>2} {'actuador':<16}{'pedido [rad]':<20}{'alcanzado [rad]':<20}{'recorrido':>9}")
    ok = True
    for i in range(model.nu):
        name = model.actuator(i).name
        jnt = model.actuator_trnid[i, 0]
        qadr = model.jnt_qposadr[jnt]
        c0 = home_ctrl[i]
        lo, hi = model.actuator_ctrlrange[i]
        lo_t, hi_t = c0 + RANGE_FRACTION * (lo - c0), c0 + RANGE_FRACTION * (hi - c0)

        mujoco.mj_resetDataKeyframe(model, data, model.key("home").id)
        mujoco.mj_forward(model, data)
        q_min = q_max = data.qpos[qadr]
        collisions = set()
        targets, phases = target_trajectory(c0, lo_t, hi_t, dt)
        for k, (target, phase) in enumerate(zip(targets, phases)):
            data.ctrl[:] = home_ctrl
            data.ctrl[i] = target
            mujoco.mj_step(model, data)
            q = data.qpos[qadr]
            q_min, q_max = min(q_min, q), max(q_max, q)
            collisions |= self_collisions(model, data, floor)
            if renderer is not None and k % FPS_STEPS == 0:
                views = []
                for cam in cams:
                    renderer.update_scene(data, cam)
                    views.append(renderer.render())
                text = [f"{i + 1}/{model.nu}  {name}  {PHASES[phase]}   objetivo {target:+.2f}  actual {q:+.2f} rad",
                        EXPECTED.get(name, "")]
                frame = np.concatenate([banner(text, 2 * VIEW_W, font), np.concatenate(views, axis=1)])
                writer.append_data(frame)

        reach = (q_max - q_min) / (hi_t - lo_t)
        passed = reach >= MIN_REACH or bool(collisions)
        ok &= passed
        blocked = f"  (choca: {', '.join(sorted(collisions))})" if collisions else ""
        print(f"{i + 1:>2} {name:<16}[{lo_t:+.2f}, {hi_t:+.2f}]    [{q_min:+.2f}, {q_max:+.2f}]    "
              f"{reach * 100:>6.0f} %  {'OK' if passed else 'FALLA'}{blocked}")

    if writer is not None:
        writer.close()
        print(f"\nVideo: {VIDEO_PATH.relative_to(Path.cwd()) if VIDEO_PATH.is_relative_to(Path.cwd()) else VIDEO_PATH}")
    print("\nRESULTADO:", "OK, todas las articulaciones recorren su rango." if ok else "FALLA, revisar articulaciones marcadas.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
