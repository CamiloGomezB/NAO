# Evaluacion de carrera: `runs/carrera_v01/checkpoints/model_5000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 00:59, commit ea5e992. vx_cmd = 0.5 m/s, perturbaciones si. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| si | 0.4 | 3/4 | 1 | 0 | 10.3 ± 0.2 | 0.462 | 15.2 | 5.6 | 73 |
| si | 0.6 | 3/4 | 1 | 0 | 9.9 ± 0.2 | 0.480 | 15.7 | 4.9 | 70 |
| si | 0.8 | 4/4 | 0 | 0 | 10.1 ± 0.5 | 0.495 | 14.3 | 7.1 | 67 |
| si | 1.0 | 3/4 | 1 | 0 | 9.7 ± 0.1 | 0.491 | 13.4 | 4.6 | 68 |
| si | 1.2 | 3/4 | 1 | 0 | 9.6 ± 0.1 | 0.493 | 13.1 | 5.8 | 67 |

**Total:** 16/20 metas, 4 caidas, 0 salidas.
Tiempo a meta medio 9.94 s (mejor 9.53 s).
