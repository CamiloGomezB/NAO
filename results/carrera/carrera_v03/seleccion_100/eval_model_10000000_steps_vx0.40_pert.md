# Evaluacion de carrera: `runs/carrera_v03/checkpoints/model_10000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 14:23, commit d9733e5. vx_cmd = 0.4 m/s, perturbaciones si, rumbo objetivo de la IMU 'carril'. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 17/20 | 0 | 3 | 13.3 ± 0.5 | 0.374 | 14.7 | 5.6 | 79 |
| no | 0.6 | 17/20 | 0 | 3 | 13.1 ± 0.4 | 0.380 | 13.4 | 5.5 | 78 |
| no | 0.8 | 17/20 | 0 | 3 | 13.1 ± 0.5 | 0.380 | 13.4 | 5.7 | 78 |
| no | 1.0 | 18/20 | 0 | 2 | 13.0 ± 0.5 | 0.382 | 13.6 | 5.4 | 76 |
| no | 1.2 | 18/20 | 0 | 2 | 13.0 ± 0.4 | 0.382 | 13.8 | 4.9 | 75 |
| si | 0.4 | 20/20 | 0 | 0 | 13.0 ± 0.3 | 0.384 | 8.2 | 4.2 | 71 |
| si | 0.6 | 20/20 | 0 | 0 | 12.8 ± 0.3 | 0.388 | 8.2 | 4.8 | 70 |
| si | 0.8 | 19/20 | 0 | 1 | 12.8 ± 0.3 | 0.389 | 8.2 | 5.2 | 69 |
| si | 1.0 | 19/20 | 0 | 1 | 12.8 ± 0.4 | 0.390 | 8.2 | 5.3 | 68 |
| si | 1.2 | 20/20 | 0 | 0 | 12.7 ± 0.3 | 0.391 | 8.2 | 5.5 | 67 |

**Total:** 185/200 metas, 0 caidas, 15 salidas.
Tiempo a meta medio 12.96 s (mejor 12.00 s).
