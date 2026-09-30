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


N_ACT = len(LEG_ACTUATORS)

# Desviacion maxima respecto a "home" [rad] para accion = +-1, por tipo de articulacion.
# Pitch (cadera, rodilla, tobillo) necesita amplitud para dar pasos; roll solo traslada el peso.
# Todos los objetivos resultantes quedan dentro de los limites articulares del NAO.
ACTION_SCALES = {
    "HipRoll": 0.25,
    "HipPitch": 0.5,
    "KneePitch": 0.5,
    "AnklePitch": 0.4,
    "AnkleRoll": 0.25,
}

# Componentes de la observacion, en orden, con su dimension. Las escalas dejan cada valor ~O(1).
OBS_LAYOUT = (
    ("gravedad_proyectada", 3),   # vector "abajo" en el marco del torso (inclinacion)
    ("vel_angular_torso", 3),     # giroscopio [rad/s] * 0.25
    ("vel_lineal_torso", 3),      # velocidad en el marco del torso [m/s] * 2
    ("q_articular", N_ACT),       # angulo - angulo en home [rad]
    ("dq_articular", N_ACT),      # velocidad articular [rad/s] * 0.05
    ("accion_anterior", N_ACT),   # ultima accion en [-1, 1]
    ("contacto_pies", 2),         # izquierdo, derecho (0/1)
    ("fase_marcha", 2),           # sin, cos del reloj de marcha
)
ANG_VEL_SCALE = 0.25
LIN_VEL_SCALE = 2.0
JOINT_VEL_SCALE = 0.05


def obs_slices() -> dict[str, slice]:
    """Posicion de cada componente dentro del vector de observacion."""
    slices, start = {}, 0
    for name, dim in OBS_LAYOUT:
        slices[name] = slice(start, start + dim)
        start += dim
    return slices


class NaoWalkEnv(gym.Env):
    metadata = {"render_modes": [], "render_fps": 50}

    def __init__(
        self,
        frame_skip: int = 10,
        action_scale: float = 1.0,
        reset_noise: float = 0.02,
        gait_period: float = 0.6,
        fall_height: float = 0.22,
        fall_tilt_deg: float = 40.0,
        render_mode: str | None = None,
    ):
        self.model = mujoco.MjModel.from_xml_path(str(SCENE_PATH))
        self.data = mujoco.MjData(self.model)
        self.frame_skip = frame_skip
        self.dt = self.model.opt.timestep * frame_skip
        self.action_scale = action_scale
        self.reset_noise = reset_noise
        self.gait_period = gait_period
        self.fall_height = fall_height
        self.fall_tilt_deg = fall_tilt_deg
        self.render_mode = render_mode

        home = self.model.key("home").id
        self._home_qpos = self.model.key_qpos[home].copy()
        self._home_ctrl = self.model.key_ctrl[home].copy()
        self._act_ids = np.array([self.model.actuator(name).id for name in LEG_ACTUATORS])
        # "LHipPitch" -> "HipPitch"; action_scale multiplica todas las escalas (para experimentos).
        self._action_scales = action_scale * np.array([ACTION_SCALES[name[1:]] for name in LEG_ACTUATORS])
        joint_ids = self.model.actuator_trnid[self._act_ids, 0]
        self._qpos_ids = self.model.jnt_qposadr[joint_ids]
        self._qvel_ids = self.model.jnt_dofadr[joint_ids]
        self._torso_id = self.model.body("torso").id
        self._floor_id = self.model.geom("floor").id
        self._foot_ids = (self.model.geom("left_foot").id, self.model.geom("right_foot").id)

        self._prev_action = np.zeros(N_ACT)
        self._step_count = 0

        self.action_space = spaces.Box(-1.0, 1.0, shape=(N_ACT,), dtype=np.float32)
        self._reset_to_home()
        obs_dim = self._get_obs().shape[0]
        assert obs_dim == sum(dim for _, dim in OBS_LAYOUT)
        self.observation_space = spaces.Box(-np.inf, np.inf, shape=(obs_dim,), dtype=np.float32)

    # ------------------------------------------------------------------ API Gymnasium

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        self._reset_to_home()
        n_joints = self.model.nq - 7
        self.data.qpos[7:] += self.np_random.uniform(-self.reset_noise, self.reset_noise, n_joints)
        mujoco.mj_forward(self.model, self.data)
        self._prev_action[:] = 0.0
        self._step_count = 0
        return self._get_obs(), {}

    def step(self, action):
        action = np.clip(np.asarray(action, dtype=np.float64), -1.0, 1.0)
        self._apply_action(action)
        mujoco.mj_step(self.model, self.data, nstep=self.frame_skip)
        self._prev_action[:] = action
        self._step_count += 1
        fall_reason = self.fall_reason()
        terminated = fall_reason is not None
        obs = self._get_obs()
        if fall_reason == "inestabilidad_numerica":
            obs = np.nan_to_num(obs, nan=0.0, posinf=0.0, neginf=0.0)
        reward = self._compute_reward(terminated)
        info = {"fall_reason": fall_reason}
        return obs, reward, terminated, False, info

    # ------------------------------------------------------------------ Partes del MDP

    def _get_obs(self) -> np.ndarray:
        torso_rot = self.data.xmat[self._torso_id].reshape(3, 3)  # marco torso -> mundo
        return np.concatenate([
            torso_rot.T @ np.array([0.0, 0.0, -1.0]),
            self.data.sensor("gyro").data * ANG_VEL_SCALE,
            self.data.sensor("local_linvel").data * LIN_VEL_SCALE,
            self.data.qpos[self._qpos_ids] - self._home_qpos[self._qpos_ids],
            self.data.qvel[self._qvel_ids] * JOINT_VEL_SCALE,
            self._prev_action,
            self.foot_contacts(),
            self.gait_phase_features(),
        ]).astype(np.float32)

    def foot_contacts(self) -> np.ndarray:
        """1.0 si el pie (izquierdo, derecho) toca el suelo."""
        contact = np.zeros(2)
        for c in self.data.contact[: self.data.ncon]:
            if self._floor_id in (c.geom1, c.geom2):
                for k, foot in enumerate(self._foot_ids):
                    if foot in (c.geom1, c.geom2):
                        contact[k] = 1.0
        return contact

    def gait_phase(self) -> float:
        """Fase del reloj de marcha en [0, 1)."""
        return (self._step_count * self.dt / self.gait_period) % 1.0

    def gait_phase_features(self) -> np.ndarray:
        angle = 2 * np.pi * self.gait_phase()
        return np.array([np.sin(angle), np.cos(angle)])

    def action_to_targets(self, action: np.ndarray) -> np.ndarray:
        """Angulos objetivo [rad] de las articulaciones controladas para una accion en [-1, 1]."""
        return self._home_ctrl[self._act_ids] + self._action_scales * action

    def _apply_action(self, action: np.ndarray) -> None:
        # Cabeza, brazos y HipYawPitch se quedan en "home"; MuJoCo limita ctrl a ctrlrange.
        self.data.ctrl[:] = self._home_ctrl
        self.data.ctrl[self._act_ids] = self.action_to_targets(action)

    def _compute_reward(self, fallen: bool) -> float:
        return 0.0  # Provisional (Paso 15).

    def torso_tilt_deg(self) -> float:
        """Angulo entre el eje vertical del torso y la vertical del mundo."""
        cos_tilt = self.data.xmat[self._torso_id][8]  # componente z del eje z del torso
        return float(np.degrees(np.arccos(np.clip(cos_tilt, -1.0, 1.0))))

    def fall_reason(self) -> str | None:
        """Motivo de la caida, o None si el robot sigue en pie."""
        bad_qacc = self.data.warning[mujoco.mjtWarning.mjWARN_BADQACC].number > 0
        if bad_qacc or not (np.all(np.isfinite(self.data.qpos)) and np.all(np.isfinite(self.data.qvel))):
            return "inestabilidad_numerica"
        if self.data.qpos[2] < self.fall_height:
            return "altura"
        if self.torso_tilt_deg() > self.fall_tilt_deg:
            return "inclinacion"
        for c in self.data.contact[: self.data.ncon]:
            if self._floor_id in (c.geom1, c.geom2):
                other = c.geom2 if c.geom1 == self._floor_id else c.geom1
                if other not in self._foot_ids:
                    return "contacto_" + self.model.geom(other).name
        return None

    # ------------------------------------------------------------------ Utilidades

    def _reset_to_home(self) -> None:
        mujoco.mj_resetDataKeyframe(self.model, self.data, self.model.key("home").id)
        mujoco.mj_forward(self.model, self.data)
