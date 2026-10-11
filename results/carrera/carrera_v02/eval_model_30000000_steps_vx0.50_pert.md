# Evaluacion de carrera: `runs/carrera_v02/checkpoints/model_30000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 05:00, commit ea5e992. vx_cmd = 0.5 m/s, perturbaciones si. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 2/4 | 0 | 2 | 10.6 ± 0.2 | 0.471 | 22.1 | 6.0 | 70 |
| no | 0.6 | 1/4 | 0 | 3 | 10.7 ± 0.0 | 0.473 | 26.1 | 5.9 | 69 |
| no | 0.8 | 1/4 | 0 | 3 | 10.2 ± 0.0 | 0.473 | 26.1 | 5.9 | 68 |
| no | 1.0 | 1/4 | 0 | 3 | 10.2 ± 0.0 | 0.473 | 24.9 | 6.2 | 68 |
| no | 1.2 | 1/4 | 0 | 3 | 10.2 ± 0.0 | 0.476 | 23.5 | 6.2 | 67 |
| si | 0.4 | 4/4 | 0 | 0 | 10.7 ± 0.3 | 0.462 | 13.7 | 5.6 | 75 |
| si | 0.6 | 4/4 | 0 | 0 | 10.7 ± 0.4 | 0.464 | 15.2 | 5.1 | 74 |
| si | 0.8 | 4/4 | 0 | 0 | 10.8 ± 0.5 | 0.462 | 17.7 | 4.8 | 74 |
| si | 1.0 | 3/4 | 0 | 1 | 10.6 ± 0.5 | 0.463 | 18.5 | 4.8 | 73 |
| si | 1.2 | 4/4 | 0 | 0 | 10.7 ± 0.5 | 0.464 | 18.3 | 5.0 | 73 |

**Total:** 25/40 metas, 0 caidas, 15 salidas.
Tiempo a meta medio 10.64 s (mejor 10.01 s).
