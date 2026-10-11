# Evaluacion de carrera: `policies/carrera_v01/model.zip`

`scripts/eval_carrera.py`, 2026-10-11 02:11, commit ea5e992. vx_cmd = 0.4 m/s, perturbaciones si. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 0/20 | 11 | 8 | — | 0.026 | 15.0 | 19.2 | 906 |
| no | 0.6 | 0/20 | 9 | 11 | — | 0.033 | 16.7 | 19.2 | 1254 |
| no | 0.8 | 0/20 | 10 | 8 | — | 0.040 | 15.5 | 16.9 | 888 |
| no | 1.0 | 0/20 | 7 | 11 | — | 0.045 | 17.3 | 16.9 | 650 |
| no | 1.2 | 0/20 | 8 | 9 | — | 0.041 | 16.8 | 16.5 | 727 |
| si | 0.4 | 20/20 | 0 | 0 | 13.2 ± 0.7 | 0.378 | 7.8 | 6.1 | 70 |
| si | 0.6 | 20/20 | 0 | 0 | 13.2 ± 0.7 | 0.378 | 8.3 | 6.0 | 70 |
| si | 0.8 | 20/20 | 0 | 0 | 13.2 ± 0.7 | 0.378 | 8.6 | 5.7 | 69 |
| si | 1.0 | 20/20 | 0 | 0 | 13.2 ± 0.7 | 0.377 | 8.3 | 6.1 | 69 |
| si | 1.2 | 20/20 | 0 | 0 | 13.3 ± 0.7 | 0.377 | 8.1 | 5.9 | 68 |

**Total:** 100/200 metas, 45 caidas, 47 salidas.
Tiempo a meta medio 13.23 s (mejor 11.98 s).
