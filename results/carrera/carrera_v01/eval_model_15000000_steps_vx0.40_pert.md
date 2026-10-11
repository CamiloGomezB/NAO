# Evaluacion de carrera: `runs/carrera_v01/checkpoints/model_15000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 01:59, commit ea5e992. vx_cmd = 0.4 m/s, perturbaciones si. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| si | 0.4 | 4/4 | 0 | 0 | 13.7 ± 0.8 | 0.366 | 12.2 | 8.4 | 69 |
| si | 0.6 | 4/4 | 0 | 0 | 13.6 ± 0.7 | 0.369 | 11.4 | 6.4 | 68 |
| si | 0.8 | 4/4 | 0 | 0 | 13.5 ± 0.6 | 0.370 | 11.3 | 5.5 | 67 |
| si | 1.0 | 4/4 | 0 | 0 | 13.6 ± 0.7 | 0.369 | 11.0 | 6.9 | 68 |
| si | 1.2 | 4/4 | 0 | 0 | 13.6 ± 0.7 | 0.368 | 10.9 | 6.7 | 66 |

**Total:** 20/20 metas, 0 caidas, 0 salidas.
Tiempo a meta medio 13.57 s (mejor 12.99 s).
