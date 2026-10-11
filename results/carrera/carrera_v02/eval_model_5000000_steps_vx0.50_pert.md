# Evaluacion de carrera: `runs/carrera_v02/checkpoints/model_5000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 02:38, commit ea5e992. vx_cmd = 0.5 m/s, perturbaciones si. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 2/4 | 0 | 2 | 10.6 ± 0.1 | 0.466 | 23.4 | 5.5 | 82 |
| no | 0.6 | 1/4 | 0 | 3 | 10.3 ± 0.0 | 0.476 | 23.0 | 5.0 | 79 |
| no | 0.8 | 2/4 | 0 | 2 | 10.1 ± 0.1 | 0.485 | 20.2 | 4.8 | 76 |
| no | 1.0 | 2/4 | 0 | 2 | 10.1 ± 0.1 | 0.487 | 19.6 | 4.5 | 75 |
| no | 1.2 | 2/4 | 0 | 2 | 10.1 ± 0.1 | 0.487 | 19.2 | 4.3 | 74 |
| si | 0.4 | 4/4 | 0 | 0 | 10.4 ± 0.4 | 0.480 | 13.1 | 5.6 | 67 |
| si | 0.6 | 4/4 | 0 | 0 | 10.3 ± 0.3 | 0.484 | 14.0 | 5.0 | 66 |
| si | 0.8 | 4/4 | 0 | 0 | 10.2 ± 0.2 | 0.488 | 14.3 | 5.1 | 65 |
| si | 1.0 | 4/4 | 0 | 0 | 10.2 ± 0.2 | 0.488 | 13.6 | 5.0 | 64 |
| si | 1.2 | 4/4 | 0 | 0 | 10.2 ± 0.2 | 0.488 | 12.7 | 4.9 | 63 |

**Total:** 29/40 metas, 0 caidas, 11 salidas.
Tiempo a meta medio 10.24 s (mejor 9.94 s).
