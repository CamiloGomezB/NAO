# Evaluacion de carrera: `policies/rl_v1.2/model.zip`

`scripts/eval_carrera.py`, 2026-10-14 04:44, commit cee48ff. vx_cmd = 0.45 m/s, perturbaciones no, rumbo objetivo de la IMU 'carril'. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| si | 0.4 | 5/5 | 0 | 0 | 11.0 ± 0.0 | 0.453 | 10.6 | 3.0 | 40 |
| si | 0.6 | 5/5 | 0 | 0 | 10.9 ± 0.1 | 0.457 | 12.6 | 2.5 | 38 |
| si | 0.8 | 5/5 | 0 | 0 | 10.9 ± 0.1 | 0.457 | 14.9 | 2.6 | 38 |
| si | 1.0 | 5/5 | 0 | 0 | 10.9 ± 0.1 | 0.456 | 17.7 | 2.7 | 37 |
| si | 1.2 | 5/5 | 0 | 0 | 10.9 ± 0.1 | 0.457 | 18.0 | 2.8 | 37 |

**Total:** 25/25 metas, 0 caidas, 0 salidas.
Tiempo a meta medio 10.91 s (mejor 10.71 s).
Esfuerzo de los motores (par RMS / par continuo, limite 80 %): maximo 77 % (RHipPitch); corridas sobre el 80 %: 0/25.
