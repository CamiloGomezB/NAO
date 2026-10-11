# Evaluacion de carrera: `runs/carrera_v01/checkpoints/model_10000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 01:28, commit ea5e992. vx_cmd = 0.5 m/s, perturbaciones si. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| si | 0.4 | 2/4 | 0 | 2 | 10.7 ± 0.0 | 0.463 | 17.1 | 7.2 | 60 |
| si | 0.6 | 2/4 | 0 | 2 | 10.6 ± 0.1 | 0.465 | 17.9 | 6.6 | 59 |
| si | 0.8 | 2/4 | 0 | 2 | 10.5 ± 0.0 | 0.472 | 18.0 | 6.9 | 58 |
| si | 1.0 | 2/4 | 0 | 2 | 10.5 ± 0.0 | 0.472 | 18.5 | 7.1 | 58 |
| si | 1.2 | 1/4 | 1 | 2 | 10.5 ± 0.0 | 0.470 | 18.3 | 9.5 | 58 |

**Total:** 9/20 metas, 1 caidas, 10 salidas.
Tiempo a meta medio 10.56 s (mejor 10.44 s).
