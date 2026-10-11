# Evaluacion de carrera: `runs/carrera_v02/checkpoints/model_25000000_steps.zip`

`scripts/eval_carrera.py`, 2026-10-11 04:33, commit ea5e992. vx_cmd = 0.4 m/s, perturbaciones si. Colocacion y meta como `demo/caminatas/benchmark.py`.

| Vision | mu | Metas | Caidas | Salidas | Tiempo a meta [s] | Vel. media [m/s] | Desvio max [cm] | Rumbo max [deg] | Esfuerzo |
|---|---|---|---|---|---|---|---|---|---|
| no | 0.4 | 3/4 | 0 | 1 | 12.3 ± 0.1 | 0.397 | 15.5 | 4.9 | 76 |
| no | 0.6 | 3/4 | 0 | 1 | 12.2 ± 0.1 | 0.401 | 14.9 | 4.6 | 75 |
| no | 0.8 | 3/4 | 0 | 1 | 12.2 ± 0.0 | 0.399 | 15.0 | 4.3 | 76 |
| no | 1.0 | 3/4 | 0 | 1 | 12.2 ± 0.1 | 0.401 | 14.4 | 4.5 | 75 |
| no | 1.2 | 3/4 | 0 | 1 | 12.2 ± 0.0 | 0.399 | 15.6 | 4.5 | 75 |
| si | 0.4 | 3/4 | 0 | 1 | 12.3 ± 0.2 | 0.395 | 14.2 | 6.5 | 79 |
| si | 0.6 | 3/4 | 0 | 1 | 12.2 ± 0.2 | 0.399 | 14.0 | 5.4 | 78 |
| si | 0.8 | 3/4 | 0 | 1 | 12.2 ± 0.2 | 0.400 | 14.0 | 5.3 | 77 |
| si | 1.0 | 3/4 | 0 | 1 | 12.2 ± 0.2 | 0.398 | 13.9 | 5.1 | 77 |
| si | 1.2 | 3/4 | 0 | 1 | 12.3 ± 0.2 | 0.397 | 13.4 | 5.0 | 77 |

**Total:** 30/40 metas, 0 caidas, 10 salidas.
Tiempo a meta medio 12.23 s (mejor 11.91 s).
