# Evaluacion de carrera: `runs/carrera_v03/checkpoints/model_5000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 14:25, commit d9733e5. vx_cmd = 0.4 m/s, perturbaciones si, rumbo objetivo de la IMU 'carril'. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 17/20 | 0 | 3 | 12.5 ± 0.4 | 0.397 | 14.2 | 5.0 | 74 |
| no | 0.6 | 17/20 | 0 | 3 | 12.6 ± 0.4 | 0.394 | 14.1 | 5.2 | 74 |
| no | 0.8 | 16/20 | 0 | 4 | 12.6 ± 0.3 | 0.393 | 14.7 | 5.0 | 74 |
| no | 1.0 | 16/20 | 0 | 4 | 12.6 ± 0.4 | 0.393 | 14.6 | 4.8 | 74 |
| no | 1.2 | 16/20 | 0 | 4 | 12.6 ± 0.4 | 0.392 | 14.3 | 4.6 | 74 |
| si | 0.4 | 20/20 | 0 | 0 | 12.8 ± 0.4 | 0.390 | 6.6 | 4.2 | 73 |
| si | 0.6 | 20/20 | 0 | 0 | 12.8 ± 0.5 | 0.389 | 7.3 | 5.7 | 73 |
| si | 0.8 | 20/20 | 0 | 0 | 12.8 ± 0.4 | 0.389 | 7.7 | 7.2 | 72 |
| si | 1.0 | 20/20 | 0 | 0 | 12.8 ± 0.4 | 0.390 | 7.6 | 7.9 | 72 |
| si | 1.2 | 20/20 | 0 | 0 | 12.8 ± 0.4 | 0.388 | 7.6 | 8.0 | 72 |

**Total:** 182/200 metas, 0 caidas, 18 salidas.
Tiempo a meta medio 12.70 s (mejor 11.74 s).
