# Evaluacion de carrera: `runs/carrera_v02/checkpoints/model_20000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 04:39, commit ea5e992. vx_cmd = 0.4 m/s, perturbaciones si. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 18/20 | 0 | 2 | 12.6 ± 0.3 | 0.393 | 12.9 | 7.5 | 71 |
| no | 0.6 | 17/20 | 0 | 3 | 12.7 ± 0.3 | 0.391 | 12.0 | 7.0 | 71 |
| no | 0.8 | 18/20 | 0 | 2 | 12.8 ± 0.4 | 0.389 | 12.4 | 6.1 | 70 |
| no | 1.0 | 17/20 | 0 | 3 | 12.8 ± 0.3 | 0.388 | 13.5 | 5.2 | 69 |
| no | 1.2 | 16/20 | 0 | 4 | 12.8 ± 0.3 | 0.387 | 14.7 | 4.3 | 67 |
| si | 0.4 | 20/20 | 0 | 0 | 12.4 ± 0.5 | 0.403 | 9.9 | 6.1 | 70 |
| si | 0.6 | 20/20 | 0 | 0 | 12.4 ± 0.5 | 0.402 | 9.9 | 5.9 | 70 |
| si | 0.8 | 20/20 | 0 | 0 | 12.5 ± 0.6 | 0.400 | 10.3 | 5.6 | 70 |
| si | 1.0 | 20/20 | 0 | 0 | 12.6 ± 0.5 | 0.397 | 10.2 | 4.9 | 69 |
| si | 1.2 | 20/20 | 0 | 0 | 12.6 ± 0.6 | 0.396 | 10.0 | 4.5 | 68 |

**Total:** 186/200 metas, 0 caidas, 14 salidas.
Tiempo a meta medio 12.61 s (mejor 11.69 s).
