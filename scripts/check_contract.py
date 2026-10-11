"""Prueba del contrato v1 de la politica de carrera (src/race/contract.py), paso 41 del PLAN.

Comprueba que:
  1. el orden de las 26 articulaciones es identico al de PenaltyStack (third_party/penaltystack/motion_contract.py);
  2. la observacion tiene 54 valores, en el orden del diseno;
  3. la pose home coincide con el keyframe "home" del modelo V6 y los limites de accion no salen del rango articular;
  4. con un frame armado desde MuJoCo (formato SensorAdapter de PenaltyStack), cada parte de la observacion tiene
     el valor esperado (inclinacion, rumbo, angulos, carga de los pies, reloj, camara);
  5. accion -> angulos: 0 = home, +1/-1 = limites (HipRoll asimetrico), fuera de [-1, 1] se recorta;
  6. salida para PenaltyStack: 26 angulos y rigideces en orden B-Human, RHipYawPitch = LHipYawPitch;
  7. la camara cumple la seccion 6.7 del diseno (ultima medicion cruda, valido < 300 ms);
  8. el archivo no usa nada que impida correrlo en Python 2.7 (revision estatica; la prueba real es en el NAO).
Termina con RESULTADO: OK o FALLA (exit code 1).

Uso:
    uv run python scripts/check_contract.py
"""

import ast
import math
import sys
from pathlib import Path

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.race import contract as C  # noqa: E402

FALLAS = []


def revisar(ok: bool, texto: str) -> None:
    print(f"   {'OK   ' if ok else 'FALLA'} {texto}")
    if not ok:
        FALLAS.append(texto)


def frame_desde_mujoco(m, d) -> dict:
    """Frame con el formato del SensorAdapter de PenaltyStack, a partir del estado de MuJoCo."""
    angles, velocity = [], []
    for nombre in C.NOMBRES_MODELO:
        if nombre.endswith("Hand"):
            angles.append(0.0); velocity.append(0.0)
            continue
        j = m.joint(nombre)
        angles.append(float(d.qpos[j.qposadr[0]])); velocity.append(float(d.qvel[j.dofadr[0]]))
    torso = m.body("torso").id
    pies = {m.body("LFoot").id: 0, m.body("RFoot").id: 1}
    piso = m.geom("floor").id
    carga = [0.0, 0.0]
    f6 = np.zeros(6)
    for i in range(d.ncon):
        c = d.contact[i]
        if piso not in (c.geom1, c.geom2):
            continue
        otro = c.geom2 if c.geom1 == piso else c.geom1
        lado = pies.get(int(m.geom_bodyid[otro]))
        if lado is None:
            continue
        mujoco.mj_contactForce(m, d, i, f6)
        carga[lado] += abs(float((np.asarray(c.frame).reshape(3, 3).T @ f6[:3])[2])) / 9.81
    # El reparto entre los 4 sensores de cada pie no importa para el contrato (se suma por pie): 1/4 a cada uno.
    fsr = [carga[0] / 4] * 4 + [carga[1] / 4] * 4
    return {"angles": angles, "velocity": velocity, "gyro": d.sensor("gyro").data.tolist(),
            "acc": d.sensor("accelerometer").data.tolist(), "orientation": d.xquat[torso].tolist(), "fsr": fsr}


def main() -> int:
    print("1. Orden de articulaciones = PenaltyStack")
    copia = (ROOT / "third_party" / "penaltystack" / "motion_contract.py").read_text(encoding="utf-8")
    nombres_ps = None
    for nodo in ast.walk(ast.parse(copia)):
        if isinstance(nodo, ast.Assign) and any(getattr(t, "id", "") == "JOINT_NAMES" for t in nodo.targets):
            nombres_ps = ast.literal_eval(nodo.value)
    revisar(nombres_ps == C.JOINT_NAMES_BHUMAN, f"26 nombres identicos a motion_contract.py ({len(C.JOINT_NAMES_BHUMAN)})")
    revisar(abs(C.CICLO_S - 0.012) < 1e-12 and abs(C.PERIODO_POLITICA_S - 0.024) < 1e-12,
            "ciclo de 12 ms y politica cada 24 ms")

    print("2. Forma de la observacion")
    reb = C.rebanadas_observacion()
    revisar(C.DIM_OBSERVACION == 54, f"54 valores (hay {C.DIM_OBSERVACION})")
    revisar(reb["d_camara"] == (7, 8) and reb["psi_camara"] == (8, 9) and reb["valido_camara"] == (9, 10),
            "d, psi y valido de la camara en las posiciones 7, 8 y 9")
    revisar(C.N_ACCION == 13 and len(C.LIMITES_ACCION) == 13, "13 acciones con su limite")

    print("3. Pose home y limites contra el modelo V6")
    m = mujoco.MjModel.from_xml_path(str(ROOT / "assets" / "nao" / "scene.xml"))
    d = mujoco.MjData(m)
    home = m.key("home")
    dif_home = max(abs(home.ctrl[i] - C.POSE_HOME[m.actuator(i).name]) for i in range(m.nu))
    revisar(dif_home < 1e-9, f"POSE_HOME = keyframe 'home' en los {m.nu} actuadores (dif. max {dif_home:.1e})")
    for nombre in C.ARTICULACIONES_ACCION:
        lo_j, hi_j = m.jnt_range[m.joint(nombre).id]
        lo, hi = C.LIMITES_ACCION[nombre]
        revisar(lo_j <= C.POSE_HOME[nombre] + lo and C.POSE_HOME[nombre] + hi <= hi_j,
                f"{nombre:15s} home{lo:+.2f}/{hi:+.2f} dentro de [{lo_j:+.3f}, {hi_j:+.3f}]")

    print("4. Observacion desde un frame de MuJoCo (robot de pie, girado 10 grados, 0.5 s asentandose)")
    mujoco.mj_resetDataKeyframe(m, d, home.id)
    yaw = math.radians(10.0)
    d.qpos[3:7] = [math.cos(yaw / 2), 0.0, 0.0, math.sin(yaw / 2)]
    for _ in range(250):
        mujoco.mj_step(m, d)
    frame = frame_desde_mujoco(m, d)
    obs = C.armar_observacion(frame, rumbo_objetivo=0.0, camara=(0.12, -0.05, 1.0),
                              accion_anterior=[0.0] * 13, t_marcha_s=0.0, vx_cmd=0.3)
    g = obs[reb["gravedad_proyectada"][0]:reb["gravedad_proyectada"][1]]
    R = d.xmat[m.body("torso").id].reshape(3, 3)
    g_ref = R.T @ np.array([0.0, 0.0, -1.0])
    revisar(np.allclose(g, g_ref, atol=1e-9), f"gravedad proyectada = R^T (0, 0, -1) del simulador {np.round(g, 3).tolist()}")
    err = obs[reb["error_rumbo_imu"][0]]
    revisar(abs(math.degrees(err) + 10.0) < 1.0, f"error de rumbo = objetivo - rumbo = {math.degrees(err):+.2f} grados (esperado ~ -10)")
    q_rel = obs[reb["q_articular"][0]:reb["q_articular"][1]]
    revisar(max(abs(x) for x in q_rel) < 0.05, f"angulos respecto a home pequenos de pie (max {max(abs(x) for x in q_rel):.3f} rad)")
    carga = obs[reb["carga_pies"][0]:reb["carga_pies"][1]]
    revisar(abs(sum(carga) - 1.0) < 0.1 and min(carga) > 0.3,
            f"carga de los pies de pie: izq {carga[0]:.2f}, der {carga[1]:.2f}, suma {sum(carga):.2f} (esperado ~1)")
    revisar(obs[reb["reloj_marcha"][0]:reb["reloj_marcha"][1]] == [0.0, 1.0], "reloj de marcha en t = 0: (sin, cos) = (0, 1)")
    revisar(obs[7:10] == [0.12, -0.05, 1.0] and obs[-1] == 0.3, "camara y vx_cmd pasan tal cual")
    gyro = obs[reb["vel_angular_torso"][0]:reb["vel_angular_torso"][1]]
    revisar(np.allclose(gyro, np.array(frame["gyro"]) * 0.25), "giroscopio escalado * 0.25")
    for _ in range(50):     # orientaciones al azar: rumbo y gravedad contra la matriz de MuJoCo
        q = np.random.default_rng(len(FALLAS) + _).normal(size=4)
        q /= np.linalg.norm(q)
        Rq = np.zeros(9)
        mujoco.mju_quat2Mat(Rq, q)
        Rq = Rq.reshape(3, 3)
        ok_g = np.allclose(C.gravedad_proyectada(q.tolist()), Rq.T @ np.array([0.0, 0.0, -1.0]), atol=1e-9)
        ok_r = abs(C.envolver_angulo(C.rumbo_desde_cuaternion(q.tolist()) - math.atan2(Rq[1, 0], Rq[0, 0]))) < 1e-9
        if not (ok_g and ok_r):
            break
    revisar(ok_g and ok_r, "gravedad y rumbo correctos en 50 orientaciones al azar")

    print("5. Accion -> angulos objetivo")
    cero = C.accion_a_objetivos([0.0] * 13)
    revisar(all(abs(cero[n] - C.POSE_HOME[n]) < 1e-12 for n in C.ARTICULACIONES_ACCION), "accion 0 = pose home")
    def una(i, v):
        a = [0.0] * 13
        a[i] = v
        return C.accion_a_objetivos(a)
    ok_lim = all(abs(una(i, 1.0)[n] - (C.POSE_HOME[n] + C.LIMITES_ACCION[n][1])) < 1e-12 and
                 abs(una(i, -1.0)[n] - (C.POSE_HOME[n] + C.LIMITES_ACCION[n][0])) < 1e-12
                 for i, n in enumerate(C.ARTICULACIONES_ACCION))
    revisar(ok_lim, "una articulacion a la vez: +1 / -1 = home + limite superior / inferior")
    iL, iR = C.ARTICULACIONES_ACCION.index("LHipRoll"), C.ARTICULACIONES_ACCION.index("RHipRoll")
    revisar(abs(una(iL, 1.0)["LHipRoll"] - 0.25) < 1e-12 and abs(una(iL, -1.0)["LHipRoll"] + 0.07) < 1e-12 and
            abs(una(iR, 1.0)["RHipRoll"] - 0.07) < 1e-12 and abs(una(iR, -1.0)["RHipRoll"] + 0.25) < 1e-12,
            "HipRoll asimetrico: hacia afuera 0.25, hacia adentro 0.07 en las dos piernas")
    revisar(C.accion_a_objetivos([5.0] * 13) == C.accion_a_objetivos([1.0] * 13), "acciones fuera de [-1, 1] se recortan")
    # Presupuesto lateral (paso 46): las dos piernas hacia adentro a la vez se escalan; hacia afuera no se toca.
    adentro = [1.0] * 13
    adentro[iL] = -1.0                                  # LHipRoll hacia adentro
    adentro[C.ARTICULACIONES_ACCION.index("LAnkleRoll")] = -1.0
    obj = C.accion_a_objetivos(adentro)
    off = dict((n, obj[n] - C.POSE_HOME[n]) for n in C.ARTICULACIONES_ACCION)
    revisar(abs(C.cuanto_adentro(off) - C.PRESUPUESTO_ADENTRO_RAD) < 1e-9,
            f"las dos piernas hacia adentro al maximo se escalan al presupuesto ({C.cuanto_adentro(off):.3f} rad)")
    revisar(abs(obj["LHipPitch"] - (C.POSE_HOME["LHipPitch"] + 0.5)) < 1e-12,
            "el presupuesto no toca las articulaciones de pitch")
    afuera = [0.0] * 13
    afuera[iL], afuera[iR] = 1.0, -1.0                  # las dos caderas hacia afuera
    obj = C.accion_a_objetivos(afuera)
    revisar(abs(obj["LHipRoll"] - 0.25) < 1e-12 and abs(obj["RHipRoll"] + 0.25) < 1e-12,
            "hacia afuera no hay presupuesto: las dos caderas abren 0.25")

    print("6. Salida para PenaltyStack (orden B-Human)")
    angulos, rigidez = C.objetivos_a_salida_bhuman(C.accion_a_objetivos([0.5] * 13))
    revisar(len(angulos) == 26 and len(rigidez) == 26 and set(rigidez) == {100.0}, "26 angulos y 26 rigideces de 100")
    revisar(angulos[C.INDICE["RHipYawPitch"]] == angulos[C.INDICE["LHipYawPitch"]] == 0.05,
            "RHipYawPitch copia a LHipYawPitch (un solo motor)")
    revisar(angulos[C.INDICE["HeadYaw"]] == 0.0 and angulos[C.INDICE["LElbowYaw"]] == -1.57,
            "las articulaciones no controladas quedan en home")

    print("7. Camara (seccion 6.7: ultima medicion cruda, valido < 300 ms)")
    cam = C.EstadoCamara()
    revisar(cam.observacion(0.0) == (0.0, 0.0, 0.0), "al empezar: d = psi = 0, valido = 0")
    cam.nueva_medicion(1.0, 0.10, 0.02, True)
    cam.nueva_medicion(1.1, 0.50, 0.50, False)          # foto sin lineas: se mantiene la anterior
    revisar(cam.observacion(1.25) == (0.10, 0.02, 1.0), "foto sin lineas no cambia el valor; valido dentro de 300 ms")
    revisar(cam.observacion(1.31)[2] == 0.0, "valido = 0 despues de 300 ms sin medicion")

    print("8. Compatibilidad con Python 2.7 (revision estatica)")
    arbol = ast.parse((ROOT / "src" / "race" / "contract.py").read_text(encoding="utf-8"))
    prohibidos = []
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.JoinedStr, ast.AnnAssign, ast.NamedExpr, ast.Nonlocal, ast.YieldFrom, ast.AsyncFunctionDef)):
            prohibidos.append(type(nodo).__name__)
        if isinstance(nodo, ast.BinOp) and isinstance(nodo.op, ast.MatMult):
            prohibidos.append("operador @")
        if isinstance(nodo, (ast.FunctionDef, ast.Lambda)):
            a = nodo.args
            if getattr(nodo, "returns", None) or a.kwonlyargs or any(x.annotation for x in a.args):
                prohibidos.append(f"anotaciones o argumentos solo-nombre en {getattr(nodo, 'name', 'lambda')}")
        if isinstance(nodo, (ast.Import, ast.ImportFrom)):
            mods = [n.name for n in nodo.names] if isinstance(nodo, ast.Import) else [nodo.module]
            prohibidos += [f"import {x}" for x in mods if x not in ("math", "__future__")]
    revisar(not prohibidos, "sin f-strings, anotaciones, :=, nonlocal, @ ni imports fuera de math" +
            (f" -> {prohibidos}" if prohibidos else ""))

    print(f"\nRESULTADO: {'OK' if not FALLAS else 'FALLA'}")
    return 0 if not FALLAS else 1


if __name__ == "__main__":
    sys.exit(main())
