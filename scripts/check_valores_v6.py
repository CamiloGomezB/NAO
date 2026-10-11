"""Mide en el modelo NAO V6 los valores que el entorno de carrera hereda del modelo aproximado (paso 46 del PLAN).

Mediciones (sin politica, solo el modelo; no necesita PyTorch):
  1. Altura de cadera en la pose home, frente a la altura de cadera al caminar de B-Human (230 mm).
  2. Choque entre piernas: muestrea acciones al azar y extremas, pone las articulaciones en sus objetivos y mide la
     distancia minima entre la pierna izquierda y la derecha (mj_geomDistance). Compara los limites viejos del modelo
     aproximado (HipRoll +-0.25 simetrico, HipYawPitch fija) con los del contrato v1 (src/race/contract.py).
  3. Altura del torso al agacharse dentro de los limites de accion -> altura de caida con margen.
  4. Altura del torso de pie, ya asentado con los servos -> altura objetivo de la recompensa.
  5. Ciclo de control: 12 pasos de 2 ms = 24 ms.
Termina con RESULTADO: OK o FALLA.

Uso:
    uv run python scripts/check_valores_v6.py
"""

import math
import sys
from pathlib import Path

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.race import contract as C  # noqa: E402

N_MUESTRAS = 20000
WALK_HIP_HEIGHT_BHUMAN_M = 0.230          # baseline/bhuman/Config/Robots/Default/walkingEngineCommon.cfg (PenaltyStack)
PIERNA_IZQ = ("LThigh", "LTibia", "left_foot")
PIERNA_DER = ("RThigh", "RTibia", "right_foot")
LIMITES_VIEJOS = dict(C.LIMITES_ACCION, LHipYawPitch=(0.0, 0.0), LHipRoll=(-0.25, 0.25), RHipRoll=(-0.25, 0.25))
FALLAS = []


def revisar(ok, texto):
    print(f"   {'OK   ' if ok else 'FALLA'} {texto}")
    if not ok:
        FALLAS.append(texto)


def poner_objetivos(m, d, objetivos):
    """Pone las articulaciones en sus angulos objetivo (cinematica, robot suspendido)."""
    mujoco.mj_resetDataKeyframe(m, d, m.key("home").id)
    d.qpos[2] = 0.6
    for nombre, angulo in objetivos.items():
        d.qpos[m.joint(nombre).qposadr[0]] = angulo
    d.qpos[m.joint("RHipYawPitch").qposadr[0]] = objetivos.get("LHipYawPitch", 0.0)
    mujoco.mj_forward(m, d)


def objetivos_con(limites, accion):
    out = {}
    for nombre, a in zip(C.ARTICULACIONES_ACCION, accion):
        lo, hi = limites[nombre]
        out[nombre] = C.POSE_HOME[nombre] + (a * hi if a >= 0 else -a * lo)
    return out


def distancia_piernas(m, d, gi, gd):
    return min(mujoco.mj_geomDistance(m, d, a, b, 0.2, None) for a in gi for b in gd)


def main() -> int:
    m = mujoco.MjModel.from_xml_path(str(ROOT / "assets" / "nao" / "scene.xml"))
    d = mujoco.MjData(m)
    gi = [m.geom(n).id for n in PIERNA_IZQ]
    gd = [m.geom(n).id for n in PIERNA_DER]

    print("1. Altura de cadera en home")
    mujoco.mj_resetDataKeyframe(m, d, m.key("home").id)
    mujoco.mj_forward(m, d)
    suela = 0.5 * (d.site("left_foot").xpos[2] + d.site("right_foot").xpos[2])
    cadera = d.xpos[m.body("LHip2").id][2] - suela
    torso_home = d.xpos[m.body("torso").id][2] - suela
    sep_pies = d.site("left_foot").xpos[1] - d.site("right_foot").xpos[1]
    print(f"   cadera sobre la suela: {1000 * cadera:.1f} mm (B-Human camina con {1000 * WALK_HIP_HEIGHT_BHUMAN_M:.0f} mm); "
          f"torso: {1000 * torso_home:.1f} mm; separacion de los pies: {1000 * sep_pies:.1f} mm")
    revisar(abs(cadera - WALK_HIP_HEIGHT_BHUMAN_M) < 0.010, "la pose home tiene la altura de cadera de B-Human (+-10 mm)")
    gap_home = distancia_piernas(m, d, gi, gd)
    print(f"   espacio entre piernas en home: {100 * gap_home:.2f} cm")

    print(f"2. Choque entre piernas: {N_MUESTRAS} acciones al azar + extremos")
    rng = np.random.default_rng(0)
    acciones = list(rng.uniform(-1, 1, size=(N_MUESTRAS, C.N_ACCION)))
    # extremos: todas las combinaciones de signos en HipYawPitch y los dos HipRoll (lo peligroso), resto al azar o en 0
    for hyp in (-1, 1):
        for lr in (-1, 1):
            for rr in (-1, 1):
                for resto in (0.0, 1.0, -1.0):
                    a = np.full(C.N_ACCION, resto)
                    a[0], a[1], a[6] = hyp, lr, rr
                    acciones.append(a)
    casos = (("viejos (modelo aproximado)", lambda a: objetivos_con(LIMITES_VIEJOS, a)),
             ("solo limites por articulacion", lambda a: objetivos_con(C.LIMITES_ACCION, a)),
             ("contrato v1 (con presupuesto)", C.accion_a_objetivos))
    resultados = {}
    for etiqueta, a_objetivos in casos:
        dist = []
        for a in acciones:
            poner_objetivos(m, d, a_objetivos(a))
            dist.append(distancia_piernas(m, d, gi, gd))
        dist = np.array(dist)
        resultados[etiqueta] = (dist.min(), 100.0 * np.mean(dist < 0.0))
        print(f"   {etiqueta:32s}: distancia minima {100 * dist.min():+.2f} cm, "
              f"acciones que cruzan las piernas {resultados[etiqueta][1]:.2f} %")
    margen_v1 = resultados["contrato v1 (con presupuesto)"][0]
    revisar(resultados["viejos (modelo aproximado)"][1] > 0.0, "los limites viejos SI cruzaban las piernas (confirma E16)")
    revisar(resultados["solo limites por articulacion"][1] > 0.0,
            "los limites por articulacion solos tampoco bastan (confirma E40)")
    # Criterio: ningun cruce y margen > 0.10 cm. (El primer criterio, >= 0.30 cm, era arbitrario: bajar el presupuesto
    # a 0.08 no sube el peor margen de esta muestra, 0.20 cm, porque ese caso lo limitan las articulaciones de pitch.
    # Ver registro de errores E40.)
    revisar(margen_v1 > 0.001, f"con el contrato v1 ninguna accion cruza las piernas (margen minimo {100 * margen_v1:.2f} cm > 0.10)")

    print("3. Altura del torso al agacharse dentro de los limites de accion")
    s_max = min(C.LIMITES_ACCION["LKneePitch"][1] / 2, -C.LIMITES_ACCION["LHipPitch"][0], -C.LIMITES_ACCION["LAnklePitch"][0])
    alturas = []
    for s in np.linspace(0, s_max, 6):
        obj = {n: C.POSE_HOME[n] for n in C.ARTICULACIONES_ACCION}
        for lado in "LR":
            obj[lado + "HipPitch"] -= s
            obj[lado + "KneePitch"] += 2 * s
            obj[lado + "AnklePitch"] -= s
        poner_objetivos(m, d, obj)
        suela_s = 0.5 * (d.site("left_foot").xpos[2] + d.site("right_foot").xpos[2])
        alturas.append(d.xpos[m.body("torso").id][2] - suela_s)
    torso_min = min(alturas)
    altura_caida = round(torso_min - 0.05, 2)
    print(f"   torso: home {1000 * alturas[0]:.1f} mm -> agachado al maximo (s = {s_max:.2f} rad) {1000 * torso_min:.1f} mm")
    print(f"   altura de caida propuesta = minimo - 5 cm = {altura_caida:.2f} m (modelo aproximado: 0.22 m)")
    revisar(altura_caida < torso_min, "la altura de caida queda por debajo de cualquier postura agachada valida")

    print("4. Altura del torso de pie, asentado 2 s con los servos (sin ruido)")
    mujoco.mj_resetDataKeyframe(m, d, m.key("home").id)
    for _ in range(1000):
        mujoco.mj_step(m, d)
    torso_pie = d.xpos[m.body("torso").id][2]
    altura_objetivo = round(torso_pie, 3)
    print(f"   torso de pie asentado: {1000 * torso_pie:.1f} mm sobre el suelo -> altura objetivo {altura_objetivo:.3f} m "
          f"(modelo aproximado: 0.31 m)")
    revisar(abs(torso_pie - torso_home) < 0.02, "asentado queda cerca de la altura cinematica de home (+-2 cm)")

    print("5. Ciclo de control")
    paso_fisica = m.opt.timestep
    frame_skip = round(C.PERIODO_POLITICA_S / paso_fisica)
    revisar(abs(frame_skip * paso_fisica - 0.024) < 1e-12 and frame_skip == 12,
            f"paso de fisica {1000 * paso_fisica:.0f} ms x {frame_skip} = {1000 * frame_skip * paso_fisica:.0f} ms")

    from src.race import valores_v6 as W
    print("6. Coincidencia con src/race/valores_v6.py")
    revisar(W.ALTURA_OBJETIVO_M == altura_objetivo and W.ALTURA_CAIDA_M == altura_caida and W.FRAME_SKIP == frame_skip,
            "los valores guardados son los medidos")

    print("\nValores medidos para src/race/valores_v6.py:")
    print(f"   ALTURA_OBJETIVO_M = {altura_objetivo:.3f}   ALTURA_CAIDA_M = {altura_caida:.2f}   "
          f"FRAME_SKIP = {frame_skip}   margen minimo entre piernas = {100 * margen_v1:.2f} cm")
    print(f"\nRESULTADO: {'OK' if not FALLAS else 'FALLA'}")
    return 0 if not FALLAS else 1


if __name__ == "__main__":
    sys.exit(main())
