# Evaluacion de carrera: `runs/carrera_v02/checkpoints/model_15000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 03:36, commit ea5e992. vx_cmd = 0.5 m/s, perturbaciones si. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 2/4 | 0 | 2 | 11.4 ± 0.1 | 0.446 | 20.0 | 7.4 | 62 |
| no | 0.6 | 2/4 | 0 | 2 | 11.4 ± 0.1 | 0.446 | 21.8 | 6.5 | 60 |
| no | 0.8 | 2/4 | 0 | 2 | 11.4 ± 0.1 | 0.444 | 21.0 | 6.2 | 60 |
| no | 1.0 | 2/4 | 0 | 2 | 11.5 ± 0.2 | 0.444 | 20.1 | 5.8 | 60 |
| no | 1.2 | 2/4 | 0 | 2 | 11.4 ± 0.1 | 0.444 | 19.8 | 5.4 | 60 |
| si | 0.4 | 4/4 | 0 | 0 | 10.8 ± 0.3 | 0.461 | 15.3 | 6.3 | 60 |
| si | 0.6 | 4/4 | 0 | 0 | 10.8 ± 0.2 | 0.459 | 15.2 | 5.3 | 59 |
| si | 0.8 | 4/4 | 0 | 0 | 10.8 ± 0.2 | 0.458 | 14.6 | 5.2 | 58 |
| si | 1.0 | 4/4 | 0 | 0 | 10.9 ± 0.2 | 0.458 | 14.9 | 5.4 | 57 |
| si | 1.2 | 4/4 | 0 | 0 | 10.9 ± 0.2 | 0.457 | 15.0 | 5.5 | 57 |

**Total:** 30/40 metas, 0 caidas, 10 salidas.
Tiempo a meta medio 11.04 s (mejor 10.52 s).
