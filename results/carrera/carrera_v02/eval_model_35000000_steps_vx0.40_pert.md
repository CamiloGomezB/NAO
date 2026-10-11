# Evaluacion de carrera: `runs/carrera_v02/checkpoints/model_35000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 05:27, commit ea5e992. vx_cmd = 0.4 m/s, perturbaciones si. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 3/4 | 0 | 1 | 12.9 ± 0.3 | 0.382 | 16.1 | 5.5 | 66 |
| no | 0.6 | 3/4 | 0 | 1 | 12.8 ± 0.4 | 0.385 | 15.4 | 5.4 | 66 |
| no | 0.8 | 3/4 | 0 | 1 | 12.8 ± 0.4 | 0.387 | 16.6 | 5.2 | 65 |
| no | 1.0 | 3/4 | 0 | 1 | 12.7 ± 0.4 | 0.387 | 16.3 | 5.0 | 65 |
| no | 1.2 | 3/4 | 0 | 1 | 12.7 ± 0.4 | 0.388 | 16.8 | 4.7 | 64 |
| si | 0.4 | 3/4 | 0 | 1 | 12.7 ± 0.6 | 0.387 | 14.0 | 5.3 | 64 |
| si | 0.6 | 3/4 | 0 | 1 | 12.6 ± 0.5 | 0.392 | 13.5 | 6.1 | 63 |
| si | 0.8 | 3/4 | 0 | 1 | 12.6 ± 0.5 | 0.393 | 14.5 | 5.8 | 63 |
| si | 1.0 | 3/4 | 0 | 1 | 12.5 ± 0.5 | 0.395 | 14.5 | 5.7 | 62 |
| si | 1.2 | 3/4 | 0 | 1 | 12.6 ± 0.5 | 0.394 | 15.1 | 6.0 | 61 |

**Total:** 30/40 metas, 0 caidas, 10 salidas.
Tiempo a meta medio 12.68 s (mejor 11.91 s).
