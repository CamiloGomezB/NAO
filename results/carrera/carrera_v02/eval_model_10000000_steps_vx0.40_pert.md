# Evaluacion de carrera: `runs/carrera_v02/checkpoints/model_10000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 03:08, commit ea5e992. vx_cmd = 0.4 m/s, perturbaciones si. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 1/4 | 0 | 3 | 12.2 ± 0.0 | 0.407 | 23.8 | 6.5 | 68 |
| no | 0.6 | 1/4 | 0 | 3 | 12.2 ± 0.0 | 0.404 | 24.8 | 5.8 | 68 |
| no | 0.8 | 1/4 | 0 | 3 | 12.2 ± 0.0 | 0.404 | 24.9 | 5.8 | 67 |
| no | 1.0 | 1/4 | 0 | 3 | 12.2 ± 0.0 | 0.404 | 24.5 | 5.5 | 67 |
| no | 1.2 | 1/4 | 0 | 3 | 12.2 ± 0.0 | 0.404 | 24.0 | 5.3 | 66 |
| si | 0.4 | 4/4 | 0 | 0 | 12.5 ± 0.4 | 0.400 | 14.9 | 5.7 | 66 |
| si | 0.6 | 4/4 | 0 | 0 | 12.5 ± 0.4 | 0.398 | 14.7 | 5.6 | 66 |
| si | 0.8 | 4/4 | 0 | 0 | 12.5 ± 0.4 | 0.398 | 14.6 | 5.1 | 66 |
| si | 1.0 | 4/4 | 0 | 0 | 12.5 ± 0.3 | 0.398 | 14.0 | 4.9 | 66 |
| si | 1.2 | 4/4 | 0 | 0 | 12.5 ± 0.4 | 0.398 | 13.9 | 4.7 | 66 |

**Total:** 25/40 metas, 0 caidas, 15 salidas.
Tiempo a meta medio 12.47 s (mejor 11.98 s).
