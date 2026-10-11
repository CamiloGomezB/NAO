# Evaluacion de carrera: `runs/carrera_v02/checkpoints/model_5000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 02:37, commit ea5e992. vx_cmd = 0.5 m/s, perturbaciones no. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 0/2 | 0 | 2 | — | 0.476 | 26.8 | 4.3 | 90 |
| no | 0.6 | 1/2 | 0 | 1 | 10.2 ± 0.0 | 0.494 | 18.6 | 4.4 | 80 |
| no | 0.8 | 2/2 | 0 | 0 | 10.1 ± 0.1 | 0.492 | 14.0 | 3.9 | 80 |
| no | 1.0 | 2/2 | 0 | 0 | 10.0 ± 0.0 | 0.498 | 13.0 | 3.1 | 80 |
| no | 1.2 | 2/2 | 0 | 0 | 10.0 ± 0.0 | 0.502 | 12.5 | 2.8 | 76 |
| si | 0.4 | 2/2 | 0 | 0 | 10.2 ± 0.0 | 0.489 | 5.1 | 4.0 | 69 |
| si | 0.6 | 2/2 | 0 | 0 | 10.2 ± 0.0 | 0.490 | 6.7 | 4.4 | 68 |
| si | 0.8 | 2/2 | 0 | 0 | 10.1 ± 0.1 | 0.495 | 6.3 | 4.8 | 67 |
| si | 1.0 | 2/2 | 0 | 0 | 10.1 ± 0.1 | 0.495 | 5.9 | 4.2 | 66 |
| si | 1.2 | 2/2 | 0 | 0 | 10.1 ± 0.1 | 0.495 | 6.6 | 3.7 | 65 |

**Total:** 17/20 metas, 0 caidas, 3 salidas.
Tiempo a meta medio 10.08 s (mejor 9.96 s).
