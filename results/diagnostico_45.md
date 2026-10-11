# Diagnóstico del paso 45: caídas al pausar/reanudar y choque entre piernas (V6)

Generado por `scripts/diag_caidas.py`. Política: `checkpoints\best_model.zip`. Semillas 1000–1029. Datos completos en `diagnostico_45.json`.

## (a) Pausas al azar

| Modo | Episodios | Pausas | Episodios con caída | Momento | Motivo | Articulación | Con choque de piernas |
|---|---|---|---|---|---|---|---|
| demo | 30 | 62 | 28 (93.3 %) | {'al_reanudar': 9, 'en_pausa': 19} | {'inclinacion': 28} | {'LShoulderPitch': 1, 'LHipRoll': 1, 'RShoulderPitch': 1, 'RHipRoll': 3, 'RAnklePitch': 20, 'RKneePitch': 1, 'LKneePitch': 1} | 6 |
| demo_reloj_fijo | 30 | 60 | 29 (96.7 %) | {'en_pausa': 18, 'al_reanudar': 11} | {'inclinacion': 29} | {'RAnklePitch': 19, 'RShoulderPitch': 2, 'RHipRoll': 5, 'LAnklePitch': 2, 'RHipPitch': 1} | 7 |
| inmediata | 30 | 36 | 30 (100.0 %) | {'al_reanudar': 4, 'en_pausa': 26} | {'inclinacion': 30} | {'RHipRoll': 8, 'LKneePitch': 7, 'RKneePitch': 4, 'LHipRoll': 1, 'RAnklePitch': 9, 'RShoulderPitch': 1} | 16 |
| pose_home | 30 | 142 | 8 (26.7 %) | {'en_pausa': 7, 'al_reanudar': 1} | {'inclinacion': 7, 'altura': 1} | {'RKneePitch': 6, 'LHipPitch': 1, 'LKneePitch': 1} | 0 |

## (b) Piernas

| Fuente | Pasos | Caídas | Pasos con choque | Distancia mínima |
|---|---|---|---|---|
| acciones aleatorias uniformes | 751 | 20 | 58 (7.723 %) | -1.28 cm |
| acciones aleatorias uniformes, contrato v1 con presupuesto lateral (NaoRace-v0) | 660 | 20 | 7 (1.061 %) | -0.43 cm |
| politica del sprint (best_model.zip) de corrido | 10000 | 0 | 0 (0.0 %) | 0.15 cm |
| politica desde cero en el V6 (diag45_desde_cero_2M) | 10000 | 0 | 16 (0.16 %) | -0.12 cm |
