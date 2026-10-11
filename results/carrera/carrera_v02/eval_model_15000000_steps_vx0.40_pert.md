# Evaluacion de carrera: `runs/carrera_v02/checkpoints/model_15000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 03:36, commit ea5e992. vx_cmd = 0.4 m/s, perturbaciones si. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 2/4 | 0 | 2 | 14.0 ± 0.0 | 0.365 | 22.8 | 6.5 | 66 |
| no | 0.6 | 3/4 | 0 | 1 | 13.8 ± 0.4 | 0.362 | 23.0 | 6.3 | 65 |
| no | 0.8 | 3/4 | 0 | 1 | 13.9 ± 0.4 | 0.360 | 22.4 | 5.5 | 65 |
| no | 1.0 | 3/4 | 0 | 1 | 13.9 ± 0.5 | 0.360 | 21.9 | 5.1 | 65 |
| no | 1.2 | 3/4 | 0 | 1 | 13.9 ± 0.5 | 0.359 | 21.5 | 5.1 | 64 |
| si | 0.4 | 4/4 | 0 | 0 | 13.0 ± 0.3 | 0.382 | 13.6 | 5.1 | 62 |
| si | 0.6 | 4/4 | 0 | 0 | 13.1 ± 0.4 | 0.380 | 12.9 | 4.5 | 62 |
| si | 0.8 | 4/4 | 0 | 0 | 13.2 ± 0.4 | 0.379 | 12.9 | 4.3 | 61 |
| si | 1.0 | 4/4 | 0 | 0 | 13.2 ± 0.4 | 0.379 | 12.9 | 4.3 | 60 |
| si | 1.2 | 4/4 | 0 | 0 | 13.2 ± 0.4 | 0.379 | 13.0 | 4.2 | 60 |

**Total:** 34/40 metas, 0 caidas, 6 salidas.
Tiempo a meta medio 13.44 s (mejor 12.53 s).
