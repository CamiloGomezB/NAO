"""Demo interactiva: la politica entregada camina en el visor 3D y se puede detener y reanudar.

Teclas (con la ventana del visor seleccionada):
    Espacio     parar / volver a caminar
    Enter       reiniciar el episodio

La politica fue entrenada para caminar siempre hacia adelante; no tiene una orden de "parar". Para
detenerse, este script espera a que ambos pies esten en el suelo (doble apoyo, ~60 ms en promedio) y
congela la postura en ese instante. Base amplia = postura estable. Ademas, tras (re)empezar a caminar
la parada se aplaza hasta llevar MIN_WALK_S caminando: parar y reanudar muy seguido desestabiliza la
marcha. Probado con pulsaciones rapidas: 399/400 paradas sin caida.

Uso (desde la raiz del repo):
    uv run python scripts/demo_interactive.py
    uv run python scripts/demo_interactive.py --model checkpoints/best_model.zip
"""

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import gymnasium as gym  # noqa: E402
import mujoco  # noqa: E402
import mujoco.viewer  # noqa: E402
import yaml  # noqa: E402
from stable_baselines3 import PPO  # noqa: E402
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize  # noqa: E402

import src.envs  # noqa: E402, F401  (registra NaoWalk-v0)
from src.evaluate import find_config, find_vecnormalize  # noqa: E402

KEY_SPACE, KEY_ENTER = 32, 257
MIN_WALK_S = 2.0  # caminata minima antes de poder detenerse
ENV_ID = "NaoWalk-v0"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", type=Path, default=ROOT / "checkpoints" / "best_model.zip")
    parser.add_argument("--seed", type=int, default=1000)
    args = parser.parse_args()

    config_path = find_config(args.model)
    env_kwargs = yaml.safe_load(config_path.read_text(encoding="utf-8"))["env"] if config_path else {}
    env = gym.make(ENV_ID, **env_kwargs).unwrapped  # sin limite de 20 s: la demo dura lo que se quiera
    vecnorm = VecNormalize.load(str(find_vecnormalize(args.model)),
                                DummyVecEnv([lambda: gym.make(ENV_ID, **env_kwargs)]))
    vecnorm.training = False
    model = PPO.load(args.model, device="cpu")

    state = {"walking": True, "stop_requested": False, "frozen": None, "reset": True, "walk_steps": 0}

    def on_key(keycode: int) -> None:
        if keycode == KEY_SPACE:
            if state["walking"] and not state["stop_requested"]:
                state["stop_requested"] = True
            else:
                state.update(walking=True, stop_requested=False, frozen=None, walk_steps=0)
        elif keycode == KEY_ENTER:
            state["reset"] = True

    print("Demo interactiva del NAO. Espacio: parar / caminar | Enter: reiniciar | cerrar ventana: salir")
    obs = None
    seed = args.seed
    with mujoco.viewer.launch_passive(env.model, env.data, key_callback=on_key) as viewer:
        viewer.cam.type = mujoco.mjtCamera.mjCAMERA_TRACKING
        viewer.cam.trackbodyid = env.model.body("torso").id
        viewer.cam.distance, viewer.cam.azimuth, viewer.cam.elevation = 1.3, 120, -15
        while viewer.is_running():
            t0 = time.perf_counter()
            if state["reset"]:
                obs, _ = env.reset(seed=seed)
                seed += 1
                state.update(walking=True, stop_requested=False, frozen=None, reset=False, walk_steps=0)
                x0 = env.data.qpos[0]

            if state["walking"]:
                action, _ = model.predict(vecnorm.normalize_obs(obs), deterministic=True)
                state["walk_steps"] += 1
                # Parada pedida: esperar la caminata minima y a tener ambos pies en el suelo; congelar.
                settled = state["walk_steps"] * env.dt >= MIN_WALK_S
                if state["stop_requested"] and settled and env.foot_contacts().all():
                    state["walking"], state["stop_requested"], state["frozen"] = False, False, action.copy()
            else:
                action = state["frozen"]
            obs, _, terminated, _, info = env.step(action)

            status = ("CAMINANDO" if state["walking"] and not state["stop_requested"]
                      else "DETENIENDOSE (terminando paso)..." if state["walking"] else "DETENIDO")
            if terminated:
                status = f"CAYO ({info['fall_reason']}) - Enter para reiniciar"
                state["walking"], state["frozen"] = False, action
            viewer.set_texts((None, mujoco.mjtGridPos.mjGRID_TOPLEFT,
                              "Estado\nAvance\nControles",
                              f"{status}\n{env.data.qpos[0] - x0:.2f} m\nEspacio: parar/caminar  Enter: reiniciar"))
            viewer.sync()
            time.sleep(max(0.0, env.dt - (time.perf_counter() - t0)))
    env.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
