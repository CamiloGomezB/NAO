# Evaluacion de carrera: `policies/rl_v1.2.1/model.zip`

`scripts/eval_carrera.py`, 2026-10-14 11:00, commit a1f6170. vx_cmd = 0.45 m/s, perturbaciones no, rumbo objetivo de la IMU 'carril'. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| si | 0.4 | 5/5 | 0 | 0 | 11.9 ± 0.0 | 0.419 | 3.9 | 3.7 | 37 |
| si | 0.6 | 5/5 | 0 | 0 | 11.8 ± 0.1 | 0.421 | 4.4 | 2.8 | 38 |
| si | 0.8 | 5/5 | 0 | 0 | 11.8 ± 0.1 | 0.422 | 4.6 | 2.8 | 37 |
| si | 1.0 | 5/5 | 0 | 0 | 11.7 ± 0.0 | 0.425 | 4.0 | 2.9 | 37 |
| si | 1.2 | 5/5 | 0 | 0 | 11.5 ± 0.1 | 0.431 | 4.2 | 2.9 | 37 |

**Total:** 25/25 metas, 0 caidas, 0 salidas.
Tiempo a meta medio 11.74 s (mejor 11.43 s).
Esfuerzo de los motores (par RMS / par continuo, limite 80 %): maximo 79 % (RHipPitch); corridas sobre el 80 %: 0/25.
