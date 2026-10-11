# Evaluacion de carrera: `runs/carrera_v01/checkpoints/model_5000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 01:29, commit ea5e992. vx_cmd = 0.4 m/s, perturbaciones si. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| si | 0.4 | 4/4 | 0 | 0 | 12.4 ± 0.1 | 0.401 | 15.4 | 4.3 | 74 |
| si | 0.6 | 4/4 | 0 | 0 | 12.4 ± 0.2 | 0.402 | 15.2 | 5.3 | 73 |
| si | 0.8 | 4/4 | 0 | 0 | 12.3 ± 0.3 | 0.405 | 15.2 | 5.3 | 71 |
| si | 1.0 | 4/4 | 0 | 0 | 12.3 ± 0.4 | 0.406 | 14.8 | 5.4 | 70 |
| si | 1.2 | 4/4 | 0 | 0 | 12.4 ± 0.5 | 0.404 | 14.8 | 6.9 | 70 |

**Total:** 20/20 metas, 0 caidas, 0 salidas.
Tiempo a meta medio 12.35 s (mejor 12.00 s).
