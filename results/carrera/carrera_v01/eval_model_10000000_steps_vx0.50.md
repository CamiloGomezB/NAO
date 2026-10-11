# Evaluacion de carrera: `runs/carrera_v01/checkpoints/model_10000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 01:28, commit ea5e992. vx_cmd = 0.5 m/s, perturbaciones no. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 0/2 | 0 | 2 | — | 0.155 | 25.3 | 19.3 | 242 |
| no | 0.6 | 0/2 | 0 | 2 | — | 0.302 | 23.9 | 14.9 | 117 |
| no | 0.8 | 0/2 | 0 | 2 | — | 0.319 | 27.0 | 13.9 | 116 |
| no | 1.0 | 0/2 | 0 | 2 | — | 0.289 | 25.7 | 14.0 | 126 |
| no | 1.2 | 0/2 | 0 | 2 | — | 0.336 | 25.6 | 14.0 | 96 |
| si | 0.4 | 1/2 | 0 | 1 | 10.3 ± 0.0 | 0.481 | 20.8 | 6.8 | 62 |
| si | 0.6 | 2/2 | 0 | 0 | 10.1 ± 0.1 | 0.494 | 18.1 | 4.6 | 59 |
| si | 0.8 | 2/2 | 0 | 0 | 10.1 ± 0.1 | 0.496 | 18.0 | 4.2 | 59 |
| si | 1.0 | 2/2 | 0 | 0 | 10.0 ± 0.0 | 0.500 | 17.2 | 4.2 | 58 |
| si | 1.2 | 2/2 | 0 | 0 | 10.0 ± 0.0 | 0.498 | 16.8 | 3.6 | 58 |

**Total:** 9/20 metas, 0 caidas, 11 salidas.
Tiempo a meta medio 10.07 s (mejor 9.96 s).
