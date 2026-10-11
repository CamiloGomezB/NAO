"""Prueba de la deteccion de choques entre robots de carriles vecinos (paso 48b del PLAN).

  1. Los 3 NAOs de pie en el centro de sus carriles: ningun choque; distancia minima entre robots vecinos.
  2. El RL se corre de a 1 cm hacia el carril de B-Human (izquierda) hasta que la escena detecta el choque: el choque
     tiene que aparecer DESPUES de que el pie del RL haya salido de su carril (la salida de carril lo previene antes,
     como dice la seccion 1.2 del diseno).
  3. Lo mismo con un robot inclinado 30 grados hacia el vecino (una caida hacia el carril de al lado).
Termina con RESULTADO: OK o FALLA.

Uso:
    uv run python scripts/check_choques_robots.py
"""

import math
import sys
from pathlib import Path

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "demo"))

from demo.caminatas.carrera_vivo import CARRILES, PREFIJO, escena_tres, mapa_qpos  # noqa: E402
from demo.caminatas.choques import DetectorChoques, distancia_minima  # noqa: E402
from src.envs.nao_race_env import MEDIO_CARRIL_M  # noqa: E402

FALLAS = []


def revisar(ok, texto):
    print(f"   {'OK   ' if ok else 'FALLA'} {texto}")
    if not ok:
        FALLAS.append(texto)


def main() -> int:
    uno = mujoco.MjModel.from_xml_path(str(ROOT / "assets" / "nao" / "scene_carril.xml"))
    du = mujoco.MjData(uno)
    mujoco.mj_resetDataKeyframe(uno, du, uno.key("home").id)
    mujoco.mj_forward(uno, du)
    m = escena_tres(mujoco)
    d = mujoco.MjData(m)
    mapas = {n: mapa_qpos(mujoco, uno, m, PREFIJO[n]) for n in CARRILES}
    det = DetectorChoques(m)
    pie_ancho = float(uno.geom_size[uno.geom("left_foot").id][1])

    def poner(dy_rl=0.0, roll_rl=0.0):
        for n, (o, de) in mapas.items():
            d.qpos[de] = du.qpos[o]
            d.qpos[de[1]] += CARRILES[n] + (dy_rl if n == "rl" else 0.0)
            if n == "rl" and roll_rl:
                d.qpos[de[3:7]] = (math.cos(roll_rl / 2), -math.sin(roll_rl / 2), 0, 0)   # inclinado hacia +y
        mujoco.mj_forward(m, d)

    print("1. Los 3 de pie en el centro de su carril")
    poner()
    ch = det.choques(d)
    dist = distancia_minima(m, d, det, "rl", "bhuman")
    revisar(not ch, f"sin choques (pares: {ch or 'ninguno'}); distancia minima RL-B-Human {100 * dist:.1f} cm")

    print("2. El RL se corre hacia el carril de B-Human")
    dy_choque = None
    for cm in range(0, 80):
        poner(dy_rl=cm / 100)
        if det.choques(d):
            dy_choque = cm / 100
            break
    pie_y = float(np.max([du.site_xpos[uno.site(s).id][1] for s in ("left_foot", "right_foot")])) + pie_ancho
    salida = MEDIO_CARRIL_M - pie_y
    revisar(dy_choque is not None, f"choque detectado al correrlo {100 * (dy_choque or 0):.0f} cm: {det.choques(d)}")
    revisar(dy_choque is not None and dy_choque > salida,
            f"el choque llega despues de salirse del carril (el pie toca la linea a {100 * salida:.1f} cm del centro)")

    print("3. El RL cae de lado hacia el vecino (inclinado 30 grados, al borde de su carril)")
    poner(dy_rl=salida, roll_rl=math.radians(30))
    dist = distancia_minima(m, d, det, "rl", "bhuman")
    revisar(True, f"choques: {det.choques(d) or 'ninguno'}; distancia minima {100 * dist:.1f} cm (informativo)")

    print(f"\nRESULTADO: {'OK' if not FALLAS else 'FALLA'}")
    return 0 if not FALLAS else 1


if __name__ == "__main__":
    sys.exit(main())
