"""Entorno Gymnasium para aprender a caminar con el NAO en MuJoCo.

La politica controla las articulaciones de las piernas a 50 Hz enviando desviaciones respecto a
la pose "home" (de pie, rodillas flexionadas); los servos PD del modelo las siguen a 500 Hz.
"""

from pathlib import Path

import gymnasium as gym
import mujoco
import numpy as np
from gymnasium import spaces

SCENE_PATH = Path(__file__).resolve().parents[2] / "assets" / "nao" / "scene.xml"

# Actuadores que controla la politica. HipYawPitch queda fija en 0 (desestabiliza el torso y no
# aporta a caminar recto); cabeza y brazos se mantienen en "home".
LEG_ACTUATORS = (
    "LHipRoll", "LHipPitch", "LKneePitch", "LAnklePitch", "LAnkleRoll",
    "RHipRoll", "RHipPitch", "RKneePitch", "RAnklePitch", "RAnkleRoll",
)


class NaoWalkEnv(gym.Env):
    metadata = {"render_modes": [], "render_fps": 50}

    def __init__(
        self,
        frame_skip: int = 10,
        action_scale: float = 0.25,
        reset_noise: float = 0.02,
        render_mode: str | None = None,
    ):
        self.model = mujoco.MjModel.from_xml_path(str(SCENE_PATH))
        self.data = mujoco.MjData(self.model)
        self.frame_skip = frame_skip
        self.dt = self.model.opt.timestep * frame_skip
        self.action_scale = action_scale
        self.reset_noise = reset_noise
        self.render_mode = render_mode

        home = self.model.key("home").id
        self._home_qpos = self.model.key_qpos[home].copy()
        self._home_ctrl = self.model.key_ctrl[home].copy()
        self._act_ids = np.array([self.model.actuator(name).id for name in LEG_ACTUATORS])
        joint_ids = self.model.actuator_trnid[self._act_ids, 0]
        self._qpos_ids = self.model.jnt_qposadr[joint_ids]
        self._qvel_ids = self.model.jnt_dofadr[joint_ids]

        self.action_space = spaces.Box(-1.0, 1.0, shape=(len(LEG_ACTUATORS),), dtype=np.float32)
        self._reset_to_home()
        obs_dim = self._get_obs().shape[0]
        self.observation_space = spaces.Box(-np.inf, np.inf, shape=(obs_dim,), dtype=np.float32)

    # ------------------------------------------------------------------ API Gymnasium

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        self._reset_to_home()
        n_joints = self.model.nq - 7
        self.data.qpos[7:] += self.np_random.uniform(-self.reset_noise, self.reset_noise, n_joints)
        mujoco.mj_forward(self.model, self.data)
        return self._get_obs(), {}

    def step(self, action):
        action = np.clip(np.asarray(action, dtype=np.float64), -1.0, 1.0)
        self._apply_action(action)
        mujoco.mj_step(self.model, self.data, nstep=self.frame_skip)
        obs = self._get_obs()
        reward = self._compute_reward()
        terminated = self._is_terminated()
        return obs, reward, terminated, False, {}

    # ------------------------------------------------------------------ Partes del MDP

    def _get_obs(self) -> np.ndarray:
        # Provisional (Paso 12 agrega orientacion, velocidades del torso, contactos y fase).
        q = self.data.qpos[self._qpos_ids] - self._home_qpos[self._qpos_ids]
        dq = self.data.qvel[self._qvel_ids]
        return np.concatenate([q, dq]).astype(np.float32)

    def _apply_action(self, action: np.ndarray) -> None:
        # Provisional (Paso 13 ajusta escalas por articulacion). MuJoCo limita ctrl a ctrlrange.
        self.data.ctrl[:] = self._home_ctrl
        self.data.ctrl[self._act_ids] += self.action_scale * action

    def _compute_reward(self) -> float:
        return 0.0  # Provisional (Paso 15).

    def _is_terminated(self) -> bool:
        return False  # Provisional (Paso 14: caida).

    # ------------------------------------------------------------------ Utilidades

    def _reset_to_home(self) -> None:
        mujoco.mj_resetDataKeyframe(self.model, self.data, self.model.key("home").id)
        mujoco.mj_forward(self.model, self.data)
