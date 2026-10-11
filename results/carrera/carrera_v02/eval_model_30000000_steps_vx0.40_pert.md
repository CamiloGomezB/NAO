# Evaluacion de carrera: `runs/carrera_v02/checkpoints/model_30000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 05:01, commit ea5e992. vx_cmd = 0.4 m/s, perturbaciones si. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 3/4 | 0 | 1 | 13.2 ± 0.4 | 0.370 | 17.0 | 5.5 | 75 |
| no | 0.6 | 2/4 | 0 | 2 | 13.1 ± 0.1 | 0.369 | 20.5 | 5.5 | 77 |
| no | 0.8 | 2/4 | 0 | 2 | 13.0 ± 0.1 | 0.372 | 20.3 | 5.3 | 75 |
| no | 1.0 | 1/4 | 0 | 3 | 13.0 ± 0.0 | 0.373 | 21.3 | 5.5 | 75 |
| no | 1.2 | 1/4 | 0 | 3 | 13.0 ± 0.0 | 0.372 | 21.2 | 5.5 | 74 |
| si | 0.4 | 4/4 | 0 | 0 | 13.1 ± 0.6 | 0.381 | 13.5 | 5.5 | 76 |
| si | 0.6 | 3/4 | 0 | 1 | 13.0 ± 0.5 | 0.377 | 13.6 | 4.4 | 76 |
| si | 0.8 | 4/4 | 0 | 0 | 13.3 ± 0.7 | 0.375 | 13.7 | 4.9 | 76 |
| si | 1.0 | 3/4 | 0 | 1 | 13.1 ± 0.6 | 0.374 | 13.2 | 4.9 | 75 |
| si | 1.2 | 3/4 | 0 | 1 | 13.0 ± 0.6 | 0.376 | 13.7 | 4.7 | 74 |

**Total:** 26/40 metas, 0 caidas, 14 salidas.
Tiempo a meta medio 13.11 s (mejor 12.24 s).
