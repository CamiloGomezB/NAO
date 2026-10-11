# Evaluacion de carrera: `runs/carrera_v01/checkpoints/model_15000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 01:58, commit ea5e992. vx_cmd = 0.5 m/s, perturbaciones no. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 0/2 | 1 | 1 | — | 0.048 | 15.8 | 14.7 | 579 |
| no | 0.6 | 0/2 | 2 | 0 | — | 0.040 | 5.3 | 16.7 | 622 |
| no | 0.8 | 0/2 | 1 | 1 | — | 0.079 | 16.3 | 16.2 | 401 |
| no | 1.0 | 0/2 | 2 | 0 | — | 0.029 | 7.5 | 18.0 | 1429 |
| no | 1.2 | 0/2 | 0 | 2 | — | 0.112 | 26.7 | 13.4 | 206 |
| si | 0.4 | 2/2 | 0 | 0 | 10.5 ± 0.0 | 0.475 | 3.4 | 3.5 | 66 |
| si | 0.6 | 2/2 | 0 | 0 | 10.6 ± 0.1 | 0.471 | 4.4 | 3.0 | 67 |
| si | 0.8 | 2/2 | 0 | 0 | 10.6 ± 0.1 | 0.470 | 4.8 | 3.0 | 67 |
| si | 1.0 | 2/2 | 0 | 0 | 10.6 ± 0.1 | 0.472 | 5.3 | 2.9 | 66 |
| si | 1.2 | 2/2 | 0 | 0 | 10.6 ± 0.1 | 0.472 | 5.6 | 2.9 | 66 |

**Total:** 10/20 metas, 6 caidas, 4 salidas.
Tiempo a meta medio 10.57 s (mejor 10.47 s).
