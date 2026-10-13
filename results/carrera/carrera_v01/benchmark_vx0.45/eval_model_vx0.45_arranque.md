# Evaluacion de carrera: `policies/carrera_v01/model.zip`

`scripts/eval_carrera.py`, 2026-10-13 08:20, commit f18831a. vx_cmd = 0.45 m/s, perturbaciones no, rumbo objetivo de la IMU 'arranque'. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| si | 0.4 | 5/5 | 0 | 0 | 11.5 ± 0.1 | 0.434 | 6.0 | 3.9 | 68 |
| si | 0.6 | 5/5 | 0 | 0 | 11.5 ± 0.1 | 0.434 | 6.3 | 3.6 | 67 |
| si | 0.8 | 5/5 | 0 | 0 | 11.5 ± 0.1 | 0.434 | 6.7 | 3.4 | 67 |
| si | 1.0 | 5/5 | 0 | 0 | 11.5 ± 0.1 | 0.433 | 6.9 | 3.6 | 67 |
| si | 1.2 | 5/5 | 0 | 0 | 11.5 ± 0.1 | 0.433 | 7.1 | 3.5 | 66 |

**Total:** 25/25 metas, 0 caidas, 0 salidas.
Tiempo a meta medio 11.52 s (mejor 11.28 s).
