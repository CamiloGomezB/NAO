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
