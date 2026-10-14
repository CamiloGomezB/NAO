"""Valores del modelo NAO V6 para el entorno de carrera, medidos en el paso 46 (scripts/check_valores_v6.py).

Reemplazan a los que el entorno del sprint inicial (src/envs/nao_walk_env.py) heredo del modelo aproximado V5. Ese
entorno NO se cambia: lo usa la politica del sprint (checkpoints/best_model.zip) en la demo de 3 carriles.

Los valores que tambien necesita el robot (pose home, limites de accion, presupuesto lateral, periodo de marcha,
ciclo de 24 ms) estan en src/race/contract.py.
"""

# Altura del torso de pie, asentado 2 s con los servos en la pose home: 315.9 mm (modelo aproximado: 0.31 m).
ALTURA_OBJETIVO_M = 0.316

# Caida si el torso baja de esta altura. Agachado al maximo dentro de los limites de accion (rodilla +0.5 rad) el
# torso queda a 291.6 mm sobre la suela; con 5 cm de margen: 0.24 m (modelo aproximado: 0.22 m).
ALTURA_CAIDA_M = 0.24

# Caida si el torso se inclina mas que esto. No depende del modelo: se mantiene el valor del sprint inicial.
INCLINACION_CAIDA_GRADOS = 40.0

# Politica cada 24 ms = 12 pasos de fisica de 2 ms (ciclo de 12 ms de PenaltyStack y del NAO, x2).
FRAME_SKIP = 12

# Referencias medidas en la pose home (informativas):
ALTURA_CADERA_HOME_M = 0.232     # B-Human camina con 230 mm: la pose home ya tiene su altura de cadera
SEPARACION_PIES_M = 0.106        # entre los centros de las suelas
ESPACIO_ENTRE_PIERNAS_M = 0.030  # entre las cajas de colision de las dos piernas

# Par continuo de cada motor del NAO V6 en la articulacion [N.m] = par continuo del motor x reductora, SIN la
# eficiencia del engranaje (cota superior; el motor real se calienta algo antes). Mismos valores que
# scripts/riesgo_motores.py (analisis del 2026-10-13): tipo 5 (22NT Z20, reductora 130.85) en HipPitch, KneePitch y
# AnklePitch; tipo 1 (reductora 201.3) en HipYawPitch, HipRoll y AnkleRoll. Los hombros no tienen dato del motor y
# quedan fuera del limite del 80 % (fase M2 del PLAN).
PAR_CONTINUO_TIPO5_NM = 0.0178 * 130.85     # 2.329
PAR_CONTINUO_TIPO1_NM = 2.47
PAR_CONTINUO_NM = {}
for _lado in "LR":
    for _art in ("HipPitch", "KneePitch", "AnklePitch"):
        PAR_CONTINUO_NM[_lado + _art] = PAR_CONTINUO_TIPO5_NM
    for _art in ("HipRoll", "AnkleRoll"):
        PAR_CONTINUO_NM[_lado + _art] = PAR_CONTINUO_TIPO1_NM
PAR_CONTINUO_NM["LHipYawPitch"] = PAR_CONTINUO_TIPO1_NM
# Limite de la fase M2: par RMS de la corrida <= 80 % del par continuo en cada articulacion con dato del motor.
LIMITE_ESFUERZO = 0.80
# Media movil del esfuerzo para el castigo (constante de tiempo, s): unos 2 ciclos de marcha.
VENTANA_ESFUERZO_S = 1.0
