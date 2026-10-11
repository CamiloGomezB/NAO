# Evaluacion de carrera: `runs/carrera_v02/checkpoints/model_25000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 04:32, commit ea5e992. vx_cmd = 0.5 m/s, perturbaciones no. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 2/2 | 0 | 0 | 10.2 ± 0.0 | 0.487 | 14.3 | 4.6 | 73 |
| no | 0.6 | 1/2 | 0 | 1 | 10.0 ± 0.0 | 0.493 | 17.9 | 5.6 | 73 |
| no | 0.8 | 1/2 | 0 | 1 | 10.0 ± 0.0 | 0.493 | 19.8 | 5.4 | 72 |
| no | 1.0 | 1/2 | 0 | 1 | 10.0 ± 0.0 | 0.495 | 19.5 | 5.5 | 71 |
| no | 1.2 | 1/2 | 0 | 1 | 10.0 ± 0.0 | 0.495 | 19.0 | 5.1 | 72 |
| si | 0.4 | 2/2 | 0 | 0 | 10.0 ± 0.0 | 0.494 | 8.2 | 4.3 | 73 |
| si | 0.6 | 2/2 | 0 | 0 | 10.0 ± 0.0 | 0.495 | 8.0 | 4.3 | 73 |
| si | 0.8 | 2/2 | 0 | 0 | 10.0 ± 0.0 | 0.498 | 7.4 | 4.2 | 73 |
| si | 1.0 | 2/2 | 0 | 0 | 10.0 ± 0.0 | 0.498 | 6.2 | 4.0 | 72 |
| si | 1.2 | 2/2 | 0 | 0 | 10.0 ± 0.0 | 0.495 | 6.2 | 3.7 | 72 |

**Total:** 16/20 metas, 0 caidas, 4 salidas.
Tiempo a meta medio 10.03 s (mejor 9.96 s).
