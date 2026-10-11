# Evaluacion de carrera: `runs/carrera_v02/checkpoints/model_25000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 04:32, commit ea5e992. vx_cmd = 0.5 m/s, perturbaciones si. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 2/4 | 0 | 2 | 10.2 ± 0.0 | 0.478 | 23.3 | 5.4 | 70 |
| no | 0.6 | 1/4 | 0 | 3 | 10.0 ± 0.0 | 0.481 | 25.9 | 5.6 | 71 |
| no | 0.8 | 1/4 | 0 | 3 | 10.0 ± 0.0 | 0.482 | 24.4 | 5.7 | 70 |
| no | 1.0 | 1/4 | 0 | 3 | 10.0 ± 0.0 | 0.485 | 24.8 | 5.3 | 70 |
| no | 1.2 | 1/4 | 0 | 3 | 10.0 ± 0.0 | 0.480 | 23.9 | 5.5 | 70 |
| si | 0.4 | 2/4 | 1 | 1 | 10.1 ± 0.1 | 0.427 | 11.9 | 6.9 | 92 |
| si | 0.6 | 3/4 | 0 | 1 | 10.0 ± 0.0 | 0.483 | 10.0 | 5.6 | 72 |
| si | 0.8 | 3/4 | 0 | 1 | 10.0 ± 0.0 | 0.484 | 9.8 | 5.5 | 72 |
| si | 1.0 | 3/4 | 0 | 1 | 10.0 ± 0.0 | 0.486 | 10.3 | 5.5 | 71 |
| si | 1.2 | 3/4 | 0 | 1 | 10.0 ± 0.0 | 0.484 | 10.4 | 5.4 | 72 |

**Total:** 20/40 metas, 1 caidas, 19 salidas.
Tiempo a meta medio 10.03 s (mejor 9.94 s).
