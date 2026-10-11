# Evaluacion de carrera: `runs/carrera_v02/checkpoints/model_5000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 02:38, commit ea5e992. vx_cmd = 0.4 m/s, perturbaciones si. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 2/4 | 0 | 2 | 12.2 ± 0.5 | 0.415 | 21.2 | 4.7 | 84 |
| no | 0.6 | 1/4 | 0 | 3 | 11.7 ± 0.0 | 0.418 | 20.6 | 4.5 | 80 |
| no | 0.8 | 1/4 | 0 | 3 | 11.7 ± 0.0 | 0.416 | 20.5 | 4.7 | 80 |
| no | 1.0 | 1/4 | 0 | 3 | 11.7 ± 0.0 | 0.415 | 20.6 | 4.0 | 80 |
| no | 1.2 | 1/4 | 0 | 3 | 11.7 ± 0.0 | 0.416 | 21.2 | 4.2 | 79 |
| si | 0.4 | 4/4 | 0 | 0 | 12.3 ± 0.4 | 0.405 | 15.8 | 5.1 | 70 |
| si | 0.6 | 4/4 | 0 | 0 | 12.2 ± 0.3 | 0.407 | 15.6 | 4.6 | 70 |
| si | 0.8 | 4/4 | 0 | 0 | 12.2 ± 0.3 | 0.408 | 14.6 | 4.6 | 69 |
| si | 1.0 | 4/4 | 0 | 0 | 12.2 ± 0.3 | 0.407 | 14.8 | 4.7 | 69 |
| si | 1.2 | 4/4 | 0 | 0 | 12.2 ± 0.3 | 0.405 | 14.8 | 4.6 | 69 |

**Total:** 26/40 metas, 0 caidas, 14 salidas.
Tiempo a meta medio 12.15 s (mejor 11.67 s).
