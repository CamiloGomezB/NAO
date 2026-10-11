"""Compara la camara SIMULADA del entrenamiento con la camara RENDERIZADA + vision de carril (paso 57 del PLAN).

Pone al NAO de pie en la pista (assets/nao/scene_carril.xml) en una rejilla de posiciones y rumbos, y en cada pose
mide d y psi con VisionCamara (la camara inferior renderizada y la vision de carril/, como en la demo de 3 carriles).
Comprueba:
  1. mismo SIGNO que la convencion de la seccion 6.7 (d + = robot a la izquierda; psi + = girado a la izquierda);
  2. el error de la camara renderizada (media y sigma) cae dentro del rango que sortea la camara simulada
     (sigma_d 1-5 cm, sigma_psi 1-4 grados; ver CAMARA_DEFECTO en src/envs/nao_race_env.py);
  3. la misma frecuencia: las dos miden a 10 Hz (PERIODO_CAMARA_S de src/race/contract.py).
Termina con RESULTADO: OK o FALLA y escribe results/camara/camara_sim_vs_render.json.

Uso:
    uv run python scripts/check_camara_sim.py
"""

import os

os.environ.setdefault("SHIM_MCCOMPAT", "0x800000001")   # NVIDIA para OpenGL en laptops con dos GPU

import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import mujoco  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "demo"))

from demo.caminatas.vision_camara import VisionCamara  # noqa: E402
from src.envs.nao_race_env import CAMARA_DEFECTO, NaoRaceEnv  # noqa: E402
from src.race import contract as C  # noqa: E402

YS_CM = (-12, -6, 0, 6, 12)
YAWS_DEG = (-8, -4, 0, 4, 8)
FOTOS = 5
FALLAS = []


def revisar(ok, texto):
    print(f"   {'OK   ' if ok else 'FALLA'} {texto}")
    if not ok:
        FALLAS.append(texto)


def main() -> int:
    import build_scene
    pista = build_scene.build(verbose=False)        # colores de config/pista.yaml (regenera scene_carril.xml)
    env = NaoRaceEnv(escena=str(ROOT / "assets" / "nao" / "scene_carril.xml"), perturbaciones=False, vision=False,
                     friction=1.0)
    rng = np.random.RandomState(0)
    filas = []
    for y_cm in YS_CM:
        for yaw_deg in YAWS_DEG:
            env.reset(seed=1, options={"y0": y_cm / 100, "yaw0": math.radians(yaw_deg), "vx_cmd": 0.3})
            vis = VisionCamara(env.model, env.data, env._torso, pista, rng)
            for _ in range(FOTOS):
                for _ in range(4):                      # ~100 ms de pie entre fotos
                    env.step(np.zeros(C.N_ACCION))
                vis.medir()
                d_real, psi_real = env.d_psi_reales()
                filas.append({"y_cm": y_cm, "yaw_deg": yaw_deg, "valida": vis.valida, "d_real": d_real,
                              "psi_real": psi_real, "d_cam": vis.d_crudo if vis.valida else None,
                              "psi_cam": vis.psi_crudo if vis.valida else None})
            vis.cerrar()
    val = [f for f in filas if f["valida"]]
    ed = np.array([f["d_cam"] - f["d_real"] for f in val])
    ep = np.degrees([f["psi_cam"] - f["psi_real"] for f in val])
    print(f"{len(filas)} fotos en {len(YS_CM) * len(YAWS_DEG)} poses; validas {len(val)}")
    signo_d = all(np.sign(f["d_cam"]) == np.sign(f["d_real"]) for f in val if abs(f["d_real"]) > 0.04)
    signo_psi = all(np.sign(f["psi_cam"]) == np.sign(f["psi_real"]) for f in val if abs(f["psi_real"]) > math.radians(3))
    revisar(signo_d, "signo de d igual al real en todas las poses con |d| > 4 cm (d + = robot a la izquierda)")
    revisar(signo_psi, "signo de psi igual al real en todas las poses con |psi| > 3 grados (psi + = girado a la izquierda)")
    smin, smax = CAMARA_DEFECTO["sigma_d_m"]
    pmin, pmax = CAMARA_DEFECTO["sigma_psi_grados"]
    rms_d, rms_p = float(np.sqrt(np.mean(ed ** 2))), float(np.sqrt(np.mean(ep ** 2)))
    print(f"   error de d:   media {100 * ed.mean():+.2f} cm, sigma {100 * ed.std():.2f} cm, rms {100 * rms_d:.2f} cm, "
          f"max {100 * np.max(np.abs(ed)):.2f} cm")
    print(f"   error de psi: media {ep.mean():+.2f} grados, sigma {ep.std():.2f}, rms {rms_p:.2f}, max {np.max(np.abs(ep)):.2f}")
    revisar(rms_d <= smax, f"error rms de d {100 * rms_d:.2f} cm dentro del rango simulado (sigma hasta {100 * smax:.0f} cm)")
    revisar(rms_p <= pmax, f"error rms de psi {rms_p:.2f} grados dentro del rango simulado (sigma hasta {pmax:.0f})")
    revisar(len(val) / len(filas) >= 1 - CAMARA_DEFECTO["perdidas"][1],
            f"fotos validas {100 * len(val) / len(filas):.0f} % (la simulada pierde hasta "
            f"{100 * CAMARA_DEFECTO['perdidas'][1]:.0f} %)")
    revisar(abs(C.PERIODO_CAMARA_S - 0.1) < 1e-12 and abs(vis.periodo - 0.1) < 1e-12,
            "las dos camaras miden a 10 Hz (contract.PERIODO_CAMARA_S y VisionCamara.periodo)")
    salida = ROOT / "results" / "camara" / "camara_sim_vs_render.json"
    salida.write_text(json.dumps({"fotos": len(filas), "validas": len(val),
                                  "error_d_cm": {"media": 100 * ed.mean(), "sigma": 100 * ed.std(), "rms": 100 * rms_d},
                                  "error_psi_grados": {"media": ep.mean(), "sigma": ep.std(), "rms": rms_p},
                                  "rango_simulado": {"sigma_d_m": [smin, smax], "sigma_psi_grados": [pmin, pmax]},
                                  "detalle": filas}, indent=1), encoding="utf-8")
    print(f"Escrito {salida.relative_to(ROOT).as_posix()}")
    print(f"\nRESULTADO: {'OK' if not FALLAS else 'FALLA'}")
    return 0 if not FALLAS else 1


if __name__ == "__main__":
    sys.exit(main())
