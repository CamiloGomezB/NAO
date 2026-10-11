# -*- coding: utf-8 -*-
"""Contrato v1 de la politica de carrera: que entra (observacion de 54 valores) y que sale (13 angulos).

Este archivo es el "idioma comun" entre el entrenamiento (MuJoCo), la demo de 3 carriles y el NAO real a
traves de PenaltyStack. Por eso:
  - es compatible con Python 2.7 (NAOqi 2.8 a bordo) y Python 3, sin numpy ni dependencias;
  - recibe los sensores con el formato del `SensorAdapter` de PenaltyStack (`frame`): angles[26], velocity[26],
    gyro[3], acc[3], orientation[4] (cuaternion wxyz del torso), fsr[8] (kg);
  - devuelve los angulos en el orden de las 26 articulaciones de B-Human (third_party/penaltystack/motion_contract.py).

Diseno: docs/plan_rl_carrera.md, secciones 6.1 (observacion), 6.2 (accion) y 6.7 (como llegan d y psi).
Verificacion: scripts/check_contract.py.

Valores marcados (a validar) se revisan en el paso 46 (valores del modelo V6) y en la sesion con el robot.
"""
from __future__ import division

import math

VERSION_CONTRATO = "v1"

# ------------------------------------------------------------------------------ tiempos
CICLO_S = 0.012                 # ciclo del motor de PenaltyStack y de LoLA en el NAO V6
CICLOS_POR_ACCION = 2
PERIODO_POLITICA_S = CICLO_S * CICLOS_POR_ACCION   # 24 ms (~41.7 Hz)
PERIODO_MARCHA_S = 0.5          # ciclo de marcha = 2 pasos de 250 ms, como el WalkingEngine de B-Human (paso 46).
                                # El sprint usaba 0.6 s. Es un parametro del barrido de 100 agentes (rango 0.4-0.7).
PERIODO_CAMARA_S = 0.1          # 10 FPS
VALIDEZ_CAMARA_S = 0.3          # "valido" = hubo medicion en los ultimos 300 ms

# ------------------------------------------------------------------------------ articulaciones
# Orden de las 26 articulaciones de B-Human (copia exacta de PenaltyStack/penalty/motion_contract.py, commit 9c08a41).
JOINT_NAMES_BHUMAN = (
    'headYaw', 'headPitch',
    'lShoulderPitch', 'lShoulderRoll', 'lElbowYaw', 'lElbowRoll', 'lWristYaw', 'lHand',
    'rShoulderPitch', 'rShoulderRoll', 'rElbowYaw', 'rElbowRoll', 'rWristYaw', 'rHand',
    'lHipYawPitch', 'lHipRoll', 'lHipPitch', 'lKneePitch', 'lAnklePitch', 'lAnkleRoll',
    'rHipYawPitch', 'rHipRoll', 'rHipPitch', 'rKneePitch', 'rAnklePitch', 'rAnkleRoll',
)
# Los mismos nombres con la convencion del modelo MuJoCo y de NAOqi ("LHipRoll").
NOMBRES_MODELO = tuple(n[0].upper() + n[1:] for n in JOINT_NAMES_BHUMAN)
INDICE = dict((n, i) for i, n in enumerate(NOMBRES_MODELO))

# Las 13 articulaciones que controla la politica, en el orden del vector de accion.
ARTICULACIONES_ACCION = (
    "LHipYawPitch",                                   # un solo motor para las dos caderas (RHipYawPitch lo copia)
    "LHipRoll", "LHipPitch", "LKneePitch", "LAnklePitch", "LAnkleRoll",
    "RHipRoll", "RHipPitch", "RKneePitch", "RAnklePitch", "RAnkleRoll",
    "LShoulderPitch", "RShoulderPitch",
)
N_ACCION = len(ARTICULACIONES_ACCION)

# Pose de pie "home" del modelo V6 (keyframe "home" de assets/nao/nao.xml). Las articulaciones que no controla
# la politica se quedan aqui. (a validar, paso 46: es la misma pose del modelo aproximado del sprint inicial)
POSE_HOME = {
    "HeadYaw": 0.0, "HeadPitch": 0.0,
    "LShoulderPitch": 1.57, "LShoulderRoll": 0.2, "LElbowYaw": -1.57, "LElbowRoll": -0.2, "LWristYaw": 0.0, "LHand": 0.0,
    "RShoulderPitch": 1.57, "RShoulderRoll": -0.2, "RElbowYaw": 1.57, "RElbowRoll": 0.2, "RWristYaw": 0.0, "RHand": 0.0,
    "LHipYawPitch": 0.0, "LHipRoll": 0.0, "LHipPitch": -0.4, "LKneePitch": 0.8, "LAnklePitch": -0.4, "LAnkleRoll": 0.0,
    "RHipYawPitch": 0.0, "RHipRoll": 0.0, "RHipPitch": -0.4, "RKneePitch": 0.8, "RAnklePitch": -0.4, "RAnkleRoll": 0.0,
}

# Desviacion maxima respecto a home [rad] para accion = -1 y para accion = +1 (diseno, seccion 6.2).
# HipRoll es ASIMETRICO: hacia afuera hasta 0.25, hacia adentro solo 0.07, porque en el V6 hay ~3 cm entre las
# piernas y ~0.075 rad hacia adentro las cruzan (registro de errores E16). Convencion NAOqi: LHipRoll positivo
# abre la pierna izquierda; RHipRoll negativo abre la derecha.
LIMITES_ACCION = {
    "LHipYawPitch": (-0.10, 0.10),   # (a validar) girar para corregir el rumbo
    "LHipRoll": (-0.07, 0.25),       # (a validar) adentro / afuera
    "RHipRoll": (-0.25, 0.07),       # (a validar) afuera / adentro
    "LHipPitch": (-0.5, 0.5), "RHipPitch": (-0.5, 0.5),
    "LKneePitch": (-0.5, 0.5), "RKneePitch": (-0.5, 0.5),
    "LAnklePitch": (-0.4, 0.4), "RAnklePitch": (-0.4, 0.4),
    "LAnkleRoll": (-0.25, 0.25), "RAnkleRoll": (-0.25, 0.25),
    "LShoulderPitch": (-0.5, 0.5), "RShoulderPitch": (-0.5, 0.5),
}

# Presupuesto lateral COMBINADO (paso 46). Los limites por articulacion no bastan: con las dos caderas y los dos
# tobillos hacia adentro a la vez, los pies se cruzan (2.2 % de acciones al azar, hasta 2.1 cm; registro E40). Si la
# SUMA de lo que entran las dos piernas pasa del presupuesto, esas componentes se escalan. Cada peso es cuanto acerca
# los pies cada articulacion respecto a HipRoll (medido en el V6: HipRoll 22.1 cm/rad por pierna, AnkleRoll 3.85,
# HipYawPitch +10.6 / -5.4 cm/rad). Presupuesto 0.09 rad equivalentes de cadera: 0 cruces en 20,000 acciones al azar
# y todos los extremos, con margen minimo de 0.34 cm (scripts/check_valores_v6.py).
PRESUPUESTO_ADENTRO_RAD = 0.09
PESO_ADENTRO_TOBILLO = 0.174
PESO_HIPYAWPITCH_POS = 0.48
PESO_HIPYAWPITCH_NEG = 0.245

# ------------------------------------------------------------------------------ observacion (54 valores)
ESCALA_GIRO = 0.25              # giroscopio [rad/s] * 0.25
ESCALA_VEL_ARTICULAR = 0.05     # velocidad articular [rad/s] * 0.05
LIMITE_ERROR_RUMBO = math.pi / 2
MASA_ROBOT_KG = 5.36            # NAO V6 (NaoV6H25.rsi3 de B-Human)

LAYOUT_OBSERVACION = (          # (nombre, dimension) en el orden del vector
    ("gravedad_proyectada", 3),     # vector "abajo" en el marco del torso (inclinacion), de la IMU
    ("vel_angular_torso", 3),       # giroscopio * ESCALA_GIRO
    ("error_rumbo_imu", 1),         # rumbo objetivo - rumbo de la IMU, recortado a +-pi/2
    ("d_camara", 1),                # desplazamiento lateral en el carril [m], + = robot a la izquierda (seccion 6.7)
    ("psi_camara", 1),              # angulo respecto a las lineas [rad], + = girado a la izquierda
    ("valido_camara", 1),           # 1 si hubo medicion en los ultimos 300 ms
    ("q_articular", N_ACCION),      # angulo - angulo home de las 13 articulaciones [rad]
    ("dq_articular", N_ACCION),     # velocidad articular * ESCALA_VEL_ARTICULAR
    ("accion_anterior", N_ACCION),  # ultima accion en [-1, 1]
    ("carga_pies", 2),              # (izquierdo, derecho): suma de sus 4 FSR / masa del robot
    ("reloj_marcha", 2),            # seno y coseno de la fase de marcha
    ("vx_cmd", 1),                  # velocidad pedida [m/s]
)
DIM_OBSERVACION = sum(dim for _, dim in LAYOUT_OBSERVACION)


def rebanadas_observacion():
    """Posicion de cada componente en el vector: {nombre: (inicio, fin)}."""
    out, inicio = {}, 0
    for nombre, dim in LAYOUT_OBSERVACION:
        out[nombre] = (inicio, inicio + dim)
        inicio += dim
    return out


# ------------------------------------------------------------------------------ utilidades sin numpy
def _recortar(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


def envolver_angulo(a):
    """Angulo en [-pi, pi)."""
    return (a + math.pi) % (2.0 * math.pi) - math.pi


def gravedad_proyectada(q_wxyz):
    """Vector (0, 0, -1) del mundo expresado en el marco del torso, a partir del cuaternion wxyz del torso."""
    w, x, y, z = q_wxyz
    # Tercera fila de la matriz de rotacion torso->mundo, cambiada de signo (R^T * (0, 0, -1)).
    return (-(2.0 * (x * z - w * y)), -(2.0 * (y * z + w * x)), -(1.0 - 2.0 * (x * x + y * y)))


def rumbo_desde_cuaternion(q_wxyz):
    """Rumbo (yaw) del torso [rad] a partir del cuaternion wxyz."""
    w, x, y, z = q_wxyz
    return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))


def rumbo_objetivo_inicial(rumbo_imu, psi_mediciones):
    """Rumbo objetivo de la IMU al arrancar = direccion del CARRIL (paso 58c, registro de errores E50).

    De pie, antes de arrancar, la camara mide psi (angulo del robot respecto a las lineas, + = girado a la izquierda).
    La direccion del carril en el marco de la IMU es rumbo_imu - psi. Si el robot arranco torcido, la IMU le pide ir
    hacia el carril y no mantener el angulo torcido. Sin mediciones validas se usa el rumbo de la IMU (como antes).

    rumbo_imu: rumbo actual de la IMU [rad]. psi_mediciones: lista de psi crudos validos tomados de pie [rad].
    """
    if not psi_mediciones:
        return envolver_angulo(rumbo_imu)
    psi_medio = sum(psi_mediciones) / float(len(psi_mediciones))
    return envolver_angulo(rumbo_imu - psi_medio)


def carga_pies(fsr8, masa_kg=MASA_ROBOT_KG):
    """(izquierdo, derecho) = suma de los 4 FSR de cada pie [kg] / masa del robot. Orden PenaltyStack:
    izquierdo fl, fr, bl, br y derecho fl, fr, bl, br."""
    izq = sum(fsr8[0:4]) / masa_kg
    der = sum(fsr8[4:8]) / masa_kg
    return (_recortar(izq, 0.0, 2.0), _recortar(der, 0.0, 2.0))


def reloj_marcha(t_s, periodo_s=PERIODO_MARCHA_S):
    fase = 2.0 * math.pi * ((t_s / periodo_s) % 1.0)
    return (math.sin(fase), math.cos(fase))


# ------------------------------------------------------------------------------ camara: d, psi, valido
class EstadoCamara(object):
    """Lo que recibe la politica de la vision (diseno, seccion 6.7): la ultima medicion CRUDA (sin filtrar),
    mantenida entre fotos, y valido = 1 si la ultima medicion tiene menos de 300 ms. Al empezar: 0, 0, 0."""

    def __init__(self):
        self.d, self.psi, self.t_medicion = 0.0, 0.0, None

    def nueva_medicion(self, t_s, d, psi, valida):
        """Llamar con cada foto procesada (10 Hz). Si la foto no encontro lineas, se mantiene el valor anterior."""
        if valida:
            self.d, self.psi, self.t_medicion = float(d), float(psi), float(t_s)

    def observacion(self, t_s):
        valido = self.t_medicion is not None and (t_s - self.t_medicion) <= VALIDEZ_CAMARA_S + 1e-9
        return (self.d, self.psi, 1.0 if valido else 0.0)


# ------------------------------------------------------------------------------ armar la observacion
def armar_observacion(frame, rumbo_objetivo, camara, accion_anterior, t_marcha_s, vx_cmd):
    """Observacion de 54 valores (lista de float) desde un frame con el formato de PenaltyStack.

    frame: dict con "angles" (26), "velocity" (26), "gyro" (3), "orientation" (wxyz) y "fsr" (8), en el orden de
           JOINT_NAMES_BHUMAN. En el NAO real se arma con ALMemory; en MuJoCo, con el estado de la simulacion.
    rumbo_objetivo: rumbo [rad] que la IMU debe mantener (el de la salida).
    camara: tupla (d, psi, valido) de EstadoCamara.observacion().
    accion_anterior: las 13 acciones del paso anterior, en [-1, 1].
    t_marcha_s: tiempo desde que arranco la marcha [s] (reloj de marcha).
    vx_cmd: velocidad pedida [m/s].
    """
    if len(accion_anterior) != N_ACCION:
        raise ValueError("accion_anterior debe tener %d valores" % N_ACCION)
    ang, vel = frame["angles"], frame["velocity"]
    if len(ang) != 26 or len(vel) != 26 or len(frame["fsr"]) != 8:
        raise ValueError("frame invalido: se esperan 26 angulos, 26 velocidades y 8 FSR")
    q = frame["orientation"]
    obs = []
    obs += gravedad_proyectada(q)
    obs += [g * ESCALA_GIRO for g in frame["gyro"]]
    obs.append(_recortar(envolver_angulo(rumbo_objetivo - rumbo_desde_cuaternion(q)),
                         -LIMITE_ERROR_RUMBO, LIMITE_ERROR_RUMBO))
    d, psi, valido = camara
    obs += [float(d), float(psi), float(valido)]
    obs += [ang[INDICE[n]] - POSE_HOME[n] for n in ARTICULACIONES_ACCION]
    obs += [vel[INDICE[n]] * ESCALA_VEL_ARTICULAR for n in ARTICULACIONES_ACCION]
    obs += [float(a) for a in accion_anterior]
    obs += carga_pies(frame["fsr"])
    obs += reloj_marcha(t_marcha_s)
    obs.append(float(vx_cmd))
    assert len(obs) == DIM_OBSERVACION
    return obs


# ------------------------------------------------------------------------------ accion -> angulos
def accion_a_objetivos(accion):
    """13 acciones en [-1, 1] -> {articulacion: angulo objetivo [rad]} (solo las 13 controladas).

    accion = 0 es la pose home; +1 suma el limite superior y -1 el inferior (asimetrico en HipRoll)."""
    if len(accion) != N_ACCION:
        raise ValueError("la accion debe tener %d valores" % N_ACCION)
    off = {}
    for nombre, a in zip(ARTICULACIONES_ACCION, accion):
        a = _recortar(float(a), -1.0, 1.0)
        lo, hi = LIMITES_ACCION[nombre]
        off[nombre] = a * hi if a >= 0.0 else -a * lo
    _aplicar_presupuesto_adentro(off)
    return dict((n, POSE_HOME[n] + off[n]) for n in ARTICULACIONES_ACCION)


def cuanto_adentro(off):
    """Cuanto entran las dos piernas, en radianes equivalentes de HipRoll, para desviaciones off respecto a home.
    Convencion NAOqi: hacia adentro es LHipRoll/LAnkleRoll negativo y RHipRoll/RAnkleRoll positivo."""
    y = off["LHipYawPitch"]
    return (max(0.0, -off["LHipRoll"]) + max(0.0, off["RHipRoll"])
            + PESO_ADENTRO_TOBILLO * (max(0.0, -off["LAnkleRoll"]) + max(0.0, off["RAnkleRoll"]))
            + (PESO_HIPYAWPITCH_POS * y if y > 0.0 else PESO_HIPYAWPITCH_NEG * (-y)))


def _aplicar_presupuesto_adentro(off):
    """Si las dos piernas entran mas que el presupuesto, escala solo las componentes que van hacia adentro."""
    total = cuanto_adentro(off)
    if total <= PRESUPUESTO_ADENTRO_RAD:
        return
    f = PRESUPUESTO_ADENTRO_RAD / total
    for nombre, signo_adentro in (("LHipRoll", -1), ("RHipRoll", 1), ("LAnkleRoll", -1), ("RAnkleRoll", 1)):
        if off[nombre] * signo_adentro > 0.0:
            off[nombre] *= f
    off["LHipYawPitch"] *= f


def objetivos_a_salida_bhuman(objetivos, rigidez=100.0):
    """{articulacion: angulo} -> (angles[26], stiffness[26]) en el orden de B-Human, como lo recibe PenaltyStack.

    Las articulaciones no controladas se quedan en home; RHipYawPitch copia a LHipYawPitch (un solo motor)."""
    angulos = [POSE_HOME[n] for n in NOMBRES_MODELO]
    for nombre, valor in objetivos.items():
        angulos[INDICE[nombre]] = float(valor)
    angulos[INDICE["RHipYawPitch"]] = angulos[INDICE["LHipYawPitch"]]
    return angulos, [float(rigidez)] * len(NOMBRES_MODELO)
