# Evaluacion de carrera: `runs/carrera_v02/final_model.zip`

`scripts/eval_carrera.py`, 2026-10-11 05:55, commit ea5e992. vx_cmd = 0.5 m/s, perturbaciones si. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 2/4 | 0 | 2 | 9.7 ± 0.2 | 0.498 | 18.5 | 7.8 | 66 |
| no | 0.6 | 3/4 | 0 | 1 | 9.6 ± 0.1 | 0.501 | 19.0 | 9.9 | 66 |
| no | 0.8 | 3/4 | 0 | 1 | 9.6 ± 0.1 | 0.510 | 18.3 | 7.6 | 63 |
| no | 1.0 | 3/4 | 0 | 1 | 9.6 ± 0.1 | 0.511 | 19.2 | 8.2 | 63 |
| no | 1.2 | 3/4 | 0 | 1 | 9.6 ± 0.2 | 0.510 | 20.7 | 8.7 | 62 |
| si | 0.4 | 3/4 | 0 | 1 | 10.0 ± 0.2 | 0.496 | 14.2 | 6.3 | 62 |
| si | 0.6 | 3/4 | 1 | 0 | 9.8 ± 0.2 | 0.417 | 8.6 | 6.1 | 96 |
| si | 0.8 | 3/4 | 1 | 0 | 9.8 ± 0.2 | 0.434 | 8.8 | 7.8 | 83 |
| si | 1.0 | 3/4 | 1 | 0 | 9.7 ± 0.2 | 0.450 | 9.1 | 13.9 | 79 |
| si | 1.2 | 3/4 | 1 | 0 | 9.7 ± 0.2 | 0.436 | 8.4 | 5.2 | 82 |

**Total:** 29/40 metas, 4 caidas, 7 salidas.
Tiempo a meta medio 9.72 s (mejor 9.27 s).
