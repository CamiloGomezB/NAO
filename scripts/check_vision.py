"""Verifica la vision de carril en la pista simulada: coloca al NAO en posiciones conocidas del carril,
renderiza su camara inferior y compara lo que estima la vision (d, psi) con la posicion real.

No usa la politica de RL (no necesita PyTorch). Sirve para dos cosas:
  - comprobar que la escena de la pista, la camara y la vision funcionan juntas (paso 40);
  - comprobar que la vision sigue funcionando cuando cambian los colores de la pista (pasos 48 y 75).

Uso (desde la raiz del repo):
    uv run python scripts/check_vision.py                    # colores actuales de la pista
    uv run python scripts/check_vision.py --pose-noise 1.0   # con error de pose de la camara [grados]
    uv run python scripts/check_vision.py --out results/camara/verificacion_vision.md
Termina con RESULTADO: OK si todas las estimaciones son validas y el error esta dentro de las tolerancias.
"""

import argparse
import math
import sys
from pathlib import Path

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "demo"))

import build_scene  # noqa: E402
import src.envs.nao_walk_env as E  # noqa: E402
from carril import CameraModel, LaneEstimator  # noqa: E402

CAM_W, CAM_H = 320, 240
HFOV, VFOV = 54.7, 42.5        # camara inferior del modelo B-Human (igual que demo/run_demo.py)
D_VALUES = (-0.15, -0.08, 0.0, 0.08, 0.15)       # desplazamiento lateral [m] (+ izquierda)
PSI_VALUES = (-10.0, -5.0, 0.0, 5.0, 10.0)       # rumbo [grados] (+ izquierda)
X_VALUES = (0.5, 2.5)                             # posicion a lo largo del carril [m]
TOL_D_CM, TOL_PSI_DEG = 3.0, 3.0                  # tolerancia del error medio absoluto


def camera_T(env, cam_id, rng, pose_noise_deg):
    """Pose camara -> marco del robot (convencion NAOqi). Misma funcion que demo/run_demo.py."""
    p = env.data.cam_xpos[cam_id]
    Rm = env.data.cam_xmat[cam_id].reshape(3, 3)
    Rn = np.column_stack((-Rm[:, 2], -Rm[:, 0], Rm[:, 1]))
    pl, pr = env.data.site("left_foot").xpos, env.data.site("right_foot").xpos
    origin = np.array([(pl[0] + pr[0]) / 2, (pl[1] + pr[1]) / 2, 0.0])
    m = env.data.xmat[env._torso_id].reshape(3, 3)
    yaw = math.atan2(m[1, 0], m[0, 0])
    c, s = math.cos(-yaw), math.sin(-yaw)
    Rz = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    T = np.eye(4)
    T[:3, :3] = Rz @ Rn
    T[:3, 3] = Rz @ (p - origin)
    if pose_noise_deg > 0:
        a, b = np.radians(rng.normal(0, pose_noise_deg, 2))
        ca, sa, cb, sb = math.cos(a), math.sin(a), math.cos(b), math.sin(b)
        T[:3, :3] = T[:3, :3] @ np.array([[cb, 0, sb], [0, 1, 0], [-sb, 0, cb]]) @ np.array([[1, 0, 0], [0, ca, -sa], [0, sa, ca]])
    return T, origin, yaw


def verificar(cfg: dict, pose_noise: float = 0.0, seed: int = 0,
              grid: tuple = (X_VALUES, D_VALUES, PSI_VALUES)) -> dict:
    """Genera la pista con los colores de cfg y mide la vision en las posiciones de grid = (x, d, psi)."""
    info = build_scene.build(cfg, verbose=False)
    E.SCENE_PATH = ROOT / "assets" / "nao" / "scene_carril.xml"
    env = E.NaoWalkEnv()
    env.reset(seed=seed)
    m, d = env.model, env.data
    cam_id = m.camera("CameraBottom").id
    renderer = mujoco.Renderer(m, CAM_H, CAM_W)
    est = LaneEstimator(CameraModel(CAM_W, CAM_H, HFOV, VFOV), polaridad=info["polaridad"],
                        color_ref=info["color_ref"])
    rng = np.random.RandomState(seed)
    home_q = d.qpos.copy()

    rows = []
    for x in grid[0]:
        for d0 in grid[1]:
            for psi0 in grid[2]:
                d.qpos[:] = home_q
                d.qpos[0], d.qpos[1] = x, d0
                half = math.radians(psi0) / 2
                d.qpos[3:7] = [math.cos(half), 0.0, 0.0, math.sin(half)]
                d.qvel[:] = 0.0
                mujoco.mj_forward(m, d)
                renderer.update_scene(d, camera=cam_id)
                img = renderer.render()
                T, origin, yaw = camera_T(env, cam_id, rng, pose_noise)
                e = est.process(np.ascontiguousarray(img[:, :, ::-1]), T)
                rows.append(dict(x=x, d=origin[1], psi=math.degrees(yaw), valid=e.valid, lines=e.n_lines,
                                 d_est=e.d, psi_est=math.degrees(e.psi)))
    renderer.close()
    env.close()

    valid = [r for r in rows if r["valid"]]
    err_d = np.array([100 * abs(r["d_est"] - r["d"]) for r in valid]) if valid else np.array([np.nan])
    err_psi = np.array([abs(r["psi_est"] - r["psi"]) for r in valid]) if valid else np.array([np.nan])
    res = dict(cfg=dict(cfg), info=info, pose_noise=pose_noise, grid=grid, n=len(rows),
               pct_valid=100.0 * len(valid) / len(rows),
               pct_two_lines=100.0 * sum(r["lines"] == 2 for r in rows) / len(rows),
               err_d_mean=float(err_d.mean()), err_d_max=float(err_d.max()),
               err_psi_mean=float(err_psi.mean()), err_psi_max=float(err_psi.max()))
    # Ademas del resultado en simulacion se exige un contraste minimo: la imagen renderizada no tiene ruido,
    # y una linea casi del mismo color que el piso no se veria en una pista real aunque aqui se detecte.
    res["contraste_ok"] = bool(info["contraste_efectivo"] >= build_scene.MIN_CONTRASTE_REAL)
    res["ok"] = bool(res["pct_valid"] == 100.0 and res["err_d_mean"] <= TOL_D_CM
                     and res["err_psi_mean"] <= TOL_PSI_DEG and res["contraste_ok"])
    return res


def informe(res: dict, origen: str = "scripts/check_vision.py") -> str:
    cfg, info = res["cfg"], res["info"]
    salida = cfg.get("salida") or cfg["linea"]
    lines = [
        "# Verificacion de la vision de carril en la pista simulada",
        "",
        f"Generado por `{origen}`. Pista: piso `{cfg['piso']}`, linea `{cfg['linea']}`, salida `{salida}`, "
        f"meta `{cfg['meta']}`, veta {'si' if info['veta'] else 'no'}. Vision por **{info['modo_vision']}**, "
        f"linea {info['polaridad']} que el piso. Error de pose de la camara: {res['pose_noise']:.1f} grados.",
        "",
        f"Posiciones: x = {res['grid'][0]} m, d = {res['grid'][1]} m, psi = {res['grid'][2]} grados "
        f"({res['n']} en total), robot de pie en la pose `home`.",
        "",
        "| Metrica | Valor | Tolerancia |",
        "|---|---|---|",
        f"| Contraste linea-piso (0-255) | {info['contraste_efectivo']:.0f} | >= {build_scene.MIN_CONTRASTE_REAL} |",
        f"| Mediciones validas | {res['pct_valid']:.0f} % | 100 % |",
        f"| Error medio de d | {res['err_d_mean']:.2f} cm | <= {TOL_D_CM} cm |",
        f"| Error maximo de d | {res['err_d_max']:.2f} cm | - |",
        f"| Error medio de psi | {res['err_psi_mean']:.2f} grados | <= {TOL_PSI_DEG} grados |",
        f"| Error maximo de psi | {res['err_psi_max']:.2f} grados | - |",
        f"| Con las 2 lineas detectadas | {res['pct_two_lines']:.0f} % | - |",
        "",
        f"RESULTADO: {'OK' if res['ok'] else 'FALLA'}",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pose-noise", type=float, default=0.0, help="error de pose de la camara [grados]")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=Path, default=None, help="guardar la tabla en un .md")
    build_scene.add_color_args(ap)
    a = ap.parse_args()

    res = verificar(build_scene.config_from_args(a), a.pose_noise, a.seed)
    text = informe(res)
    print(text)
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(text, encoding="utf-8")
        print(f"Guardado en {a.out}")
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
