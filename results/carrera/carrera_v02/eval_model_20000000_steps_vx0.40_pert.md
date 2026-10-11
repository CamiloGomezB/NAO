# Evaluacion de carrera: `runs/carrera_v02/checkpoints/model_20000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 04:05, commit ea5e992. vx_cmd = 0.4 m/s, perturbaciones si. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 3/4 | 0 | 1 | 12.6 ± 0.1 | 0.390 | 19.5 | 8.8 | 67 |
| no | 0.6 | 3/4 | 0 | 1 | 12.7 ± 0.0 | 0.387 | 18.4 | 7.6 | 68 |
| no | 0.8 | 4/4 | 0 | 0 | 13.0 ± 0.4 | 0.385 | 17.0 | 6.8 | 67 |
| no | 1.0 | 3/4 | 0 | 1 | 12.8 ± 0.1 | 0.384 | 17.0 | 6.4 | 66 |
| no | 1.2 | 3/4 | 0 | 1 | 12.7 ± 0.0 | 0.384 | 16.6 | 5.8 | 64 |
| si | 0.4 | 4/4 | 0 | 0 | 12.4 ± 0.6 | 0.401 | 16.7 | 6.7 | 68 |
| si | 0.6 | 4/4 | 0 | 0 | 12.5 ± 0.7 | 0.399 | 16.1 | 6.6 | 68 |
| si | 0.8 | 4/4 | 0 | 0 | 12.6 ± 0.7 | 0.398 | 15.5 | 6.5 | 68 |
| si | 1.0 | 4/4 | 0 | 0 | 12.6 ± 0.7 | 0.396 | 16.1 | 6.2 | 67 |
| si | 1.2 | 4/4 | 0 | 0 | 12.7 ± 0.8 | 0.394 | 16.1 | 5.6 | 66 |

**Total:** 36/40 metas, 0 caidas, 4 salidas.
Tiempo a meta medio 12.65 s (mejor 11.98 s).
