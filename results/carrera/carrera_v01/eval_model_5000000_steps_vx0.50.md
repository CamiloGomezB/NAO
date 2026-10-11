# Evaluacion de carrera: `runs/carrera_v01/checkpoints/model_5000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 00:58, commit ea5e992. vx_cmd = 0.5 m/s, perturbaciones no. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 0/2 | 2 | 0 | — | 0.151 | 7.6 | 7.8 | 176 |
| no | 0.6 | 0/2 | 2 | 0 | — | 0.152 | 6.5 | 18.2 | 170 |
| no | 0.8 | 0/2 | 2 | 0 | — | 0.125 | 13.0 | 14.1 | 200 |
| no | 1.0 | 0/2 | 2 | 0 | — | 0.080 | 9.0 | 17.9 | 319 |
| no | 1.2 | 0/2 | 2 | 0 | — | 0.092 | 6.7 | 11.9 | 251 |
| si | 0.4 | 2/2 | 0 | 0 | 10.0 ± 0.2 | 0.499 | 14.1 | 3.5 | 77 |
| si | 0.6 | 2/2 | 0 | 0 | 9.6 ± 0.1 | 0.518 | 13.3 | 2.7 | 72 |
| si | 0.8 | 2/2 | 0 | 0 | 9.5 ± 0.2 | 0.525 | 11.3 | 2.2 | 71 |
| si | 1.0 | 2/2 | 0 | 0 | 9.5 ± 0.2 | 0.527 | 10.7 | 2.3 | 70 |
| si | 1.2 | 2/2 | 0 | 0 | 9.4 ± 0.2 | 0.526 | 10.7 | 2.3 | 70 |

**Total:** 10/20 metas, 10 caidas, 0 salidas.
Tiempo a meta medio 9.58 s (mejor 9.24 s).
