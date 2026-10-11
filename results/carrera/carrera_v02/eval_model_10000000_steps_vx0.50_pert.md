# Evaluacion de carrera: `runs/carrera_v02/checkpoints/model_10000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 03:07, commit ea5e992. vx_cmd = 0.5 m/s, perturbaciones si. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 2/4 | 0 | 2 | 10.5 ± 0.2 | 0.470 | 17.2 | 8.8 | 68 |
| no | 0.6 | 1/4 | 0 | 3 | 10.4 ± 0.0 | 0.466 | 22.2 | 9.7 | 67 |
| no | 0.8 | 1/4 | 0 | 3 | 10.5 ± 0.0 | 0.468 | 22.2 | 9.7 | 67 |
| no | 1.0 | 1/4 | 0 | 3 | 10.4 ± 0.0 | 0.468 | 21.6 | 6.9 | 67 |
| no | 1.2 | 1/4 | 0 | 3 | 10.4 ± 0.0 | 0.466 | 21.7 | 7.6 | 67 |
| si | 0.4 | 4/4 | 0 | 0 | 10.5 ± 0.3 | 0.476 | 17.1 | 9.6 | 66 |
| si | 0.6 | 4/4 | 0 | 0 | 10.4 ± 0.4 | 0.478 | 17.3 | 9.3 | 65 |
| si | 0.8 | 4/4 | 0 | 0 | 10.4 ± 0.3 | 0.479 | 16.8 | 7.8 | 66 |
| si | 1.0 | 4/4 | 0 | 0 | 10.4 ± 0.3 | 0.480 | 15.8 | 6.3 | 65 |
| si | 1.2 | 4/4 | 0 | 0 | 10.3 ± 0.3 | 0.483 | 16.1 | 5.5 | 65 |

**Total:** 26/40 metas, 0 caidas, 14 salidas.
Tiempo a meta medio 10.41 s (mejor 9.96 s).
