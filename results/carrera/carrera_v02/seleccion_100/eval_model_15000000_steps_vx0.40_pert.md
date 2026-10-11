# Evaluacion de carrera: `runs/carrera_v02/checkpoints/model_15000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 04:36, commit ea5e992. vx_cmd = 0.4 m/s, perturbaciones si. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 17/20 | 0 | 3 | 13.6 ± 0.5 | 0.367 | 16.4 | 5.5 | 70 |
| no | 0.6 | 19/20 | 0 | 1 | 13.8 ± 0.5 | 0.363 | 16.3 | 5.4 | 69 |
| no | 0.8 | 18/20 | 0 | 2 | 13.8 ± 0.5 | 0.361 | 15.8 | 4.9 | 69 |
| no | 1.0 | 17/20 | 0 | 3 | 13.9 ± 0.5 | 0.359 | 15.9 | 4.8 | 69 |
| no | 1.2 | 18/20 | 0 | 2 | 13.9 ± 0.5 | 0.359 | 15.6 | 4.7 | 68 |
| si | 0.4 | 20/20 | 0 | 0 | 12.9 ± 0.5 | 0.386 | 10.3 | 4.7 | 64 |
| si | 0.6 | 20/20 | 0 | 0 | 13.0 ± 0.5 | 0.383 | 10.1 | 4.2 | 64 |
| si | 0.8 | 20/20 | 0 | 0 | 13.1 ± 0.5 | 0.382 | 10.3 | 4.2 | 63 |
| si | 1.0 | 20/20 | 0 | 0 | 13.1 ± 0.5 | 0.381 | 10.4 | 4.1 | 63 |
| si | 1.2 | 20/20 | 0 | 0 | 13.1 ± 0.5 | 0.381 | 10.4 | 3.9 | 62 |

**Total:** 189/200 metas, 0 caidas, 11 salidas.
Tiempo a meta medio 13.39 s (mejor 11.93 s).
