# -*- coding: utf-8 -*-
"""Vision de carril con la CAMARA RENDERIZADA de cada robot (no simulada con ruido).

Cada robot tiene su propia fisica (su propio MjModel/MjData). Cada 100 ms (10 FPS, como la camara del NAO) se
renderiza su camara inferior, la vision de carril/ estima (d, psi) y un control proporcional da la velocidad
de giro deseada: w = -(k_psi * psi + k_d * d), la misma ley que demo/run_demo.py y el benchmark.
"""
import math

import mujoco
import numpy as np

from carril import CameraModel, LaneEstimator

CAM_W, CAM_H = 320, 240
HFOV, VFOV = 54.7, 42.5          # camara inferior del modelo B-Human (igual que demo/run_demo.py)
K_PSI, K_D, W_MAX = 1.2, 2.0, 0.5


def camera_T(m, d, cam_id, torso_id, rng=None, pose_noise_deg=0.0):
    """Pose camara -> marco del robot (convencion NAOqi: x eje optico, y izquierda, z arriba)."""
    p = d.cam_xpos[cam_id]
    Rm = d.cam_xmat[cam_id].reshape(3, 3)
    Rn = np.column_stack((-Rm[:, 2], -Rm[:, 0], Rm[:, 1]))
    pl, pr = d.site("left_foot").xpos, d.site("right_foot").xpos
    origin = np.array([(pl[0] + pr[0]) / 2, (pl[1] + pr[1]) / 2, 0.0])
    R = d.xmat[torso_id].reshape(3, 3)
    yaw = math.atan2(R[1, 0], R[0, 0])
    c, s = math.cos(-yaw), math.sin(-yaw)
    Rz = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    T = np.eye(4)
    T[:3, :3] = Rz @ Rn
    T[:3, 3] = Rz @ (p - origin)
    if rng is not None and pose_noise_deg > 0:
        a, b = np.radians(rng.normal(0, pose_noise_deg, 2))
        ca, sa, cb, sb = math.cos(a), math.sin(a), math.cos(b), math.sin(b)
        T[:3, :3] = T[:3, :3] @ np.array([[cb, 0, sb], [0, 1, 0], [-sb, 0, cb]]) @ np.array([[1, 0, 0], [0, ca, -sa], [0, sa, ca]])
    return T


class VisionCamara(object):
    """Camara inferior renderizada + vision de carril, a 10 Hz. Interfaz como VisionSimulada: giro(t)."""

    def __init__(self, m, d, torso_id, pista, rng, pose_noise_deg=1.0, periodo=0.1, alfa=0.5):
        self.m, self.d, self.torso_id = m, d, torso_id
        self.cam_id = m.camera("CameraBottom").id
        self.renderer = mujoco.Renderer(m, CAM_H, CAM_W)
        self.est = LaneEstimator(CameraModel(CAM_W, CAM_H, HFOV, VFOV), polaridad=pista.get("polaridad", "oscura"),
                                 color_ref=pista.get("color_ref"))
        self.rng, self.pose_noise, self.periodo, self.alfa = rng, pose_noise_deg, periodo, alfa
        self.t_ult = -1e9
        self.d_est = self.psi_est = None
        self.imagen = None        # ultima imagen (RGB) para mostrarla
        self.puntos = None        # pixeles de la linea detectados en la ultima imagen
        self.valida = False

    def medir(self):
        self.renderer.update_scene(self.d, camera=self.cam_id)
        img = self.renderer.render()
        T = camera_T(self.m, self.d, self.cam_id, self.torso_id, self.rng, self.pose_noise)
        e = self.est.process(np.ascontiguousarray(img[:, :, ::-1]), T)
        self.imagen = img
        self.puntos = self.est._uv.copy() if len(self.est._uv) else None
        self.valida = bool(e.valid)
        if e.valid:
            if self.d_est is None:
                self.d_est, self.psi_est = e.d, e.psi
            else:
                self.d_est += self.alfa * (e.d - self.d_est)
                self.psi_est += self.alfa * (e.psi - self.psi_est)

    def giro(self, t, *_):
        """Velocidad de giro deseada [rad/s]. Los argumentos extra (d y psi reales) se ignoran: solo camara."""
        if t - self.t_ult >= self.periodo:
            self.t_ult = t
            self.medir()
        if self.d_est is None:
            return 0.0
        return float(np.clip(-(K_PSI * self.psi_est + K_D * self.d_est), -W_MAX, W_MAX))

    def cerrar(self):
        self.renderer.close()
