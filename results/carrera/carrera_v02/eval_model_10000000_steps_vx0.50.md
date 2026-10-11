# Evaluacion de carrera: `runs/carrera_v02/checkpoints/model_10000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 03:07, commit ea5e992. vx_cmd = 0.5 m/s, perturbaciones no. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 1/2 | 0 | 1 | 10.4 ± 0.0 | 0.475 | 19.3 | 9.1 | 73 |
| no | 0.6 | 1/2 | 0 | 1 | 10.4 ± 0.0 | 0.475 | 18.4 | 8.4 | 72 |
| no | 0.8 | 1/2 | 0 | 1 | 10.3 ± 0.0 | 0.477 | 16.1 | 8.5 | 72 |
| no | 1.0 | 1/2 | 0 | 1 | 10.2 ± 0.0 | 0.468 | 16.7 | 7.5 | 73 |
| no | 1.2 | 1/2 | 0 | 1 | 10.4 ± 0.0 | 0.479 | 17.1 | 6.8 | 71 |
| si | 0.4 | 2/2 | 0 | 0 | 10.1 ± 0.1 | 0.491 | 11.6 | 5.9 | 67 |
| si | 0.6 | 2/2 | 0 | 0 | 10.1 ± 0.1 | 0.492 | 11.0 | 4.0 | 68 |
| si | 0.8 | 2/2 | 0 | 0 | 10.1 ± 0.1 | 0.491 | 10.5 | 5.2 | 68 |
| si | 1.0 | 2/2 | 0 | 0 | 10.1 ± 0.1 | 0.495 | 11.5 | 4.5 | 67 |
| si | 1.2 | 2/2 | 0 | 0 | 10.1 ± 0.1 | 0.495 | 12.2 | 4.1 | 67 |

**Total:** 15/20 metas, 0 caidas, 5 salidas.
Tiempo a meta medio 10.19 s (mejor 9.99 s).
