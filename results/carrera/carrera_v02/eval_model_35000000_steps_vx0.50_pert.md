# Evaluacion de carrera: `runs/carrera_v02/checkpoints/model_35000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 05:27, commit ea5e992. vx_cmd = 0.5 m/s, perturbaciones si. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 3/4 | 0 | 1 | 10.7 ± 0.2 | 0.459 | 15.2 | 5.8 | 64 |
| no | 0.6 | 3/4 | 0 | 1 | 10.5 ± 0.2 | 0.466 | 14.0 | 5.8 | 64 |
| no | 0.8 | 3/4 | 0 | 1 | 10.5 ± 0.2 | 0.470 | 14.3 | 5.5 | 63 |
| no | 1.0 | 3/4 | 0 | 1 | 10.5 ± 0.2 | 0.472 | 15.1 | 5.6 | 62 |
| no | 1.2 | 3/4 | 0 | 1 | 10.4 ± 0.2 | 0.474 | 15.6 | 5.4 | 62 |
| si | 0.4 | 3/4 | 0 | 1 | 10.7 ± 0.5 | 0.462 | 17.4 | 6.0 | 63 |
| si | 0.6 | 3/4 | 0 | 1 | 10.5 ± 0.4 | 0.472 | 15.5 | 6.4 | 61 |
| si | 0.8 | 3/4 | 0 | 1 | 10.3 ± 0.3 | 0.477 | 15.1 | 6.3 | 60 |
| si | 1.0 | 3/4 | 0 | 1 | 10.3 ± 0.3 | 0.479 | 15.6 | 6.1 | 60 |
| si | 1.2 | 3/4 | 0 | 1 | 10.2 ± 0.2 | 0.481 | 16.1 | 6.1 | 59 |

**Total:** 30/40 metas, 0 caidas, 10 salidas.
Tiempo a meta medio 10.45 s (mejor 9.94 s).
