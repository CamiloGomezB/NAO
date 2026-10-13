# Evaluacion de carrera: `policies/carrera_v03/model.zip`

`scripts/eval_carrera.py`, 2026-10-12 21:40, commit fe45c71. vx_cmd = 0.45 m/s, perturbaciones no, rumbo objetivo de la IMU 'carril'. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| si | 0.4 | 5/5 | 0 | 0 | 11.2 ± 0.0 | 0.447 | 3.1 | 4.8 | 68 |
| si | 0.6 | 5/5 | 0 | 0 | 11.2 ± 0.0 | 0.445 | 4.2 | 6.3 | 68 |
| si | 0.8 | 5/5 | 0 | 0 | 11.2 ± 0.0 | 0.446 | 4.9 | 8.7 | 67 |
| si | 1.0 | 5/5 | 0 | 0 | 11.2 ± 0.0 | 0.447 | 5.4 | 9.8 | 67 |
| si | 1.2 | 5/5 | 0 | 0 | 11.2 ± 0.0 | 0.444 | 6.9 | 10.3 | 67 |

**Total:** 25/25 metas, 0 caidas, 0 salidas.
Tiempo a meta medio 11.19 s (mejor 11.16 s).
