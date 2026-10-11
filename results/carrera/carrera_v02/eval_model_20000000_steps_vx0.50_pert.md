# Evaluacion de carrera: `runs/carrera_v02/checkpoints/model_20000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 04:04, commit ea5e992. vx_cmd = 0.5 m/s, perturbaciones si. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 2/4 | 0 | 2 | 10.5 ± 0.0 | 0.469 | 19.5 | 9.3 | 65 |
| no | 0.6 | 3/4 | 0 | 1 | 10.4 ± 0.1 | 0.473 | 17.4 | 8.7 | 65 |
| no | 0.8 | 3/4 | 0 | 1 | 10.3 ± 0.1 | 0.474 | 17.3 | 7.5 | 64 |
| no | 1.0 | 3/4 | 0 | 1 | 10.4 ± 0.1 | 0.473 | 16.9 | 6.2 | 63 |
| no | 1.2 | 3/4 | 0 | 1 | 10.4 ± 0.1 | 0.471 | 15.9 | 5.3 | 62 |
| si | 0.4 | 3/4 | 0 | 1 | 10.1 ± 0.1 | 0.484 | 16.9 | 8.1 | 64 |
| si | 0.6 | 3/4 | 0 | 1 | 10.0 ± 0.1 | 0.489 | 15.5 | 7.8 | 63 |
| si | 0.8 | 3/4 | 0 | 1 | 10.0 ± 0.1 | 0.486 | 14.2 | 6.9 | 63 |
| si | 1.0 | 3/4 | 0 | 1 | 10.0 ± 0.1 | 0.486 | 13.6 | 5.7 | 62 |
| si | 1.2 | 3/4 | 0 | 1 | 10.0 ± 0.1 | 0.484 | 13.5 | 4.9 | 62 |

**Total:** 29/40 metas, 0 caidas, 11 salidas.
Tiempo a meta medio 10.20 s (mejor 9.94 s).
