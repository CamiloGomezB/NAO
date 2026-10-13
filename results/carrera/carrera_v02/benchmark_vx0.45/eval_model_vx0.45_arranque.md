# Evaluacion de carrera: `policies/carrera_v02/model.zip`

`scripts/eval_carrera.py`, 2026-10-13 08:20, commit f18831a. vx_cmd = 0.45 m/s, perturbaciones no, rumbo objetivo de la IMU 'arranque'. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| si | 0.4 | 5/5 | 0 | 0 | 11.5 ± 0.0 | 0.432 | 7.8 | 4.6 | 62 |
| si | 0.6 | 5/5 | 0 | 0 | 11.5 ± 0.0 | 0.431 | 8.2 | 3.9 | 60 |
| si | 0.8 | 5/5 | 0 | 0 | 11.5 ± 0.0 | 0.431 | 8.6 | 4.1 | 59 |
| si | 1.0 | 5/5 | 0 | 0 | 11.5 ± 0.0 | 0.431 | 8.9 | 4.2 | 59 |
| si | 1.2 | 5/5 | 0 | 0 | 11.5 ± 0.0 | 0.431 | 9.3 | 4.1 | 58 |

**Total:** 25/25 metas, 0 caidas, 0 salidas.
Tiempo a meta medio 11.51 s (mejor 11.50 s).
