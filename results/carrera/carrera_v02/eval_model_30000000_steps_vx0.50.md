# Evaluacion de carrera: `runs/carrera_v02/checkpoints/model_30000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 05:00, commit ea5e992. vx_cmd = 0.5 m/s, perturbaciones no. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 1/2 | 0 | 1 | 10.2 ± 0.0 | 0.483 | 22.1 | 5.2 | 73 |
| no | 0.6 | 2/2 | 0 | 0 | 10.4 ± 0.0 | 0.477 | 17.8 | 5.5 | 75 |
| no | 0.8 | 2/2 | 0 | 0 | 10.4 ± 0.0 | 0.480 | 16.8 | 5.8 | 76 |
| no | 1.0 | 2/2 | 0 | 0 | 10.2 ± 0.0 | 0.488 | 15.0 | 6.0 | 73 |
| no | 1.2 | 2/2 | 0 | 0 | 10.1 ± 0.1 | 0.491 | 14.6 | 5.7 | 71 |
| si | 0.4 | 2/2 | 0 | 0 | 10.7 ± 0.0 | 0.464 | 8.8 | 3.3 | 79 |
| si | 0.6 | 2/2 | 0 | 0 | 10.5 ± 0.0 | 0.469 | 6.4 | 3.3 | 76 |
| si | 0.8 | 2/2 | 0 | 0 | 10.5 ± 0.0 | 0.471 | 5.9 | 3.1 | 77 |
| si | 1.0 | 2/2 | 0 | 0 | 10.5 ± 0.0 | 0.470 | 5.4 | 3.3 | 75 |
| si | 1.2 | 2/2 | 0 | 0 | 10.5 ± 0.0 | 0.474 | 6.1 | 3.5 | 75 |

**Total:** 19/20 metas, 0 caidas, 1 salidas.
Tiempo a meta medio 10.42 s (mejor 10.04 s).
