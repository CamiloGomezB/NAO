# Evaluacion de carrera: `runs/carrera_v02/final_model.zip`

`scripts/eval_carrera.py`, 2026-10-11 05:55, commit ea5e992. vx_cmd = 0.4 m/s, perturbaciones si. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 3/4 | 0 | 1 | 12.1 ± 0.3 | 0.408 | 15.8 | 6.8 | 69 |
| no | 0.6 | 3/4 | 0 | 1 | 11.8 ± 0.3 | 0.414 | 16.1 | 6.6 | 68 |
| no | 0.8 | 3/4 | 0 | 1 | 11.8 ± 0.3 | 0.416 | 16.6 | 6.7 | 67 |
| no | 1.0 | 3/4 | 0 | 1 | 11.8 ± 0.3 | 0.416 | 17.6 | 6.7 | 66 |
| no | 1.2 | 3/4 | 0 | 1 | 11.9 ± 0.3 | 0.414 | 17.8 | 6.6 | 65 |
| si | 0.4 | 3/4 | 0 | 1 | 12.4 ± 0.1 | 0.402 | 12.5 | 5.0 | 69 |
| si | 0.6 | 3/4 | 1 | 0 | 12.3 ± 0.2 | 0.371 | 6.7 | 5.8 | 91 |
| si | 0.8 | 3/4 | 0 | 1 | 12.3 ± 0.2 | 0.407 | 12.4 | 5.3 | 69 |
| si | 1.0 | 3/4 | 0 | 1 | 12.1 ± 0.2 | 0.408 | 12.9 | 5.5 | 69 |
| si | 1.2 | 3/4 | 0 | 1 | 12.1 ± 0.2 | 0.408 | 13.5 | 6.0 | 69 |

**Total:** 30/40 metas, 1 caidas, 9 salidas.
Tiempo a meta medio 12.08 s (mejor 11.50 s).
